import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_user
from app import models, schemas
from app.services import gemini

router = APIRouter(prefix="/tutor", tags=["AI Tutor"])

@router.post("/chat")
async def chat_with_tutor(
    prompt: schemas.ChatPromptIn,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submits a doubt to the AI Tutor.
    Includes the lesson content as context if lesson_id is specified.
    Saves conversation to database.
    """
    lesson_title = None
    lesson_content = None
    
    # 1. Fetch lesson context if provided
    if prompt.lesson_id:
        lesson_query = select(models.Lesson).where(models.Lesson.lesson_id == prompt.lesson_id)
        lesson_res = await db.execute(lesson_query)
        lesson = lesson_res.scalars().first()
        if lesson:
            lesson_title = lesson.title
            lesson_content = lesson.content

    # 2. Call Gemini API
    answer = await gemini.ask_tutor(
        question=prompt.question,
        lesson_title=lesson_title,
        lesson_content=lesson_content
    )

    # 3. Save to database
    chat_record = models.ChatHistory(
        user_id=current_user.user_id,
        lesson_id=prompt.lesson_id,
        question=prompt.question,
        answer=answer
    )
    db.add(chat_record)
    await db.commit()
    await db.refresh(chat_record)

    return {
        "chat_id": chat_record.chat_id,
        "question": chat_record.question,
        "answer": chat_record.answer,
        "timestamp": chat_record.timestamp
    }


@router.get("/history", response_model=List[schemas.ChatHistoryOut])
async def get_chat_history(
    lesson_id: Optional[uuid.UUID] = None,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches the history of doubts solved.
    Optionally filters by lesson_id.
    """
    query = select(models.ChatHistory).where(models.ChatHistory.user_id == current_user.user_id)
    
    if lesson_id:
        query = query.where(models.ChatHistory.lesson_id == lesson_id)
        
    query = query.order_by(models.ChatHistory.timestamp.asc())
    result = await db.execute(query)
    chats = result.scalars().all()
    
    return chats
