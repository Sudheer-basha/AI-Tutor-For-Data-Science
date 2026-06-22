import uuid
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app import models

async def check_and_unlock_next_lesson(
    user_id: uuid.UUID,
    lesson_id: uuid.UUID,
    db: AsyncSession
) -> dict:
    """
    Checks if a user has completed both the quiz and the assignment for a given lesson.
    If yes, marks the lesson as completed, unlocks the next lesson, and checks/awards badges.
    Returns a status dict.
    """
    # 1. Fetch current lesson
    lesson_query = select(models.Lesson).where(models.Lesson.lesson_id == lesson_id)
    lesson_res = await db.execute(lesson_query)
    current_lesson = lesson_res.scalars().first()
    
    if not current_lesson:
        return {"status": "error", "message": "Lesson not found"}

    # 2. Check if assignment is passed (score >= 70)
    # Get all assignments for this lesson
    assignments_query = select(models.Assignment).where(models.Assignment.lesson_id == lesson_id)
    assignments_res = await db.execute(assignments_query)
    lesson_assignments = assignments_res.scalars().all()
    
    assignment_passed = True
    for assignment in lesson_assignments:
        sub_query = select(models.UserAssignment).where(
            models.UserAssignment.user_id == user_id,
            models.UserAssignment.assignment_id == assignment.assignment_id,
            models.UserAssignment.status == "passed"
        )
        sub_res = await db.execute(sub_query)
        submission = sub_res.scalars().first()
        if not submission:
            assignment_passed = False
            break

    # 3. Check if quiz is passed (score >= 70)
    quiz_passed = False
    # Check if there are quizzes for this lesson
    quizzes_count_query = select(func.count(models.Quiz.quiz_id)).where(models.Quiz.lesson_id == lesson_id)
    quizzes_count_res = await db.execute(quizzes_count_query)
    total_quizzes = quizzes_count_res.scalar() or 0
    
    if total_quizzes == 0:
        # If no quiz, auto-pass quiz
        quiz_passed = True
    else:
        user_quiz_query = select(models.UserQuiz).where(
            models.UserQuiz.user_id == user_id,
            models.UserQuiz.lesson_id == lesson_id,
            models.UserQuiz.score >= 70
        )
        user_quiz_res = await db.execute(user_quiz_query)
        user_quiz = user_quiz_res.scalars().first()
        if user_quiz:
            quiz_passed = True

    # 4. If both passed, complete current lesson and unlock next
    unlocked_next = False
    new_badge_earned = None
    
    if assignment_passed and quiz_passed:
        # Mark current lesson progress as completed
        progress_query = select(models.Progress).where(
            models.Progress.user_id == user_id,
            models.Progress.lesson_id == lesson_id
        )
        progress_res = await db.execute(progress_query)
        progress = progress_res.scalars().first()
        
        if progress and progress.status != "completed":
            progress.status = "completed"
            progress.completed_at = datetime.utcnow()
            db.add(progress)
            await db.flush()
            
            # Find next lesson (order_index = current + 1)
            next_lesson_query = select(models.Lesson).where(
                models.Lesson.order_index == current_lesson.order_index + 1
            )
            next_lesson_res = await db.execute(next_lesson_query)
            next_lesson = next_lesson_res.scalars().first()
            
            if next_lesson:
                # Unlock next lesson progress
                next_progress_query = select(models.Progress).where(
                    models.Progress.user_id == user_id,
                    models.Progress.lesson_id == next_lesson.lesson_id
                )
                next_progress_res = await db.execute(next_progress_query)
                next_progress = next_progress_res.scalars().first()
                
                if next_progress and next_progress.status == "locked":
                    next_progress.status = "unlocked"
                    next_progress.unlocked_at = datetime.utcnow()
                    db.add(next_progress)
                    unlocked_next = True
            
            # 5. Check and award badges
            new_badge_earned = await check_and_award_badges(user_id, db)
            
            await db.commit()

    return {
        "status": "success",
        "lesson_completed": assignment_passed and quiz_passed,
        "unlocked_next": unlocked_next,
        "badge_earned": new_badge_earned
    }

async def check_and_award_badges(user_id: uuid.UUID, db: AsyncSession) -> str:
    """
    Counts completed lessons and awards milestone badges.
    Returns the name of the badge if a new one is awarded, else None.
    """
    # Count completed lessons
    completed_count_query = select(func.count(models.Progress.progress_id)).where(
        models.Progress.user_id == user_id,
        models.Progress.status == "completed"
    )
    completed_count_res = await db.execute(completed_count_query)
    completed_count = completed_count_res.scalar() or 0
    
    # Query all badges
    badges_query = select(models.Badge)
    badges_res = await db.execute(badges_query)
    all_badges = badges_res.scalars().all()
    
    newly_earned_badge_name = None
    
    for badge in all_badges:
        if badge.milestone_type == "lesson_count" and completed_count >= badge.milestone_value:
            # Check if user already has this badge
            already_earned_query = select(models.UserBadge).where(
                models.UserBadge.user_id == user_id,
                models.UserBadge.badge_id == badge.badge_id
            )
            already_earned_res = await db.execute(already_earned_query)
            already_earned = already_earned_res.scalars().first()
            
            if not already_earned:
                # Award badge
                user_badge = models.UserBadge(
                    user_id=user_id,
                    badge_id=badge.badge_id,
                    date_awarded=datetime.utcnow()
                )
                db.add(user_badge)
                newly_earned_badge_name = badge.name
                
    return newly_earned_badge_name
