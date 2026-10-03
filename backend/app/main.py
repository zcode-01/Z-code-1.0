"""
Z-Code Backend — Main FastAPI Application
Entry point: uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager
# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .config import settings
from .routers import auth, users, courses, quizzes, chat, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run on startup: create DB tables."""
    await init_db()
    yield


app = FastAPI(
    title="Z-Code API",
    description="Backend for the Z-Code learning platform — courses, quizzes, XP, streaks & AI tutor.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",      # Swagger UI  → http://localhost:8000/api/docs
    redoc_url="/api/redoc",    # ReDoc       → http://localhost:8000/api/redoc
)

# ─── CORS ───────────────────────────────────────────────────────────────────
# Allow the HTML files to call the API even when opened from the filesystem.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=r".*",   # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── ROUTERS ────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(quizzes.router)
app.include_router(chat.router)
app.include_router(admin.router)


# ─── HEALTH CHECK ───────────────────────────────────────────────────────────
@app.get("/api/health", tags=["Health"])
async def health():
    """Simple health check — returns 200 if the server is running."""
    return {"status": "ok", "version": "1.0.0", "platform": "Z-Code"}
