"""
Z-Code Backend — Quiz Router
Endpoints:
  GET  /api/quizzes/lesson/{lesson_id}  — fetch quiz for a lesson (questions, no answers)
  POST /api/quizzes/submit              — submit answers, get score + XP
  GET  /api/quizzes/history             — user's past quiz attempts
  POST /api/quizzes              [admin] — create a quiz with questions
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import Quiz, QuizQuestion, QuizAttempt, User
from ..schemas import QuizOut, QuizSubmit, QuizResult, QuizCreate, ChatHistoryItem
from ..auth import get_current_user, get_admin_user
from .users import award_xp

router = APIRouter(prefix="/api/quizzes", tags=["Quizzes"])


# ─────────────────────────────────────────────
# GET QUIZ FOR A LESSON
# ─────────────────────────────────────────────
@router.get("/lesson/{lesson_id}", response_model=QuizOut)
async def get_quiz(
    lesson_id: int,
    _user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Return the quiz for a lesson.
    Questions are returned WITHOUT the correct_option field
    so the frontend can't cheat by reading the response.
    """
    result = await db.execute(
        select(Quiz)
        .where(Quiz.lesson_id == lesson_id)
        .options(selectinload(Quiz.questions))
    )
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="No quiz found for this lesson")
    return quiz


# ─────────────────────────────────────────────
# SUBMIT QUIZ
# ─────────────────────────────────────────────
@router.post("/submit", response_model=QuizResult)
async def submit_quiz(
    body: QuizSubmit,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Score the submitted answers server-side.
    - If the user passes (score >= pass_score), awards XP.
    - Records the attempt in the DB.
    - Returns whether the user passed and how much XP was earned.
    """
    result = await db.execute(
        select(Quiz)
        .where(Quiz.id == body.quiz_id)
        .options(selectinload(Quiz.questions))
    )
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Build a map of question_id -> correct_option
    correct_map = {q.id: q.correct_option for q in quiz.questions}

    score = 0
    for answer in body.answers:
        if correct_map.get(answer.question_id) == answer.answer.lower():
            score += 1

    passed = score >= quiz.pass_score
    xp_earned = 0

    if passed:
        xp_earned = quiz.xp_reward
        await award_xp(current_user.id, xp_earned, db)
        message = f"🎉 Great job! You scored {score}/{len(quiz.questions)} and unlocked the next lesson!"
    else:
        message = f"You scored {score}/{len(quiz.questions)}. You need {quiz.pass_score} correct answers to pass. Try again!"

    # Save attempt
    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz.id,
        score=score,
        total=len(quiz.questions),
        passed=passed,
    )
    db.add(attempt)
    await db.commit()

    return QuizResult(
        score=score,
        total=len(quiz.questions),
        passed=passed,
        xp_earned=xp_earned,
        message=message,
    )


# ─────────────────────────────────────────────
# QUIZ HISTORY
# ─────────────────────────────────────────────
@router.get("/history")
async def quiz_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return the current user's past quiz attempts (most recent first)."""
    result = await db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.user_id == current_user.id)
        .order_by(QuizAttempt.attempted_at.desc())
        .limit(50)
    )
    attempts = result.scalars().all()
    return [
        {
            "quiz_id": a.quiz_id,
            "score": a.score,
            "total": a.total,
            "passed": a.passed,
            "attempted_at": a.attempted_at,
        }
        for a in attempts
    ]


# ─────────────────────────────────────────────
# ADMIN — CREATE QUIZ
# ─────────────────────────────────────────────
@router.post("", status_code=201)
async def create_quiz(
    body: QuizCreate,
    _admin: Annotated[User, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Admin only — create a quiz with questions for a lesson.

    Example body:
    {
      "lesson_id": 1,
      "pass_score": 4,
      "xp_reward": 100,
      "questions": [
        {
          "question_text": "Which language are you learning?",
          "option_a": "Python",
          "option_b": "Java",
          "option_c": "C++",
          "option_d": "HTML",
          "correct_option": "a"
        }
      ]
    }
    """
    quiz = Quiz(lesson_id=body.lesson_id, pass_score=body.pass_score, xp_reward=body.xp_reward)
    db.add(quiz)
    await db.flush()

    for i, q_data in enumerate(body.questions, start=1):
        question = QuizQuestion(
            quiz_id=quiz.id,
            order=i,
            question_text=q_data["question_text"],
            option_a=q_data["option_a"],
            option_b=q_data["option_b"],
            option_c=q_data["option_c"],
            option_d=q_data["option_d"],
            correct_option=q_data["correct_option"].lower(),
        )
        db.add(question)

    await db.commit()
    return {"message": "Quiz created", "quiz_id": quiz.id}
