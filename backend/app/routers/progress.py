from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_user
from app import models, schemas

router = APIRouter(prefix="/progress", tags=["Progress & Badges"])

@router.get("/stats", response_model=schemas.DashboardStats)
async def get_dashboard_stats(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Computes summary analytics for the student's dashboard.
    """
    user_id = current_user.user_id

    # 1. Lessons completed count
    completed_lessons_query = select(func.count(models.Progress.progress_id)).where(
        models.Progress.user_id == user_id,
        models.Progress.status == "completed"
    )
    completed_lessons_res = await db.execute(completed_lessons_query)
    lessons_completed = completed_lessons_res.scalar() or 0

    # 2. Assignments completed count (passed submissions)
    passed_assignments_query = select(func.count(models.UserAssignment.user_assignment_id)).where(
        models.UserAssignment.user_id == user_id,
        models.UserAssignment.status == "passed"
    )
    passed_assignments_res = await db.execute(passed_assignments_query)
    assignments_completed = passed_assignments_res.scalar() or 0

    # 3. Average quiz score
    avg_quiz_score_query = select(func.avg(models.UserQuiz.score)).where(
        models.UserQuiz.user_id == user_id
    )
    avg_quiz_score_res = await db.execute(avg_quiz_score_query)
    avg_quiz_score = avg_quiz_score_res.scalar()
    # Handle None
    avg_quiz_score = float(avg_quiz_score) if avg_quiz_score is not None else 0.0

    # 4. Total badges count
    badges_count_query = select(func.count(models.UserBadge.user_badge_id)).where(
        models.UserBadge.user_id == user_id
    )
    badges_count_res = await db.execute(badges_count_query)
    total_badges = badges_count_res.scalar() or 0

    return schemas.DashboardStats(
        lessons_completed=lessons_completed,
        assignments_completed=assignments_completed,
        avg_quiz_score=round(avg_quiz_score, 1),
        streak_count=current_user.streak_count,
        total_badges=total_badges
    )


@router.get("/badges", response_model=List[schemas.BadgeOut])
async def list_user_badges(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lists all available badges in the system, showing the award date if the current user has earned them.
    """
    # Query all badges and left join user earned badges
    query = (
        select(models.Badge, models.UserBadge.date_awarded)
        .outerjoin(
            models.UserBadge,
            (models.UserBadge.badge_id == models.Badge.badge_id) & 
            (models.UserBadge.user_id == current_user.user_id)
        )
    )
    result = await db.execute(query)
    
    badge_list = []
    for badge, date_awarded in result.all():
        badge_list.append(
            schemas.BadgeOut(
                badge_id=badge.badge_id,
                name=badge.name,
                description=badge.description,
                icon_svg=badge.icon_svg,
                date_awarded=date_awarded
            )
        )
    return badge_list
