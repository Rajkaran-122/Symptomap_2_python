
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
