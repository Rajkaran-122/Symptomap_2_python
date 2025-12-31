
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
