"""

Chatbot API routes

"""



from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Body

from fastapi.responses import Response

from sqlalchemy.ext.asyncio import AsyncSession

from pydantic import BaseModel

from typing import Optional, Dict

import uuid



from app.core.database import get_db

from app.services.chatbot_service import ChatbotService

from app.services.image_upload_service import ImageUploadService

from app.services.pdf_export_service import PDFExportService





router = APIRouter(prefix="/chatbot", tags=["Chatbot"])





# Request/Response models

class StartConversationRequest(BaseModel):

    user_info: Optional[Dict] = None

    location: Optional[Dict] = None





class MessageRequest(BaseModel):

    session_id: str

    message: str

    image_url: Optional[str] = None





class EndConversationRequest(BaseModel):

    session_id: str





class FeedbackRequest(BaseModel):

    session_id: str

    rating: int

    comments: Optional[str] = None





# Routes

@router.post("/start")

async def start_conversation(

    request: StartConversationRequest,

    db: AsyncSession = Depends(get_db)

):

    """Start a new AI doctor chatbot conversation"""

    

    session_id = f"conv_{uuid.uuid4().hex}"

    

    chatbot = ChatbotService(db)

    result = await chatbot.start_conversation(

        session_id=session_id,

        user_info=request.user_info,

        location=request.location

    )

    

    return result





@router.post("/message")

async def send_message(

    request: MessageRequest,

    db: AsyncSession = Depends(get_db)

):

    """Send a message and get AI response"""

    

    chatbot = ChatbotService(db)

    

    try:

        result = await chatbot.process_message(

            session_id=request.session_id,

            message=request.message,

            image_url=request.image_url

        )

        return result

    except ValueError as e:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail=str(e)

        )





@router.post("/end")

async def end_conversation(

    request: EndConversationRequest,

    db: AsyncSession = Depends(get_db)

):

    """End conversation and get final assessment"""

    

    chatbot = ChatbotService(db)

    

    try:

        result = await chatbot.end_conversation(request.session_id)

        return result

    except ValueError as e:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail=str(e)

        )





@router.post("/feedback")

async def submit_feedback(

    request: FeedbackRequest,

    db: AsyncSession = Depends(get_db)

):

    """Submit user feedback on conversation"""

    

    from sqlalchemy import select, update

    from app.models.chatbot import ChatbotConversation

    

    result = await db.execute(

        select(ChatbotConversation).where(

            ChatbotConversation.session_id == request.session_id

        )

    )

    conversation = result.scalar_one_or_none()

    

    if not conversation:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="Conversation not found"

        )

    

    conversation.user_feedback = request.rating

    conversation.feedback_comments = request.comments

    

    await db.commit()

    

    return {

        "message": "Thank you for your feedback!",

        "feedback_id": str(conversation.id)

    }





@router.get("/conversation/{session_id}")

async def get_conversation(

    session_id: str,

    db: AsyncSession = Depends(get_db)

):

    """Get conversation history"""

    

    from sqlalchemy import select

    from app.models.chatbot import ChatbotConversation

    

    result = await db.execute(

        select(ChatbotConversation).where(

            ChatbotConversation.session_id == session_id

        )

    )

    conversation = result.scalar_one_or_none()

    

    if not conversation:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="Conversation not found"

        )

    

    return {

        "session_id": conversation.session_id,

        "started_at": conversation.started_at,

        "ended_at": conversation.ended_at,

        "conversation_state": conversation.conversation_state,

        "messages": conversation.conversation_data,

        "severity_assessment": conversation.severity_assessment,

        "soap_note": conversation.soap_note,

        "recommendations": conversation.recommendations

    }



@router.post("/upload-image")

async def upload_image(

    session_id: str,

    file: UploadFile = File(...),

    db: AsyncSession = Depends(get_db)

):

    """Upload image for symptom analysis"""

    

    # Verify session exists

    from app.models.chatbot import ChatbotConversation

    from sqlalchemy import select

    

    result = await db.execute(

        select(ChatbotConversation).where(ChatbotConversation.session_id == session_id)

    )

    conversation = result.scalar_one_or_none()

    

    if not conversation:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="Session not found"

        )

    

    # Save image

    image_service = ImageUploadService()

    file_info = await image_service.save_image(file, session_id)

    

    # Get analysis (placeholder for now)

    analysis = await image_service.get_image_analysis(file_info['filepath'])

    

    return {

        "session_id": session_id,

        "file_info": file_info,

        "analysis": analysis,

        "message": "Image uploaded successfully. Continue describing your symptoms."

   }





@router.get("/export-pdf/{session_id}")

async def export_conversation_pdf(

    session_id: str,

    db: AsyncSession = Depends(get_db)

):

    """Export conversation as PDF report"""

    

    # Get conversation

    from app.models.chatbot import ChatbotConversation

    from sqlalchemy import select

    

    result = await db.execute(

        select(ChatbotConversation).where(ChatbotConversation.session_id == session_id)

    )

    conversation = result.scalar_one_or_none()

    

    if not conversation:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="Conversation not found"

        )

    

    # Prepare data

    conversation_data = {

        "session_id": session_id,

        "soap_note": conversation.soap_note,

        "assessment": conversation.assessment,

        "recommendations": conversation.recommendations

    }

    

    # Generate PDF

    pdf_service = PDFExportService()

    pdf_bytes = pdf_service.generate_conversation_pdf(conversation_data)

    

    # Return as downloadable file

    return Response(

        content=pdf_bytes,

        media_type="application/pdf",

        headers={

            "Content-Disposition": f"attachment; filename=health_report_{session_id}.pdf"

        }

    )


@router.post("/flag/{session_id}")
async def flag_for_review(
    session_id: str,
    reason: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    """Flag a conversation for human review"""
    from app.models.chatbot import ChatbotConversation
    from sqlalchemy import select
    
    result = await db.execute(
        select(ChatbotConversation).where(ChatbotConversation.session_id == session_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    conversation.flagged_for_review = True
    conversation.review_reason = reason
    await db.commit()
    
    return {"message": "Conversation flagged for human review"}
