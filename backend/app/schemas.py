"""
Z-Code Backend — Pydantic Schemas
Request & response shapes for all API endpoints.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────
class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None


# ─────────────────────────────────────────────
# USER
# ─────────────────────────────────────────────
class UserOut(BaseModel):
    id: int
    name: str
    email: str
    avatar_letter: str
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────
# USER PROFILE
# ─────────────────────────────────────────────
class ProfileOut(BaseModel):
    xp: int
    level: int
    level_title: str
    current_streak: int
    longest_streak: int
    lessons_completed: int
    exercises_done: int
    weekly_xp: int

    model_config = {"from_attributes": True}


class ProfileUpdate(BaseModel):
    name: str | None = None
    avatar_letter: str | None = None


# ─────────────────────────────────────────────
# COURSE
# ─────────────────────────────────────────────
class CourseOut(BaseModel):
    id: int
    slug: str
    title: str
    description: str
    difficulty: str
    duration_hours: int
    is_published: bool

    model_config = {"from_attributes": True}


class CourseCreate(BaseModel):
    slug: str
    title: str
    description: str = ""
    difficulty: str = "Beginner"
    duration_hours: int = 0


# ─────────────────────────────────────────────
# LESSON
# ─────────────────────────────────────────────
class LessonOut(BaseModel):
    id: int
    course_id: int
    order: int
    title: str
    description: str
    duration_minutes: int
    xp_reward: int
    is_published: bool
    completed: bool = False   # injected per-user

    model_config = {"from_attributes": True}


class LessonCreate(BaseModel):
    course_id: int
    order: int
    title: str
    description: str = ""
    duration_minutes: int = 30
    xp_reward: int = 50


# ─────────────────────────────────────────────
# PROGRESS
# ─────────────────────────────────────────────
class ProgressResponse(BaseModel):
    course_id: int
    total_lessons: int
    completed_lessons: int
    percent: float


class CompleteLesson(BaseModel):
    lesson_id: int


# ─────────────────────────────────────────────
# QUIZ
# ─────────────────────────────────────────────
class QuestionOut(BaseModel):
    id: int
    order: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    # correct_option is NOT returned to the frontend

    model_config = {"from_attributes": True}


class QuizOut(BaseModel):
    id: int
    lesson_id: int
    pass_score: int
    xp_reward: int
    questions: list[QuestionOut]

    model_config = {"from_attributes": True}


class QuizAnswer(BaseModel):
    question_id: int
    answer: str   # "a", "b", "c", or "d"


class QuizSubmit(BaseModel):
    quiz_id: int
    answers: list[QuizAnswer]


class QuizResult(BaseModel):
    score: int
    total: int
    passed: bool
    xp_earned: int
    message: str


class QuizCreate(BaseModel):
    lesson_id: int
    pass_score: int = 4
    xp_reward: int = 100
    questions: list[dict]   # [{question_text, option_a..d, correct_option}]


# ─────────────────────────────────────────────
# AI CHAT
# ─────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


class ChatHistoryItem(BaseModel):
    role: str
    content: str
    sent_at: datetime

    model_config = {"from_attributes": True}
