"""
Z-Code Backend — User & Profile Router
Endpoints: GET /api/users/profile, PATCH /api/users/profile, GET /api/users/stats
"""

from typing import Annotated
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models import User, UserProfile
from ..schemas import ProfileOut, ProfileUpdate
from ..auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])

# XP thresholds per level (level = index+1)
LEVEL_THRESHOLDS = [0, 500, 1000, 2000, 3500, 5000, 7500, 10000]
LEVEL_TITLES = [
    "Beginner", "Explorer", "Rising Learner", "Builder",
    "Developer", "Expert", "Master", "Legend"
]


def compute_level(xp: int) -> tuple[int, str]:
    """Return (level, level_title) based on XP."""
    level = 1
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if xp >= threshold:
            level = i + 1
    level = min(level, len(LEVEL_TITLES))
    return level, LEVEL_TITLES[level - 1]


async def get_or_create_profile(user_id: int, db: AsyncSession) -> UserProfile:
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile


@router.get("/profile", response_model=ProfileOut)
async def get_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get the current user's XP, streak, and level data."""
    profile = await get_or_create_profile(current_user.id, db)
    return profile


@router.patch("/profile")
async def update_profile(
    body: ProfileUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update user's display name or avatar letter."""
    if body.name is not None:
        current_user.name = body.name
    if body.avatar_letter is not None:
        current_user.avatar_letter = body.avatar_letter[0].upper()
    await db.commit()
    return {"message": "Profile updated"}


@router.get("/stats")
async def get_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Return dashboard stats: XP, streak, lessons completed, level, weekly XP.
    Also handles daily streak update logic.
    """
    profile = await get_or_create_profile(current_user.id, db)

    today = date.today().isoformat()
    if profile.last_activity_date != today:
        yesterday = (date.today().replace(day=date.today().day - 1)).isoformat() \
            if date.today().day > 1 else None
        if profile.last_activity_date == yesterday:
            profile.current_streak += 1
        elif profile.last_activity_date != today:
            profile.current_streak = 1
        profile.last_activity_date = today
        if profile.current_streak > profile.longest_streak:
            profile.longest_streak = profile.current_streak
        await db.commit()

    level, title = compute_level(profile.xp)
    next_level_xp = LEVEL_THRESHOLDS[min(level, len(LEVEL_THRESHOLDS) - 1)]

    return {
        "name": current_user.name,
        "avatar_letter": current_user.avatar_letter,
        "xp": profile.xp,
        "level": level,
        "level_title": title,
        "next_level_xp": next_level_xp,
        "current_streak": profile.current_streak,
        "longest_streak": profile.longest_streak,
        "lessons_completed": profile.lessons_completed,
        "exercises_done": profile.exercises_done,
        "weekly_xp": profile.weekly_xp,
    }


async def award_xp(user_id: int, xp: int, db: AsyncSession):
    """Helper — add XP to a user's profile and update their level."""
    profile = await get_or_create_profile(user_id, db)
    profile.xp += xp
    profile.weekly_xp += xp
    level, title = compute_level(profile.xp)
    profile.level = level
    profile.level_title = title
    await db.commit()
