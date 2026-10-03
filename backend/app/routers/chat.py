"""
Z-Code Backend — AI Chat Router (Gemini)
Endpoints:
  POST /api/chat          — send a message, get an AI reply
  GET  /api/chat/history  — fetch the user's recent chat history
  DELETE /api/chat/history — clear the user's chat history
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from ..database import get_db
from ..models import ChatMessage, User
from ..schemas import ChatRequest, ChatResponse, ChatHistoryItem
from ..auth import get_current_user
from ..config import settings

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


async def call_gemini(user_message: str, history: list[dict]) -> str:
    """
    Call Google Gemini API with the conversation history.
    Returns the AI's text reply.
    """
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your-gemini-api-key-here":
        # Fallback mock response if API key isn't set
        return (
            "🤖 Z-Code AI is not configured yet. Please set your GEMINI_API_KEY in the backend/.env file. "
            "Get a free API key at https://makersuite.google.com/app/apikey"
        )

    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT,
        )

        # Build chat history for Gemini
        gemini_history = []
        for msg in history[-10:]:  # last 10 messages for context
            gemini_history.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [msg["content"]],
            })

        chat = model.start_chat(history=gemini_history)
        response = await chat.send_message_async(user_message)
        return response.text

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


@router.post("", response_model=ChatResponse)
async def send_message(
    body: ChatRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Send a message to Z-Code AI.
    - Loads recent chat history for context
    - Calls Gemini API
    - Saves both user message and AI reply to DB
    """
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

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
    reply = await call_gemini(body.message, history)

    # Save user message
    user_msg = ChatMessage(user_id=current_user.id, role="user", content=body.message)
    db.add(user_msg)

    # Save AI reply
    ai_msg = ChatMessage(user_id=current_user.id, role="assistant", content=reply)
    db.add(ai_msg)

    await db.commit()
    return ChatResponse(reply=reply)


@router.get("/history", response_model=list[ChatHistoryItem])
async def get_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return the user's last 50 chat messages (oldest first)."""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.sent_at.asc())
        .limit(50)
    )
    return result.scalars().all()


@router.delete("/history")
async def clear_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Clear the current user's entire chat history."""
    await db.execute(delete(ChatMessage).where(ChatMessage.user_id == current_user.id))
    await db.commit()
    return {"message": "Chat history cleared"}
