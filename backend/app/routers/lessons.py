import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_user
from app import models, schemas

router = APIRouter(prefix="/lessons", tags=["Lessons"])

@router.get("", response_model=List[schemas.LessonOut])
async def list_lessons(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lists all lessons with their unlock status for the current user.
    """
    # Join Lessons with User's Progress
    query = (
        select(models.Lesson, models.Progress.status)
        .join(models.Progress, models.Progress.lesson_id == models.Lesson.lesson_id)
        .where(models.Progress.user_id == current_user.user_id)
        .order_by(models.Lesson.order_index)
    )
    result = await db.execute(query)
    
    lesson_list = []
    for lesson, progress_status in result.all():
        lesson_list.append(
            schemas.LessonOut(
                lesson_id=lesson.lesson_id,
                title=lesson.title,
                week_number=lesson.week_number,
                month_number=lesson.month_number,
                order_index=lesson.order_index,
                status=progress_status
            )
        )
    return lesson_list


@router.get("/{lesson_id}", response_model=schemas.LessonDetailOut)
async def get_lesson_detail(
    lesson_id: uuid.UUID,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches the detail content of a lesson. 
    Aborts if the lesson is locked.
    """
    # Check progress record first
    progress_query = select(models.Progress).where(
        models.Progress.user_id == current_user.user_id,
        models.Progress.lesson_id == lesson_id
    )
    progress_result = await db.execute(progress_query)
    progress = progress_result.scalars().first()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson progress record not found"
        )
        
    if progress.status == "locked":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This lesson is locked. Please complete the previous lesson, its quiz, and assignment first!"
        )
        
    # Fetch lesson content
    lesson_query = select(models.Lesson).where(models.Lesson.lesson_id == lesson_id)
    lesson_result = await db.execute(lesson_query)
    lesson = lesson_result.scalars().first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson content not found"
        )
        
    return schemas.LessonDetailOut(
        lesson_id=lesson.lesson_id,
        course_id=lesson.course_id,
        title=lesson.title,
        content=lesson.content,
        week_number=lesson.week_number,
        month_number=lesson.month_number,
        order_index=lesson.order_index,
        status=progress.status
    )
