"""
Z-Code Backend — ORM Models
All SQLAlchemy table definitions live here.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Integer, String, Boolean, Float, DateTime,
    ForeignKey, Text, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ─────────────────────────────────────────────
# USER
# ─────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    avatar_letter: Mapped[str] = mapped_column(String(1), default="Z")
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Relationships
    profile: Mapped["UserProfile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    progress: Mapped[list["LessonProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    chat_history: Mapped[list["ChatMessage"]] = relationship(back_populates="user", cascade="all, delete-orphan")


# ─────────────────────────────────────────────
# USER PROFILE (XP, Streaks, Level)
# ─────────────────────────────────────────────
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    level_title: Mapped[str] = mapped_column(String(50), default="Beginner")
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_activity_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    lessons_completed: Mapped[int] = mapped_column(Integer, default=0)
    exercises_done: Mapped[int] = mapped_column(Integer, default=0)
    weekly_xp: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["User"] = relationship(back_populates="profile")


# ─────────────────────────────────────────────
# COURSE
# ─────────────────────────────────────────────
class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    difficulty: Mapped[str] = mapped_column(String(20), default="Beginner")
    duration_hours: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    lessons: Mapped[list["Lesson"]] = relationship(back_populates="course", cascade="all, delete-orphan", order_by="Lesson.order")


# ─────────────────────────────────────────────
# LESSON
# ─────────────────────────────────────────────
class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    order: Mapped[int] = mapped_column(Integer, default=1)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    xp_reward: Mapped[int] = mapped_column(Integer, default=50)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)

    course: Mapped["Course"] = relationship(back_populates="lessons")
    progress: Mapped[list["LessonProgress"]] = relationship(back_populates="lesson", cascade="all, delete-orphan")
    quiz: Mapped["Quiz | None"] = relationship(back_populates="lesson", uselist=False, cascade="all, delete-orphan")


# ─────────────────────────────────────────────
# LESSON PROGRESS
# ─────────────────────────────────────────────
class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"))
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="progress")
    lesson: Mapped["Lesson"] = relationship(back_populates="progress")


# ─────────────────────────────────────────────
# QUIZ
# ─────────────────────────────────────────────
class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), unique=True)
    pass_score: Mapped[int] = mapped_column(Integer, default=4)  # out of total questions
    xp_reward: Mapped[int] = mapped_column(Integer, default=100)

    lesson: Mapped["Lesson"] = relationship(back_populates="quiz")
    questions: Mapped[list["QuizQuestion"]] = relationship(back_populates="quiz", cascade="all, delete-orphan", order_by="QuizQuestion.order")
    attempts: Mapped[list["QuizAttempt"]] = relationship(back_populates="quiz", cascade="all, delete-orphan")


# ─────────────────────────────────────────────
# QUIZ QUESTION
# ─────────────────────────────────────────────
class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"))
    order: Mapped[int] = mapped_column(Integer, default=1)
    question_text: Mapped[str] = mapped_column(Text)
    option_a: Mapped[str] = mapped_column(String(300))
    option_b: Mapped[str] = mapped_column(String(300))
    option_c: Mapped[str] = mapped_column(String(300))
    option_d: Mapped[str] = mapped_column(String(300))
    correct_option: Mapped[str] = mapped_column(String(1))  # "a", "b", "c", or "d"

    quiz: Mapped["Quiz"] = relationship(back_populates="questions")


# ─────────────────────────────────────────────
# QUIZ ATTEMPT
# ─────────────────────────────────────────────
class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"))
    score: Mapped[int] = mapped_column(Integer, default=0)
    total: Mapped[int] = mapped_column(Integer, default=5)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="quiz_attempts")
    quiz: Mapped["Quiz"] = relationship(back_populates="attempts")


# ─────────────────────────────────────────────
# AI CHAT MESSAGE
# ─────────────────────────────────────────────
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    role: Mapped[str] = mapped_column(String(10))   # "user" or "assistant"
    content: Mapped[str] = mapped_column(Text)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="chat_history")
