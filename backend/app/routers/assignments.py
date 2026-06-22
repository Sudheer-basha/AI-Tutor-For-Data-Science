import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_user
from app import models, schemas
from app.services import gemini, progress

router = APIRouter(prefix="/assignments", tags=["Assignments"])

@router.get("/by-lesson/{lesson_id}", response_model=schemas.AssignmentOut)
async def get_assignment_by_lesson(
    lesson_id: uuid.UUID,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches the assignment details for a specific lesson.
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
            detail="This assignment is locked. Please unlock the lesson first."
        )

    # 2. Fetch assignment
    assign_query = select(models.Assignment).where(models.Assignment.lesson_id == lesson_id)
    assign_res = await db.execute(assign_query)
    assignment = assign_res.scalars().first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found for this lesson"
        )
        
    return assignment

@router.get("/{assignment_id}", response_model=schemas.AssignmentOut)
async def get_assignment(
    assignment_id: uuid.UUID,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches details for a specific assignment by ID.
    Checks that the corresponding lesson is unlocked.
    """
    query = (
        select(models.Assignment, models.Progress.status)
        .join(models.Progress, models.Progress.lesson_id == models.Assignment.lesson_id)
        .where(
            models.Assignment.assignment_id == assignment_id,
            models.Progress.user_id == current_user.user_id
        )
    )
    result = await db.execute(query)
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
        
    assignment, progress_status = row
    
    if progress_status == "locked":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This assignment is locked. Please unlock the corresponding lesson first."
        )
        
    return assignment



@router.get("/submission/{assignment_id}", response_model=schemas.UserAssignmentOut)
async def get_submission(
    assignment_id: uuid.UUID,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves the current user's latest submission for an assignment.
    """
    sub_query = (
        select(models.UserAssignment)
        .where(
            models.UserAssignment.user_id == current_user.user_id,
            models.UserAssignment.assignment_id == assignment_id
        )
        .order_by(models.UserAssignment.submitted_at.desc())
    )
    sub_res = await db.execute(sub_query)
    submission = sub_res.scalars().first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No submission found"
        )
    return submission


@router.post("/{assignment_id}/submit")
async def submit_assignment(
    assignment_id: uuid.UUID,
    submission_data: schemas.AssignmentSubmissionIn,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submits an assignment, triggers AI evaluation, updates lesson progress,
    and returns score, feedback, and unlock/badge triggers.
    """
    # 1. Fetch assignment and lesson context
    assign_query = (
        select(models.Assignment, models.Lesson)
        .join(models.Lesson, models.Lesson.lesson_id == models.Assignment.lesson_id)
        .where(models.Assignment.assignment_id == assignment_id)
    )
    assign_res = await db.execute(assign_query)
    row = assign_res.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
        
    assignment, lesson = row
    
    # 2. Check if lesson is unlocked
    prog_query = select(models.Progress).where(
        models.Progress.user_id == current_user.user_id,
        models.Progress.lesson_id == lesson.lesson_id
    )
    prog_res = await db.execute(prog_query)
    prog = prog_res.scalars().first()
    
    if not prog or prog.status == "locked":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot submit assignments for a locked lesson."
        )

    # 3. Call AI grading service
    evaluation = await gemini.evaluate_assignment(
        assignment_title=assignment.title,
        assignment_desc=assignment.description,
        submission=submission_data.submission_content
    )
    
    score = evaluation.get("score", 0)
    passed = evaluation.get("passed", False)
    feedback = evaluation.get("feedback", "No feedback provided.")
    status_val = "passed" if passed else "failed"

    # 4. Check if there's an existing submission and overwrite or create new
    existing_sub_query = select(models.UserAssignment).where(
        models.UserAssignment.user_id == current_user.user_id,
        models.UserAssignment.assignment_id == assignment_id
    )
    existing_sub_res = await db.execute(existing_sub_query)
    user_assignment = existing_sub_res.scalars().first()
    
    if user_assignment:
        user_assignment.submission_content = submission_data.submission_content
        user_assignment.score = score
        user_assignment.feedback = feedback
        user_assignment.status = status_val
        user_assignment.submitted_at = datetime.utcnow()
    else:
        user_assignment = models.UserAssignment(
            user_id=current_user.user_id,
            assignment_id=assignment_id,
            submission_content=submission_data.submission_content,
            score=score,
            feedback=feedback,
            status=status_val,
            submitted_at=datetime.utcnow()
        )
        db.add(user_assignment)
        
    await db.flush()

    # 5. Evaluate progress and unlock next lesson if both assignment & quiz are passed
    unlock_details = await progress.check_and_unlock_next_lesson(
        user_id=current_user.user_id,
        lesson_id=lesson.lesson_id,
        db=db
    )
    
    await db.commit()

    return {
        "user_assignment_id": user_assignment.user_assignment_id,
        "score": score,
        "feedback": feedback,
        "status": status_val,
        "lesson_completed": unlock_details.get("lesson_completed", False),
        "unlocked_next": unlock_details.get("unlocked_next", False),
        "badge_earned": unlock_details.get("badge_earned", None)
    }
