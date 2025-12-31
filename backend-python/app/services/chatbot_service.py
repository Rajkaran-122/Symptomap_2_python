"""
AI Doctor Chatbot Service
Implements complete medical conversation flowchart with GPT-4
"""

import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import openai

from app.core.config import settings
from app.models.chatbot import ChatbotConversation, AnonymousSymptomReport, DiseaseInfo
from app.core.redis import redis_client


class ChatbotService:
    """
    AI Doctor chatbot service implementing the complete medical conversation flow
    """
    
    CONVERSATION_STATES = {
        "GREETING": "greeting",
        "BASIC_INFO": "basic_info",
        "SYMPTOM_COLLECTION": "symptom_collection",
        "SYMPTOM_CLARIFICATION": "symptom_clarification",
        "HISTORY_COLLECTION": "history_collection",
        "ASSESSMENT": "assessment",
        "COMPLETED": "completed"
    }
    
    # Emergency red flag symptoms
    RED_FLAG_SYMPTOMS = [
        "chest pain", "difficulty breathing", "severe bleeding", "unconscious",
        "stroke symptoms", "severe head injury", "seizure", "severe allergic reaction",
        "severe abdominal pain", "can't breathe", "heart attack", "choking"
    ]
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    
    async def start_conversation(
        self,
        session_id: str,
        user_info: Optional[Dict] = None,
        location: Optional[Dict] = None
    ) -> Dict:
        """
        Start a new chatbot conversation
        
        Args:
            session_id: Unique session identifier
            user_info: Optional user info (age, gender, etc.)
            location: Optional location (city, country, lat, lng)
        
        Returns:
            Dict with greeting message and optional health alerts
        """
        
        # Create conversation in database
        conversation = ChatbotConversation(
            session_id=session_id,
            conversation_state=self.CONVERSATION_STATES["GREETING"],
            user_info=user_info or {},
            city=location.get("city") if location else None,
            country=location.get("country") if location else None,
            conversation_data=[]
        )
        
        self.db.add(conversation)
        await self.db.commit()
        
        # Generate greeting message
        greeting = (
            "Hello! I'm your AI health assistant. I'm here to help you understand your symptoms "
            "and guide you on the best course of action.\n\n"
            "⚠️ **Important Disclaimer**: I provide general health information only and am not a substitute "
            "for professional medical advice. If you think you have a medical emergency, please call emergency "
            "services immediately.\n\n"
            "To get started, could you please describe your main symptoms?"
        )
        
        # Check for local outbreaks and add warning
        local_alert = None
        if location and location.get("city"):
            local_alert = await self._check_local_outbreaks(location.get("city"), location.get("country"))
        
        return {
            "session_id": session_id,
            "message": greeting,
            "conversation_state": self.CONVERSATION_STATES["GREETING"],
            "local_health_alert": local_alert
        }
    
    
    async def process_message(
        self,
        session_id: str,
        message: str,
        image_url: Optional[str] = None
    ) -> Dict:
        """
        Process user message and generate AI response
        
        Args:
            session_id: Conversation session ID
            message: User's message
            image_url: Optional image URL
        
        Returns:
            Dict with bot response and updated state
        """
        
        # Get conversation from database
        result = await self.db.execute(
            select(ChatbotConversation).where(ChatbotConversation.session_id == session_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise ValueError("Conversation not found")
        
        # Check for emergency symptoms first
        emergency_detected = self._detect_emergency(message)
        if emergency_detected:
            response = {
                "type": "emergency",
                "content": (
                    "⚠️ **EMERGENCY**: Your symptoms may require immediate medical attention. "
                    "Please call emergency services (911 or your local emergency number) immediately "
                    "or go to the nearest emergency room.\n\n"
                    "Do not delay seeking medical care."
                ),
                "severity": "emergency"
            }
            
            # Save to conversation
            await self._save_message(conversation, "user", message)
            await self._save_message(conversation, "assistant", response["content"])
            
            return {
                "session_id": session_id,
                "bot_messages": [response],
                "conversation_state": conversation.conversation_state
            }
        
        # Load conversation history from Redis (for context)
        history = await self._get_conversation_history(session_id)
        
        # Generate AI response based on current state
        bot_response = await self._generate_ai_response(
            conversation,
            message,
            history,
            image_url
        )
        
       # Save messages
        await self._save_message(conversation, "user", message)
        await self._save_message(conversation, "assistant", bot_response.get("content", ""))
        
        # Update conversation state
        await self._update_conversation_state(conversation, bot_response)
        
        await self.db.commit()
        
        return {
            "session_id": session_id,
            "bot_messages": [bot_response],
            "conversation_state": conversation.conversation_state,
            "completion_percentage": self._calculate_completion(conversation)
        }
    
    
    async def end_conversation(self, session_id: str) -> Dict:
        """
        End conversation and generate final assessment
        
        Args:
            session_id: Conversation session ID
        
        Returns:
            Dict with assessment, SOAP note, and recommendations
        """
        
        result = await self.db.execute(
            select(ChatbotConversation).where(ChatbotConversation.session_id == session_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise ValueError("Conversation not found")
        
        # Generate final assessment
        assessment = await self._generate_assessment(conversation)
        
        # Generate SOAP note
        soap_note = await self._generate_soap_note(conversation)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(conversation, assessment)
        
        # Update conversation
        conversation.conversation_state = self.CONVERSATION_STATES["COMPLETED"]
        conversation.ended_at = datetime.now(timezone.utc)
        conversation.soap_note = soap_note
        conversation.severity_assessment = assessment.get("severity")
        conversation.suspected_conditions = assessment.get("differential_diagnoses", [])
        conversation.recommendations = json.dumps(recommendations)
        
        await self.db.commit()
        
        # Create anonymous symptom report for surveillance
        await self._create_anonymous_report(conversation, assessment)
        
        return {
            "session_id": session_id,
            "ended_at": conversation.ended_at.isoformat(),
            "assessment": assessment,
            "soap_note": soap_note,
            "recommendations": recommendations,
            "export_available": True
        }
    
    
    def _detect_emergency(self, message: str) -> bool:
        """Detect emergency symptoms in message"""
        message_lower = message.lower()
        return any(symptom in message_lower for symptom in self.RED_FLAG_SYMPTOMS)
    
    
    async def _generate_ai_response(
        self,
        conversation: ChatbotConversation,
        message: str,
        history: List[Dict],
        image_url: Optional[str] = None
    ) -> Dict:
        """Generate AI response using GPT-4"""
        
        # Build system prompt based on conversation state
        system_prompt = self._build_system_prompt(conversation.conversation_state)
        
        # Build messages for GPT-4
        messages = [
            {"role": "system", "content": system_prompt},
            *history,
            {"role": "user", "content": message}
        ]
        
        # Add image if provided
        if image_url:
            messages[-1]["content"] = [
                {"type": "text", "text": message},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        
        # Call GPT-4
        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",  # or gpt-4-turbo-preview
            messages=messages,
            temperature=0.3,
            max_tokens=800
        )
        
        content = response.choices[0].message.content
        
        return {
            "type": "text",
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    
    def _build_system_prompt(self, conversation_state: str) -> str:
        """Build system prompt based on conversation state"""
        
        base_prompt = """You are a highly-trained, empathetic, and medically cautious AI health assistant.

CRITICAL SAFETY RULES:
1. You are NOT a doctor and cannot provide diagnoses
2. Always recommend consulting a healthcare professional
3. For emergencies, immediately tell user to call emergency services
4. Be empathetic but medically conservative

Your role is to:
- Collect symptom information systematically
- Ask clarifying questions
- Assess severity (emergency/urgent/routine)
- Provide general health guidance
- Recommend when to see a doctor

"""
        
        state_prompts = {
            "greeting": "The user just started the conversation. Welcome them and ask them to describe their main symptoms.",
            
            "symptom_collection": """The user has started describing symptoms. Your task:
1. Ask 3-5 clarifying questions about the symptoms:
   - When did they start?
   - How severe (1-10 scale)?
   - Location/characteristics?
   - What makes them better/worse?
   - Any associated symptoms?
2. Format questions clearly and numbered
3. Be conversational and empathetic""",
            
            "history_collection": """Now collect medical history. Ask 5 questions at a time about:
- Chronic conditions (diabetes, hypertension, etc.)
- Current medications
- Allergies
- Recent travel
- Family history (if relevant)
Format as numbered questions.""",
            
            "assessment": """You have collected enough information. Now provide:
1. A brief summary of what you understood
2. Your assessment of severity (emergency/urgent/routine)
3. Next steps recommendation
Be clear and direct."""
        }
        
        return base_prompt + state_prompts.get(conversation_state, "")
    
    
    async def _generate_assessment(self, conversation: ChatbotConversation) -> Dict:
        """Generate final medical assessment"""
        
        # Extract all symptoms and responses from conversation
        conversation_text = self._extract_conversation_text(conversation)
        
        assessment_prompt = f"""Based on this medical conversation, provide a structured assessment:

Conversation:
{conversation_text}

Provide your assessment in JSON format with:
{{
    "severity": "emergency|urgent|routine",
    "primary_diagnosis": {{"condition": "...", "confidence": 0.0-1.0}},
    "differential_diagnoses": [{{"condition": "...", "confidence": 0.0-1.0, "reason": "..."}}],
    "red_flags_detected": [],
    "recommendation": {{"action": "...", "urgency": "...", "follow_up_days": ...}}
}}"""
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a medical AI assistant. Provide structured assessments in JSON format."},
                {"role": "user", "content": assessment_prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    
    async def _generate_soap_note(self, conversation: ChatbotConversation) -> Dict:
        """Generate SOAP note"""
        
        conversation_text = self._extract_conversation_text(conversation)
        
        soap_prompt = f"""Generate a SOAP note from this conversation:

{conversation_text}

Format as JSON:
{{
    "subjective": "Patient-reported symptoms and history...",
    "objective": "Measurable data if available...",
    "assessment": "Clinical impression and differential diagnoses...",
    "plan": "Recommendations and follow-up..."
}}"""
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": soap_prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    
    async def _generate_recommendations(
        self,
        conversation: ChatbotConversation,
        assessment: Dict
    ) -> Dict:
        """Generate home care recommendations"""
        
        severity = assessment.get("severity", "routine")
        
        if severity == "emergency":
            return {
                "action": "emergency",
                "message": "Go to emergency room immediately or call emergency services"
            }
        
        # Generate detailed recommendations based on symptoms
        symptoms_text = json.dumps(conversation.primary_symptoms)
        
        rec_prompt = f"""Based on these symptoms and {severity} severity, provide home care recommendations.

Symptoms: {symptoms_text}

Provide JSON with:
{{
    "home_care": ["rest", "hydrate", ...],
    "medications": {{"over_the_counter": [...], "avoid": [...]}},
    "when_to_see_doctor": {{"urgent": [...], "routine": [...]}},
    "follow_up": {{"recommended_days": 3, "message": "..."}}
}}"""
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": rec_prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    
    async def _check_local_outbreaks(
        self,
        city: Optional[str],
        country: Optional[str]
    ) -> Optional[Dict]:
        """Check for disease outbreaks in user's location"""
        
        if not city:
            return None
        
        # Query recent symptom reports in the area
        # (This would query the outbreak/symptom report tables)
        # For now, return None - implement based on your outbreak detection logic
        
        return None
    
    
    async def _save_message(
        self,
        conversation: ChatbotConversation,
        role: str,
        content: str
    ):
        """Save message to conversation history"""
        
        if conversation.conversation_data is None:
            conversation.conversation_data = []
        
        conversation.conversation_data.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Also save to Redis for quick access
        redis_key = f"chat:{conversation.session_id}"
        await redis_client.set(
            redis_key,
            json.dumps(conversation.conversation_data),
            ex=86400  # 24 hours
        )
    
    
    async def _get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history from Redis"""
        
        redis_key = f"chat:{session_id}"
        history_json = await redis_client.get(redis_key)
        
        if history_json:
            return json.loads(history_json)
        
        return []
    
    
    async def _update_conversation_state(
        self,
        conversation: ChatbotConversation,
        bot_response: Dict
    ):
        """Update conversation state based on progress"""
        
        # Simple state progression logic
        current_state = conversation.conversation_state
        message_count = len(conversation.conversation_data or [])
        
        if current_state == "greeting" and message_count >= 4:
            conversation.conversation_state = "symptom_collection"
        elif current_state == "symptom_collection" and message_count >= 10:
            conversation.conversation_state = "history_collection"
        elif current_state == "history_collection" and message_count >= 16:
            conversation.conversation_state = "assessment"
    
    
    def _calculate_completion(self, conversation: ChatbotConversation) -> int:
        """Calculate completion percentage"""
        
        state_percentages = {
            "greeting": 10,
            "symptom_collection": 40,
            "history_collection": 70,
            "assessment": 90,
            "completed": 100
        }
        
        return state_percentages.get(conversation.conversation_state, 0)
    
    
    def _extract_conversation_text(self, conversation: ChatbotConversation) -> str:
        """Extract conversation as text"""
        
        if not conversation.conversation_data:
            return ""
        
        lines = []
        for msg in conversation.conversation_data:
            role = "User" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content']}")
        
        return "\n\n".join(lines)
    
    
    async def _create_anonymous_report(
        self,
        conversation: ChatbotConversation,
        assessment: Dict
    ):
        """Create anonymous symptom report for surveillance"""
        
        # Extract age group from user info
        age = conversation.user_info.get("age")
        age_group = self._get_age_group(age) if age else None
        
        report = AnonymousSymptomReport(
            conversation_id=conversation.id,
            report_date=datetime.now(timezone.utc),
            city=conversation.city,
            district=None,  # Could extract from location
            age_group=age_group,
            gender=conversation.user_info.get("gender"),
            symptoms=conversation.primary_symptoms,
            suspected_disease=assessment.get("primary_diagnosis", {}).get("condition")
        )
        
        self.db.add(report)
    
    
    def _get_age_group(self, age: int) -> str:
        """Convert age to age group"""
        if age <= 18:
            return "0-18"
        elif age <= 40:
            return "19-40"
        elif age <= 60:
            return "41-60"
        else:
            return "60+"
