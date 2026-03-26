"""
AI Doctor Chatbot Service
Implements complete medical conversation flowchart with GPT-4
"""

import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
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
        """
        try:
            # Get conversation from database
            result = await self.db.execute(
                select(ChatbotConversation).where(ChatbotConversation.session_id == session_id)
            )
            conversation = result.scalar_one_or_none()
            
            if not conversation:
                raise ValueError("Conversation not found")
            
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
            
            # Update conversation state (Now handled exclusively here)
            await self._update_conversation_state(conversation, bot_response)
            
            await self.db.commit()
            
            return {
                "session_id": session_id,
                "bot_messages": [bot_response],
                "conversation_state": conversation.conversation_state,
                "completion_percentage": self._calculate_completion(conversation)
            }
        except Exception as e:
            await self.db.rollback()
            print(f"ERROR in process_message: {e}")
            return {
                "session_id": session_id,
                "bot_messages": [{
                    "type": "text",
                    "content": "Thank you for your patience. I am currently reviewing your input to ensure the most accurate health guidance. Please consult a healthcare professional for a final medical diagnosis.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }],
                "conversation_state": "error",
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
        """
        Generate AI response using GPT-4 with localized context.
        BRD: Always use database data for outbreaks, alerts, and predictions.
        """
        
        # 1. FETCH DATABASE CONTEXT
        context_str = ""
        if conversation.city:
            outbreaks = await self._check_local_outbreaks(conversation.city, conversation.country)
            if outbreaks:
                context_str += f"\n[LOCAL OUTBREAK DATA for {conversation.city}]:\n{json.dumps(outbreaks, indent=2)}\n"
            
            hospitals = await self._get_nearby_hospitals(conversation.city)
            if hospitals:
                context_str += f"\n[NEARBY HOSPITALS for {conversation.city}]:\n{json.dumps(hospitals, indent=2)}\n"
            
            alerts = await self._get_local_alerts(conversation.city)
            if alerts:
                context_str += f"\n[OFFICIAL HEALTH ALERTS for {conversation.city}]:\n{json.dumps(alerts, indent=2)}\n"
            
            predictions = await self._get_local_predictions(conversation.city)
            if predictions:
                context_str += f"\n[HEALTH RISK PREDICTIONS for {conversation.city}]:\n{json.dumps(predictions, indent=2)}\n"

        # 2. BUILD PROMPT & MESSAGES
        system_prompt = self._build_system_prompt(conversation.conversation_state, context_str)
        
        messages = [
            {"role": "system", "content": system_prompt},
            *history,
            {"role": "user", "content": message}
        ]
        
        if image_url:
            messages[-1]["content"] = [
                {"type": "text", "text": message},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]

        # 3. CALL AI (OR SMART FALLBACK)
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            return {
                "type": "text",
                "content": response.choices[0].message.content,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except openai.RateLimitError:
            # BRD FR-6: Smart Fallback (Advice based on limited data)
            content = self._generate_smart_fallback(message, context_str)
            return {
                "type": "text",
                "content": content,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "is_fallback": True
            }
        except Exception as e:
            print(f"AI Generation Error: {e}")
            return {
                "type": "text",
                "content": "Thank you for sharing those details. I'm focusing on providing you with the best insights. In the meantime, please prioritize hydration and rest.",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }


    def _build_system_prompt(self, conversation_state: str, context: str = "") -> str:
        """Build system prompt based on conversation state and database context"""
        
        base_prompt = f"""You are a professional, empathetic medical AI health assistant. Your goal is to provide structured analysis while prioritizing user safety.

CRITICAL RULES:
1. **STRICTLY NO MEDICINES**: You are FORBIDDEN from naming any specific medicines, brands, or pharmaceutical drugs (e.g., No Paracetamol, No Ibuprofen, No Antibiotics). 
2. **FOCUS ON REMEDIES & PRECAUTIONS**: Instead of medicines, recommend Home Remedies (hydration, rest, steam, herbal tea, sponge baths) and Precautions (hygiene, sanitation, mosquito nets, stagnant water clearance).
3. **INVESTIGATE BEFORE DECIDING**: Do not categorize the user immediately. Ask probing "Cross-Questions" to confirm the actual issue (e.g., check for rashes, neck stiffness, or cough if they have a fever).
4. **DECIDE DISEASE**: After probing, provide a likely assessment of the condition (e.g., "Symptoms suggest a Viral Fever pattern").
5. **TRIAGE CRITERIA**: 
   - **DANGER CRITERIA**: Difficulty breathing, chest pain, high fever (>103°F), sudden confusion, or stroke symptoms. Mention "DANGER CRITERIA" explicitly and recommend immediate doctor/emergency visit.
   - **NORMAL CRITERIA**: Mild symptoms. Provide Analysis, Precautions, and Home Remedies.

Your analysis must use localized health data if available (Outbreaks, Alerts, Predictions).

[CURRENT DATABASE INSIGHTS FOR THIS LOCATION]:
{context if context else "No specific local outbreak data, alerts, or predictions currently reported for this area."}
"""
        
        state_prompts = {
            "greeting": "Welcome the user and ask for their main symptoms. Be empathetic and professional.",
            
            "symptom_collection": """The user has shared symptoms. Your task is to INVESTIGATE:
1. Ask probing 'Cross-Questions' to confirm the actual issue (e.g., if fever, check for rashes/stiffness/cough).
2. Clarify: onset, severity (1-10), characteristics, and aggravating factors.
3. Keep probing to rule out DANGER requirements. Do not suggest medicines.""",
            
            "history_collection": """Probe into medical history:
- Chronic conditions, allergies, recent travel.
- Use this to cross-reference with localized OUTBREAKS or ALERTS.""",
            
            "assessment": """Now make your final DECISION and IDENTIFY THE ILLNESS:
1. Summary of findings (recap of what you've investigated).
2. Illness Decision: Clearly state the most likely condition/illness identified through your cross-questioning.
3. Triage: State if it is **NORMAL** or **DANGER** criteria.
4. Analysis: Explain the evidence leading to this specific illness identification.
5. Management: Provide Precautions and Home Remedies only (STRICTLY NO MEDICINES).
6. Professional Ending: End with "Thank you for sharing your symptoms. Please consult a registered medical professional for a definitive diagnosis." or a similar polite ending script."""
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
        
        try:
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
        except Exception as e:
            print(f"Assessment generation failed: {e}")
            return {
                "severity": "routine", # Default safety
                "primary_diagnosis": {"condition": "Assessment failed", "confidence": 0.0},
                "recommendation": {"action": "consult_doctor", "urgency": "routine"}
            }
    
    
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
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": soap_prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"SOAP note generation failed: {e}")
            return {
                "subjective": "Error generating note.",
                "objective": "N/A",
                "assessment": "N/A",
                "plan": "Consult doctor."
            }
    
    
    async def _generate_recommendations(
        self,
        conversation: ChatbotConversation,
        assessment: Dict
    ) -> Dict:
        """Generate home care recommendations (Precautions and Remedies only)"""
        
        severity = assessment.get("severity", "routine")
        
        if severity == "emergency":
            return {
                "action": "emergency",
                "message": "Go to emergency room immediately or call emergency services. Do not attempt home treatment."
            }
        
        # Generate detailed recommendations based on symptoms
        symptoms_text = json.dumps(conversation.primary_symptoms)
        
        rec_prompt = f"""Based on these symptoms and {severity} severity, provide suggestions.
STRICT RULE: NO MEDICINE NAMES.

Symptoms: {symptoms_text}

Provide JSON with:
{{
    "home_remedies": ["hydration", "rest", "lukewarm sponge bath", ...],
    "precautions": ["isolate if sick", "mosquito-proof area", "monitor temperature"],
    "when_to_see_doctor": {{"urgent": [...], "routine": [...]}},
    "safety_warning": "Consult a doctor for diagnosis and prescriptions."
}}"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": rec_prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Recommendation generation failed: {e}")
            return {
                "home_care": ["Rest and hydrate"],
                "when_to_see_doctor": {"routine": ["If symptoms persist"]},
                "message": "Unable to generate specific recommendations. Please consult a doctor."
            }
    
    
    async def _check_local_outbreaks(
        self,
        city: Optional[str],
        country: Optional[str]
    ) -> Optional[Dict]:
        """Check for disease outbreaks in user's location"""
        
        if not city:
            return None
            
        try:
            # Import models locally to avoid circular dependencies
            from app.models.outbreak import Outbreak, Hospital
            
            # Query recent outbreaks in this city (last 30 days)
            # NEED TO JOIN WITH HOSPITAL TO FILTER BY CITY
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            
            result = await self.db.execute(
                select(Outbreak)
                .join(Hospital, Outbreak.hospital_id == Hospital.id)
                .where(Hospital.city.ilike(f"%{city}%"))
                .where(Outbreak.date_reported >= thirty_days_ago)
                .order_by(Outbreak.patient_count.desc())
                .limit(3)
            )
            outbreaks = result.scalars().all()
            
            if not outbreaks:
                return None
                
            outbreak_data = []
            for ob in outbreaks:
                outbreak_data.append({
                    "disease": ob.disease_type,
                    "cases": ob.patient_count,
                    "severity": ob.severity,
                    "status": "Verified" if ob.verified else "Reported"
                })
                
            return {
                "city": city,
                "outbreaks": outbreak_data,
                "warning": f"There are {len(outbreaks)} active health concerns in {city}."
            }
        except Exception as e:
            print(f"Error checking local outbreaks: {e}")
            return None
    
    
    async def _get_nearby_hospitals(
        self,
        city: str
    ) -> List[Dict]:
        """Get available hospitals in the area"""
        try:
            from app.models.outbreak import Hospital
            
            result = await self.db.execute(
                select(Hospital)
                .where(Hospital.city.ilike(f"%{city}%"))
                .order_by(Hospital.available_beds.desc())
                .limit(5)
            )
            hospitals = result.scalars().all()
            
            return [{
                "name": h.name,
                "address": h.address,
                "available_beds": h.available_beds,
                "phone": h.phone,
                "type": h.hospital_type
            } for h in hospitals]
        except Exception as e:
            print(f"Error fetching hospitals: {e}")
            return []


    async def _get_disease_context(
        self,
        disease_name: str
    ) -> Optional[Dict]:
        """Get detailed information about a disease"""
        try:
            from app.models.chatbot import DiseaseInfo
            
            result = await self.db.execute(
                select(DiseaseInfo).where(DiseaseInfo.disease_name.ilike(f"%{disease_name}%"))
            )
            disease = result.scalar_one_or_none()
            
            if not disease:
                return None
                
            return {
                "name": disease.disease_name,
                "category": disease.category,
                "symptoms": disease.common_symptoms,
                "red_flags": disease.red_flag_symptoms,
                "prevention": disease.prevention_measures,
                "transmission": disease.transmission_modes
            }
        except Exception as e:
            print(f"Error fetching disease info: {e}")
            return None


    async def _get_local_alerts(
        self,
        city: str
    ) -> List[Dict]:
        """Get active health alerts for the zone"""
        try:
            from app.models.outbreak import Alert
            
            # Search alerts where zone_name contains city name or message mentions city
            result = await self.db.execute(
                select(Alert)
                .where((Alert.zone_name.ilike(f"%{city}%")) | (Alert.message.ilike(f"%{city}%")))
                .where((Alert.expires_at == None) | (Alert.expires_at > datetime.now(timezone.utc)))
                .order_by(Alert.sent_at.desc())
                .limit(3)
            )
            alerts = result.scalars().all()
            
            return [{
                "title": a.title,
                "message": a.message,
                "severity": a.severity,
                "type": a.alert_type
            } for a in alerts]
        except Exception as e:
            print(f"Error fetching alerts: {e}")
            return []


    async def _get_local_predictions(
        self,
        city: str
    ) -> List[Dict]:
        """Get disease risk predictions for the zone"""
        try:
            from app.models.outbreak import Prediction
            
            result = await self.db.execute(
                select(Prediction)
                .where(Prediction.zone_name.ilike(f"%{city}%"))
                .where(Prediction.prediction_date > datetime.now(timezone.utc))
                .order_by(Prediction.risk_score.desc())
                .limit(3)
            )
            predictions = result.scalars().all()
            
            return [{
                "disease": p.disease_type,
                "risk_level": p.risk_level,
                "risk_score": p.risk_score,
                "probability": f"{p.probability_of_spread}%"
            } for p in predictions]
        except Exception as e:
            print(f"Error fetching predictions: {e}")
            return []


    def _generate_smart_fallback(self, user_query: str, context: str = "") -> str:
        """
        BRD FR-6: Smart suggestion when API is down/rate-limited.
        Strictly No Medicine Names. Focus on Remedies/Precautions.
        """
        query = user_query.lower()
        
        # 1. Base response
        response = "I'm currently optimizing my live data connection, but based on health guidelines and local records, I have these suggestions for you:\n\n"
        
        # 2. Inject context if we have it
        if context:
            response += "🔍 **DATABASE-DRIVEN INSIGHTS**:\n"
            if "OUTBREAK" in context:
                response += "- Active health alerts are reported in your area. Maintain high hygiene standards.\n"
            if "HOSPITAL" in context:
                response += "- Local medical facilities are available for professional consultation.\n"
            response += "\n"
        
        # 3. Add General Category Fallbacks (Remedies & Precautions Only)
        advice_parts = []
        
        if any(w in query for w in ["fever", "temperature", "body pain"]):
            advice_parts.append("🌡️ **Remedy & Precaution**: Focus on high fluid intake (ORS, water, coconut water) and complete bed rest. Use lukewarm sponge baths if temperature is high. Avoid heavy physical activity transitions.")
            
        if any(w in query for w in ["cough", "cold", "sore throat"]):
            advice_parts.append("🧣 **Respiratory Precautions**: Steam inhalation can help clear nasal passages. Gargle with warm salt water. Keep yourself warm and avoid cold beverages.")
            
        if any(w in query for w in ["prevent", "avoid", "dengue", "mosquito"]):
            advice_parts.append("🦟 **Environmental Precaution**: Ensure no stagnant water exists in containers/coolers. Use mosquito nets and screens. Wear full-sleeved light-colored clothing.")

        if not advice_parts:
            advice_parts.append("📝 **General Observation**: Monitor your symptoms very closely. Take note of any new developments like rashes, stiffness, or breathing issues to share with a doctor.")
            
        response += "\n\n⚠️ *I am an AI health assistant. I do not prescribe medicines. Thank you for using SymptoMap. Please consult a registered medical professional for diagnosis and pharmaceutical treatment.*"
        
        return response


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
        """
        Update conversation state based on progress.
        Enforces PROBE -> DECIDE flow:
        - Greeting -> Symptom Collection (mandatory)
        - Symptom Collection -> History (after at least 2 probing exchanges)
        - History -> Assessment (after history probe)
        """
        current_state = conversation.conversation_state
        # message_count includes both user and assistant messages stored in conversation_data
        message_count = len(conversation.conversation_data or [])
        
        if current_state == "greeting":
            # Move to symptom collection after the first user description
            if message_count >= 2:
                conversation.conversation_state = "symptom_collection"
        
        elif current_state == "symptom_collection":
            # Enforce at least 2 cross-questioning exchanges (approx 6-8 messages total)
            if message_count >= 8:
                conversation.conversation_state = "history_collection"
        
        elif current_state == "history_collection":
            # Move to assessment after history is gathered (approx 12+ messages total)
            if message_count >= 12:
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
