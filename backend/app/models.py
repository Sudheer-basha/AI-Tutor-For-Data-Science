import uuid
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import ForeignKey, DateTime, Date, String, Text, Integer, Boolean, JSON, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Gamification and tracking
    streak_count: Mapped[int] = mapped_column(Integer, default=1)
    last_active_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationships
    progress: Mapped[List["Progress"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    submissions: Mapped[List["UserAssignment"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    quizzes: Mapped[List["UserQuiz"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    badges: Mapped[List["UserBadge"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    chats: Mapped[List["ChatHistory"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    certificate: Mapped[Optional["Certificate"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"
    
    course_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    lessons: Mapped[List["Lesson"]] = relationship(back_populates="course", cascade="all, delete-orphan")


class Lesson(Base):
    __tablename__ = "lessons"
    
    lesson_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    course_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("courses.course_id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)  # Detailed course material (Markdown)
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    month_number: Mapped[int] = mapped_column(Integer, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)  # Enforce progression order

    # Relationships
    course: Mapped["Course"] = relationship(back_populates="lessons")
    assignments: Mapped[List["Assignment"]] = relationship(back_populates="lesson", cascade="all, delete-orphan")
    quizzes: Mapped[List["Quiz"]] = relationship(back_populates="lesson", cascade="all, delete-orphan")
    progress: Mapped[List["Progress"]] = relationship(back_populates="lesson", cascade="all, delete-orphan")


class Assignment(Base):
    __tablename__ = "assignments"
    
    assignment_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    lesson_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("lessons.lesson_id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)  # Instructions / requirements / starter code
    type: Mapped[str] = mapped_column(String(50), default="coding")  # coding, project
    
    # Relationships
    lesson: Mapped["Lesson"] = relationship(back_populates="assignments")
    submissions: Mapped[List["UserAssignment"]] = relationship(back_populates="assignment", cascade="all, delete-orphan")


class UserAssignment(Base):
    __tablename__ = "user_assignments"
    
    user_assignment_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.user_id"), nullable=False)
    assignment_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("assignments.assignment_id"), nullable=False)
    submission_content: Mapped[str] = mapped_column(Text, nullable=False)  # Code submitted by student
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Set by AI Evaluation
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # AI detailed feedback
    status: Mapped[str] = mapped_column(String(50), default="submitted")  # submitted, passed, failed
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="submissions")
    assignment: Mapped["Assignment"] = relationship(back_populates="submissions")


class Quiz(Base):
    __tablename__ = "quizzes"
    
    quiz_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    lesson_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("lessons.lesson_id"), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list] = mapped_column(JSON, nullable=False)  # list of strings (A, B, C, D text)
    correct_option: Mapped[str] = mapped_column(String(10), nullable=False)  # "A", "B", "C", or "D"

    # Relationships
    lesson: Mapped["Lesson"] = relationship(back_populates="quizzes")


class UserQuiz(Base):
    __tablename__ = "user_quizzes"
    
    user_quiz_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.user_id"), nullable=False)
    lesson_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("lessons.lesson_id"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)  # Quiz score percentage (e.g. 80 for 80%)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="quizzes")


class Badge(Base):
    __tablename__ = "badges"
    
    badge_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    milestone_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'lesson_count', 'badge_specific'
    milestone_value: Mapped[int] = mapped_column(Integer, default=0)
    icon_svg: Mapped[str] = mapped_column(Text, nullable=False)  # SVG path/XML to display in frontend

    # Relationships
    earned_by: Mapped[List["UserBadge"]] = relationship(back_populates="badge", cascade="all, delete-orphan")


class UserBadge(Base):
    __tablename__ = "user_badges"
    
    user_badge_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.user_id"), nullable=False)
    badge_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("badges.badge_id"), nullable=False)
    date_awarded: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="badges")
    badge: Mapped["Badge"] = relationship(back_populates="earned_by")


class Progress(Base):
    __tablename__ = "progress"
    
    progress_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.user_id"), nullable=False)
    lesson_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("lessons.lesson_id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="locked")  # locked, unlocked, completed
    unlocked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="progress")
    lesson: Mapped["Lesson"] = relationship(back_populates="progress")


class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    chat_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.user_id"), nullable=False)
    lesson_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("lessons.lesson_id"), nullable=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="chats")


class Certificate(Base):
    __tablename__ = "certificates"
    
    certificate_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.user_id"), unique=True, nullable=False)
    certificate_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    issue_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="certificate")
