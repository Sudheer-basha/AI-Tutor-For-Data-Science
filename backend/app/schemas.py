import uuid
from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# --- User Schemas ---
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    user_id: uuid.UUID
    name: str
    email: str
    created_at: datetime
    streak_count: int
    last_active_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None


# --- Course & Lesson Schemas ---
class LessonOut(BaseModel):
    lesson_id: uuid.UUID
    title: str
    week_number: int
    month_number: int
    order_index: int
    status: str  # locked, unlocked, completed

    model_config = ConfigDict(from_attributes=True)

class LessonDetailOut(BaseModel):
    lesson_id: uuid.UUID
    course_id: uuid.UUID
    title: str
    content: str
    week_number: int
    month_number: int
    order_index: int
    status: str

    model_config = ConfigDict(from_attributes=True)


# --- Assignment Schemas ---
class AssignmentOut(BaseModel):
    assignment_id: uuid.UUID
    lesson_id: uuid.UUID
    title: str
    description: str
    type: str

    model_config = ConfigDict(from_attributes=True)

class AssignmentSubmissionIn(BaseModel):
    submission_content: str

class UserAssignmentOut(BaseModel):
    user_assignment_id: uuid.UUID
    user_id: uuid.UUID
    assignment_id: uuid.UUID
    submission_content: str
    score: Optional[int] = None
    feedback: Optional[str] = None
    status: str
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Quiz Schemas ---
class QuizQuestionOut(BaseModel):
    quiz_id: uuid.UUID
    question: str
    options: List[str]

    model_config = ConfigDict(from_attributes=True)

class QuizAnswerIn(BaseModel):
    quiz_id: uuid.UUID
    selected_option: str  # "A", "B", "C", "D"

class QuizSubmissionIn(BaseModel):
    answers: List[QuizAnswerIn]

class QuizSubmissionResultOut(BaseModel):
    score: int
    passed: bool
    correct_count: int
    total_count: int
    details: List[dict]  # List of {"quiz_id": ..., "correct": bool, "correct_option": ...}


# --- Badge Schemas ---
class BadgeOut(BaseModel):
    badge_id: uuid.UUID
    name: str
    description: str
    icon_svg: str
    date_awarded: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- Progress & Dashboard Schemas ---
class DashboardStats(BaseModel):
    lessons_completed: int
    assignments_completed: int
    avg_quiz_score: float
    streak_count: int
    total_badges: int

    model_config = ConfigDict(from_attributes=True)


# --- AI Chat Tutor Schemas ---
class ChatPromptIn(BaseModel):
    lesson_id: Optional[uuid.UUID] = None
    question: str

class ChatHistoryOut(BaseModel):
    chat_id: uuid.UUID
    question: str
    answer: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Certificate Schemas ---
class CertificateOut(BaseModel):
    certificate_id: uuid.UUID
    certificate_code: str
    issue_date: datetime
    name: str
    course_name: str

    model_config = ConfigDict(from_attributes=True)
