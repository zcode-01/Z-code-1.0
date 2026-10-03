"""
Z-Code Backend — Admin Router
Endpoints:
  GET  /api/admin/users          — list all users
  GET  /api/admin/stats          — platform-wide statistics
  PATCH /api/admin/users/{id}/admin — promote/demote admin
  DELETE /api/admin/users/{id}   — delete a user
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..database import get_db
from ..models import User, UserProfile, Course, Lesson, QuizAttempt, ChatMessage
from ..auth import get_admin_user

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/users")
async def list_users(
    _admin: Annotated[User, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List all registered users with their XP and level info."""
    result = await db.execute(
        select(User, UserProfile)
        .outerjoin(UserProfile, User.id == UserProfile.user_id)
        .order_by(User.created_at.desc())
    )
    rows = result.all()
    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_admin": user.is_admin,
            "created_at": user.created_at,
            "xp": profile.xp if profile else 0,
            "level": profile.level if profile else 1,
            "lessons_completed": profile.lessons_completed if profile else 0,
        }
        for user, profile in rows
    ]


@router.get("/stats")
async def platform_stats(
    _admin: Annotated[User, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Platform-wide statistics for the admin dashboard."""
    total_users = (await db.execute(select(func.count()).select_from(User))).scalar()
    total_courses = (await db.execute(select(func.count()).select_from(Course))).scalar()
    total_lessons = (await db.execute(select(func.count()).select_from(Lesson))).scalar()
    total_quiz_attempts = (await db.execute(select(func.count()).select_from(QuizAttempt))).scalar()
    total_ai_messages = (await db.execute(select(func.count()).select_from(ChatMessage))).scalar()

    # Total XP awarded
    total_xp = (await db.execute(select(func.sum(UserProfile.xp)))).scalar() or 0

    return {
        "total_users": total_users,
        "total_courses": total_courses,
        "total_lessons": total_lessons,
        "total_quiz_attempts": total_quiz_attempts,
        "total_ai_messages": total_ai_messages,
        "total_xp_awarded": total_xp,
    }


@router.patch("/users/{user_id}/admin")
async def toggle_admin(
    user_id: int,
    _admin: Annotated[User, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Promote or demote a user's admin status."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_admin = not user.is_admin
    await db.commit()
    return {"message": f"User {'promoted to' if user.is_admin else 'removed from'} admin", "is_admin": user.is_admin}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_admin: Annotated[User, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a user and all their data (cascade)."""
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted"}
