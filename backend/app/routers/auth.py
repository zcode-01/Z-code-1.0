"""
Z-Code Backend — Auth Router
Endpoints: POST /api/auth/signup, POST /api/auth/login, GET /api/auth/me
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models import User, UserProfile
from ..schemas import SignupRequest, LoginRequest, Token, UserOut
from ..auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/signup", response_model=Token, status_code=201)
async def signup(body: SignupRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Register a new user.
    - Checks for duplicate email
    - Hashes the password
    - Creates a UserProfile with default XP/streak values
    - Returns a JWT
    """
    # Check duplicate email
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        name=body.name,
        email=body.email,
        hashed_password=hash_password(body.password),
        avatar_letter=body.name[0].upper() if body.name else "Z",
    )
    db.add(user)
    await db.flush()  # get user.id without committing

    # Create default profile
    profile = UserProfile(user_id=user.id)
    db.add(profile)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(user.id)
    return Token(access_token=token)


@router.post("/login", response_model=Token)
async def login(body: LoginRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Authenticate an existing user.
    Returns a JWT on success, or 401 on bad credentials.
    """
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_access_token(user.id)
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Return the currently authenticated user's info."""
    return current_user
