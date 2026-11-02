"""
Z-Code Backend — AI Chat Router (NVIDIA Nemotron 3 & Gemini Fallback)
Endpoints:
  POST /api/chat          — send a message, get an AI reply
  GET  /api/chat/history  — fetch the user's recent chat history
  DELETE /api/chat/history — clear the user's chat history
"""

from typing import Annotated
import logging
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from ..database import get_db
from ..models import ChatMessage, User
from ..schemas import ChatRequest, ChatResponse, ChatHistoryItem
from ..auth import get_current_user, get_optional_current_user
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["AI Chat"])

# System prompt — defines Z-Code AI's personality
SYSTEM_PROMPT = """You are Z-Code AI, a friendly and encouraging coding tutor for the Z-Code learning platform.

Your role:
- Help students learn Python programming (and other languages)
- Explain programming concepts in simple, clear terms
- Encourage students when they're stuck
- Provide short code examples when helpful
- Keep answers concise and easy to understand for beginners
- Stay focused on coding/programming topics

Z-Code Platform features:
- Structured courses (Python, JavaScript, etc.)
- Lessons with quizzes to unlock the next chapter
- XP and leveling system to gamify learning
- Streak tracking for daily motivation

Always be warm, supportive, and encouraging. If someone is confused, reassure them that it's normal and that they'll get it with practice."""


async def call_nvidia(user_message: str, history: list[dict]) -> tuple[str, str | None]:
    """
    Call NVIDIA API (Nemotron 3 Ultra) with conversation history.
    Returns (reply_text, reasoning_text).
    """
    if not settings.NVIDIA_API_KEY:
        raise ValueError("NVIDIA_API_KEY is not configured")

    headers = {
        "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
        "Content-Type": "application/json",
    }

    # Format messages array: system prompt first, then recent conversation history, then latest user message
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history[-10:]:
        role = "assistant" if msg["role"] in ("assistant", "model") else "user"
        messages.append({"role": role, "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": settings.NVIDIA_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 4096,
        "chat_template_kwargs": {"enable_thinking": True},
        "stream": False,
    }

    url = f"{settings.NVIDIA_BASE_URL.rstrip('/')}/chat/completions"

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"NVIDIA API error ({response.status_code}): {response.text}",
            )
        data = response.json()

    choices = data.get("choices", [])
    if not choices:
        raise HTTPException(status_code=500, detail="No response choices returned by NVIDIA AI service.")

    choice_msg = choices[0].get("message", {})
    reply = choice_msg.get("content") or ""
    reasoning = choice_msg.get("reasoning_content")

    if not reply.strip() and reasoning:
        reply = reasoning

    return reply.strip(), reasoning


async def call_gemini(user_message: str, history: list[dict]) -> str:
    """
    Fallback: Call Google Gemini API with the conversation history.
    """
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your-gemini-api-key-here":
        raise ValueError("GEMINI_API_KEY is not configured")

    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT,
        )

        gemini_history = []
        for msg in history[-10:]:
            gemini_history.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [msg["content"]],
            })

        chat = model.start_chat(history=gemini_history)
        response = await chat.send_message_async(user_message)
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini AI service error: {str(e)}")


async def get_ai_reply(user_message: str, history: list[dict]) -> tuple[str, str | None, str]:
    """
    Selects the best available AI provider:
    1. NVIDIA NIM (Nemotron 3 Ultra)
    2. Google Gemini (fallback)
    Returns (reply, reasoning, model_name).
    """
    # 1. NVIDIA AI
    if settings.NVIDIA_API_KEY and settings.NVIDIA_API_KEY != "your-nvidia-api-key-here":
        try:
            reply, reasoning = await call_nvidia(user_message, history)
            return reply, reasoning, settings.NVIDIA_MODEL
        except Exception as e:
            logger.warning("NVIDIA AI call failed: %s. Checking for fallback...", e)
            # If Gemini is configured, fall back to it
            if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key-here":
                gemini_reply = await call_gemini(user_message, history)
                return gemini_reply, None, "gemini-1.5-flash"
            # Otherwise re-raise
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

    # 2. Gemini fallback if NVIDIA key is not set
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key-here":
        gemini_reply = await call_gemini(user_message, history)
        return gemini_reply, None, "gemini-1.5-flash"

    # 3. Not configured
    return (
        "🤖 Z-Code AI is not configured yet. Please configure your NVIDIA_API_KEY in the backend/.env file.",
        None,
        "none",
    )


@router.post("", response_model=ChatResponse)
async def send_message(
    body: ChatRequest,
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Send a message to Z-Code AI.
    - Works for both logged-in users and guests (never returns 401)
    - Loads recent chat history for context (if logged in)
    - Calls NVIDIA Nemotron 3 Ultra (or fallback)
    - Saves user message and AI reply to DB (if logged in)
    """
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    history = []
    if current_user is not None:
        # Load recent history for context
        history_result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.user_id == current_user.id)
            .order_by(ChatMessage.sent_at.desc())
            .limit(10)
        )
        recent = list(reversed(history_result.scalars().all()))
        history = [{"role": m.role, "content": m.content} for m in recent]

    # Get AI reply
    reply, reasoning, model_used = await get_ai_reply(body.message, history)

    if current_user is not None:
        user_msg = ChatMessage(user_id=current_user.id, role="user", content=body.message)
        db.add(user_msg)
        ai_msg = ChatMessage(user_id=current_user.id, role="assistant", content=reply)
        db.add(ai_msg)
        await db.commit()

    return ChatResponse(reply=reply, reasoning=reasoning, model=model_used)


@router.get("/history", response_model=list[ChatHistoryItem])
async def get_history(
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return the user's last 50 chat messages (oldest first). Returns empty list for guests."""
    if current_user is None:
        return []
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.sent_at.asc())
        .limit(50)
    )
    return result.scalars().all()


@router.delete("/history")
async def clear_history(
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Clear the current user's entire chat history."""
    if current_user is not None:
        await db.execute(delete(ChatMessage).where(ChatMessage.user_id == current_user.id))
        await db.commit()
    return {"message": "Chat history cleared"}
