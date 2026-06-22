import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_user
from app import models, schemas
from app.services import progress

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])

@router.get("/by-lesson/{lesson_id}", response_model=List[schemas.QuizQuestionOut])
async def get_quiz_questions(
    lesson_id: uuid.UUID,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches the multiple-choice questions for a specific lesson's quiz.
    Checks that the lesson is unlocked first.
    """
    # 1. Check if lesson is unlocked
    prog_query = select(models.Progress).where(
        models.Progress.user_id == current_user.user_id,
        models.Progress.lesson_id == lesson_id
    )
    prog_res = await db.execute(prog_query)
    prog = prog_res.scalars().first()
    
    if not prog or prog.status == "locked":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This quiz is locked. Please unlock the lesson first."
        )

    # 2. Fetch quiz questions
    quiz_query = select(models.Quiz).where(models.Quiz.lesson_id == lesson_id)
    quiz_res = await db.execute(quiz_query)
    questions = quiz_res.scalars().all()
    
    return [
        schemas.QuizQuestionOut(
            quiz_id=q.quiz_id,
            question=q.question,
            options=q.options
        ) for q in questions
    ]


@router.get("/status/{lesson_id}")
async def get_quiz_status(
    lesson_id: uuid.UUID,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if the user has already completed the quiz and get their score.
    """
    query = select(models.UserQuiz).where(
        models.UserQuiz.user_id == current_user.user_id,
        models.UserQuiz.lesson_id == lesson_id
    )
    result = await db.execute(query)
    user_quiz = result.scalars().first()
    
    if not user_quiz:
        return {"completed": False, "score": None}
        
    return {
        "completed": True,
        "score": user_quiz.score,
        "passed": user_quiz.score >= 70,
        "completed_at": user_quiz.completed_at
    }


@router.post("/by-lesson/{lesson_id}/submit", response_model=schemas.QuizSubmissionResultOut)
async def submit_quiz(
    lesson_id: uuid.UUID,
    submission_data: schemas.QuizSubmissionIn,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Evaluates MCQ answers, records the score, checks if lesson requirements
    are satisfied, and triggers progression updates.
    """
    # 1. Fetch correct answers for this lesson
    quiz_query = select(models.Quiz).where(models.Quiz.lesson_id == lesson_id)
    quiz_res = await db.execute(quiz_query)
    questions = quiz_res.scalars().all()
    
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No quiz questions found for this lesson"
        )
        
    # Build dictionary of correct answers
    correct_answers_dict = {q.quiz_id: q.correct_option for q in questions}
    
    # 2. Score the submission
    correct_count = 0
    total_count = len(questions)
    details = []
    
    user_answers_dict = {ans.quiz_id: ans.selected_option for ans in submission_data.answers}
    
    for q in questions:
        user_opt = user_answers_dict.get(q.quiz_id)
        correct_opt = correct_answers_dict.get(q.quiz_id)
        
        is_correct = (user_opt == correct_opt)
        if is_correct:
            correct_count += 1
            
        details.append({
            "quiz_id": str(q.quiz_id),
            "correct": is_correct,
            "correct_option": correct_opt,
            "user_option": user_opt
        })
        
    score = int((correct_count / total_count) * 100)
    passed = (score >= 70)

    # 3. Save or update UserQuiz entry
    existing_q_query = select(models.UserQuiz).where(
        models.UserQuiz.user_id == current_user.user_id,
        models.UserQuiz.lesson_id == lesson_id
    )
    existing_q_res = await db.execute(existing_q_query)
    user_quiz = existing_q_res.scalars().first()
    
    if user_quiz:
        # Update with highest score or latest score (let's save highest/latest)
        user_quiz.score = max(user_quiz.score, score)
        user_quiz.completed_at = datetime.utcnow()
    else:
        user_quiz = models.UserQuiz(
            user_id=current_user.user_id,
            lesson_id=lesson_id,
            score=score,
            completed_at=datetime.utcnow()
        )
        db.add(user_quiz)
        
    await db.flush()

    # 4. Check if lesson is now fully completed
    unlock_details = await progress.check_and_unlock_next_lesson(
        user_id=current_user.user_id,
        lesson_id=lesson_id,
        db=db
    )
    
    await db.commit()

    return schemas.QuizSubmissionResultOut(
        score=score,
        passed=passed,
        correct_count=correct_count,
        total_count=total_count,
        details=details
    )
