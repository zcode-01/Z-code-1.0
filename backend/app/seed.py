"""
Z-Code Backend — Seed Script
Populates the database with initial course, lessons, and quiz data.
Run with: python -m app.seed  (from the backend/ directory)
"""

import asyncio
from .database import init_db, AsyncSessionLocal
from .models import Course, Lesson, Quiz, QuizQuestion, User, UserProfile
from .auth import hash_password


async def seed():
    print("🌱 Seeding Z-Code database...")
    await init_db()

    async with AsyncSessionLocal() as db:
        # ─── Admin User ──────────────────────────────
        # pyrefly: ignore [missing-import]
        from sqlalchemy import select
        existing_admin = await db.execute(select(User).where(User.email == "admin@zcode.dev"))
        if not existing_admin.scalar_one_or_none():
            admin = User(
                name="Admin",
                email="admin@zcode.dev",
                hashed_password=hash_password("admin123"),
                avatar_letter="A",
                is_admin=True,
            )
            db.add(admin)
            await db.flush()
            db.add(UserProfile(user_id=admin.id, xp=9999, level=8, level_title="Legend"))
            print("  ✓ Admin user created (admin@zcode.dev / admin123)")

        # ─── Demo Student ────────────────────────────
        existing_demo = await db.execute(select(User).where(User.email == "dhanush@zcode.dev"))
        if not existing_demo.scalar_one_or_none():
            demo = User(
                name="Dhanush",
                email="dhanush@zcode.dev",
                hashed_password=hash_password("demo123"),
                avatar_letter="D",
            )
            db.add(demo)
            await db.flush()
            db.add(UserProfile(user_id=demo.id, xp=1260, level=3, level_title="Rising Learner",
                               current_streak=5, lessons_completed=12, exercises_done=45, weekly_xp=50))
            print("  ✓ Demo user created (dhanush@zcode.dev / demo123)")

        # ─── Python Course ───────────────────────────
        existing_course = await db.execute(select(Course).where(Course.slug == "python"))
        if not existing_course.scalar_one_or_none():
            course = Course(
                slug="python",
                title="Python Programming",
                description="Master Python from the fundamentals to real-world programming.",
                difficulty="Beginner",
                duration_hours=12,
            )
            db.add(course)
            await db.flush()
            print("  ✓ Python course created")

            # Lessons
            lessons_data = [
                ("Introduction to Python", "Learn the basics of Python and write your first program.", 25, 50),
                ("Variables & Data Types", "Understand strings, numbers, booleans and variables.", 35, 60),
                ("Operators & Expressions", "Learn arithmetic, comparison and logical operators.", 40, 70),
                ("Conditional Statements", "Learn how to make decisions using if, elif and else.", 35, 70),
                ("Loops in Python", "Master for loops, while loops and iteration.", 45, 80),
                ("Functions", "Define reusable blocks of code with functions.", 50, 90),
                ("Lists & Tuples", "Work with ordered collections of data.", 40, 80),
                ("Dictionaries & Sets", "Store key-value pairs and unique collections.", 45, 85),
                ("File Handling", "Read from and write to files in Python.", 50, 90),
                ("Error Handling", "Handle exceptions gracefully with try/except.", 45, 90),
                ("Modules & Packages", "Organize code and use Python's standard library.", 55, 100),
                ("Final Project", "Build a real Python project from scratch.", 90, 150),
            ]

            lesson_objs = []
            for i, (title, desc, dur, xp) in enumerate(lessons_data, start=1):
                lesson = Lesson(
                    course_id=course.id, order=i, title=title,
                    description=desc, duration_minutes=dur, xp_reward=xp,
                )
                db.add(lesson)
                lesson_objs.append(lesson)

            await db.flush()
            print(f"  ✓ {len(lesson_objs)} lessons created")

            # Quiz for Lesson 1 (Introduction to Python)
            quiz = Quiz(lesson_id=lesson_objs[0].id, pass_score=4, xp_reward=100)
            db.add(quiz)
            await db.flush()

            questions = [
                ("Which language are you learning in this course?",
                 "Python", "Java", "C++", "HTML", "a"),
                ("Which symbol is used to create a comment in Python?",
                 "#", "//", "/*", "--", "a"),
                ("Which function displays output in Python?",
                 "print()", "display()", "show()", "output()", "a"),
                ("Which one is a valid Python variable name?",
                 "name", "2name", "my-name", "class", "a"),
                ("What type of value is \"Hello\"?",
                 "String", "Integer", "Boolean", "Float", "a"),
            ]
            for i, (text, a, b, c, d, correct) in enumerate(questions, start=1):
                db.add(QuizQuestion(
                    quiz_id=quiz.id, order=i,
                    question_text=text,
                    option_a=a, option_b=b, option_c=c, option_d=d,
                    correct_option=correct,
                ))
            print("  ✓ Introduction quiz created (5 questions)")

        await db.commit()
        print("\n✅ Seeding complete!")
        print("\nLogin credentials:")
        print("  Admin : admin@zcode.dev  / admin123")
        print("  Demo  : dhanush@zcode.dev / demo123")


if __name__ == "__main__":
    asyncio.run(seed())
