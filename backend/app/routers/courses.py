"""
Z-Code Backend — Courses & Lessons Router
Endpoints:
  GET  /api/courses                   — list all published courses
  GET  /api/courses/{slug}            — course detail + lessons (with per-user completion)
  GET  /api/courses/{slug}/progress   — user's progress % for a course
  POST /api/courses/{slug}/complete   — mark a lesson as completed (awards XP)
  POST /api/courses         [admin]   — create a course
  POST /api/lessons         [admin]   — create a lesson
"""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import Course, Lesson, LessonProgress, UserProfile
from ..schemas import CourseOut, LessonOut, ProgressResponse, CompleteLesson, CourseCreate, LessonCreate
from ..auth import get_current_user, get_admin_user
from ..models import User
from .users import award_xp, get_or_create_profile

router = APIRouter(prefix="/api", tags=["Courses"])


# ─────────────────────────────────────────────
# LIST COURSES
# ─────────────────────────────────────────────
@router.get("/courses", response_model=list[CourseOut])
async def list_courses(db: Annotated[AsyncSession, Depends(get_db)]):
    """Return all published courses (no auth required)."""
    result = await db.execute(select(Course).where(Course.is_published == True))
    return result.scalars().all()


# ─────────────────────────────────────────────
# COURSE DETAIL + LESSONS
# ─────────────────────────────────────────────
@router.get("/courses/{slug}")
async def get_course(
    slug: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Return course info plus all lessons, each annotated with
    whether the current user has completed it.
    """
    result = await db.execute(
        select(Course)
        .where(Course.slug == slug, Course.is_published == True)
        .options(selectinload(Course.lessons))
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Fetch user's completed lesson IDs for this course
    lesson_ids = [l.id for l in course.lessons]
    progress_result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id.in_(lesson_ids),
            LessonProgress.completed == True,
        )
    )
    completed_ids = {p.lesson_id for p in progress_result.scalars().all()}

    lessons_out = []
    for lesson in sorted(course.lessons, key=lambda l: l.order):
        data = LessonOut.model_validate(lesson)
        data.completed = lesson.id in completed_ids
        lessons_out.append(data)

    return {
        "id": course.id,
        "slug": course.slug,
        "title": course.title,
        "description": course.description,
        "difficulty": course.difficulty,
        "duration_hours": course.duration_hours,
        "total_lessons": len(lessons_out),
        "completed_lessons": len(completed_ids),
        "lessons": [l.model_dump() for l in lessons_out],
    }


# ─────────────────────────────────────────────
# COURSE PROGRESS
# ─────────────────────────────────────────────
@router.get("/courses/{slug}/progress", response_model=ProgressResponse)
async def get_progress(
    slug: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Course).where(Course.slug == slug).options(selectinload(Course.lessons))
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    lesson_ids = [l.id for l in course.lessons]
    if not lesson_ids:
        return ProgressResponse(course_id=course.id, total_lessons=0, completed_lessons=0, percent=0.0)

    progress_result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id.in_(lesson_ids),
            LessonProgress.completed == True,
        )
    )
    completed = progress_result.scalars().all()
    total = len(lesson_ids)
    done = len(completed)
    return ProgressResponse(
        course_id=course.id,
        total_lessons=total,
        completed_lessons=done,
        percent=round((done / total) * 100, 1) if total else 0.0,
    )


# ─────────────────────────────────────────────
# COMPLETE A LESSON
# ─────────────────────────────────────────────
@router.post("/courses/{slug}/complete")
async def complete_lesson(
    slug: str,
    body: CompleteLesson,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Mark a lesson as completed for the current user.
    Awards XP only once (idempotent — safe to call multiple times).
    """
    # Verify lesson belongs to the course
    result = await db.execute(
        select(Lesson)
        .join(Course, Lesson.course_id == Course.id)
        .where(Course.slug == slug, Lesson.id == body.lesson_id)
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found in this course")

    # Upsert progress
    prog_result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id == body.lesson_id,
        )
    )
    progress = prog_result.scalar_one_or_none()

    xp_awarded = 0
    if progress and progress.completed:
        return {"message": "Already completed", "xp_earned": 0}

    if not progress:
        progress = LessonProgress(user_id=current_user.id, lesson_id=body.lesson_id)
        db.add(progress)

    progress.completed = True
    progress.completed_at = datetime.now(timezone.utc)
    await db.flush()

    # Award XP & update lesson count
    await award_xp(current_user.id, lesson.xp_reward, db)
    profile = await get_or_create_profile(current_user.id, db)
    profile.lessons_completed += 1
    xp_awarded = lesson.xp_reward

    await db.commit()
    return {"message": "Lesson completed!", "xp_earned": xp_awarded}


# ─────────────────────────────────────────────
# ADMIN — CREATE COURSE
# ─────────────────────────────────────────────
@router.post("/courses", status_code=201, response_model=CourseOut)
async def create_course(
    body: CourseCreate,
    _admin: Annotated[User, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Admin only — create a new course."""
    existing = await db.execute(select(Course).where(Course.slug == body.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Course slug already exists")
    course = Course(**body.model_dump())
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


# ─────────────────────────────────────────────
# ADMIN — CREATE LESSON
# ─────────────────────────────────────────────
@router.post("/lessons", status_code=201, response_model=LessonOut)
async def create_lesson(
    body: LessonCreate,
    _admin: Annotated[User, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Admin only — add a lesson to a course."""
    lesson = Lesson(**body.model_dump())
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    result = LessonOut.model_validate(lesson)
    return result
