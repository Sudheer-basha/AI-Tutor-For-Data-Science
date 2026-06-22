from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app import models, schemas

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_data: schemas.UserRegister, db: AsyncSession = Depends(get_db)):
    # Check if user already exists
    email_query = select(models.User).where(models.User.email == user_data.email)
    result = await db.execute(email_query)
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_pwd = get_password_hash(user_data.password)
    new_user = models.User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_pwd,
        streak_count=1,
        last_active_date=datetime.utcnow().date()
    )
    db.add(new_user)
    await db.flush() # Flush to populate user_id
    
    # Initialize lesson progress sequence
    lessons_query = select(models.Lesson).order_by(models.Lesson.order_index)
    lessons_result = await db.execute(lessons_query)
    lessons = lessons_result.scalars().all()
    
    for index, lesson in enumerate(lessons):
        # First lesson is unlocked by default, rest are locked
        status_val = "unlocked" if index == 0 else "locked"
        unlocked_time = datetime.utcnow() if index == 0 else None
        
        progress_record = models.Progress(
            user_id=new_user.user_id,
            lesson_id=lesson.lesson_id,
            status=status_val,
            unlocked_at=unlocked_time
        )
        db.add(progress_record)
        
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    query = select(models.User).where(models.User.email == form_data.username)
    result = await db.execute(query)
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Update user active date and streak
    today = datetime.utcnow().date()
    if user.last_active_date:
        delta = today - user.last_active_date
        if delta.days == 1:
            # Active yesterday, increment streak
            user.streak_count += 1
        elif delta.days > 1:
            # Streak broken, reset
            user.streak_count = 1
    else:
        user.streak_count = 1
        
    user.last_active_date = today
    db.add(user)
    await db.commit()
    
    # Generate token
    access_token = create_access_token(data={"sub": str(user.user_id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserOut)
async def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user
