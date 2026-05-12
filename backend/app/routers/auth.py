from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token, UserLogin
from app.services.auth import get_password_hash, verify_password, create_access_token
import logging

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).filter((User.email == user_in.email) | (User.username == user_in.username)))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    # Try finding by email first (as per frontend)
    result = await db.execute(select(User).filter(User.email == login_data.email))
    user = result.scalars().first()
    
    # Fallback to username if email didn't match (optional, but good for flexibility)
    if not user:
        result = await db.execute(select(User).filter(User.username == login_data.email))
        user = result.scalars().first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "username": user.username,
        "user_id": user.id
    }

@router.post("/refresh")
async def refresh_token(
    refresh_data: dict,
    db: AsyncSession = Depends(get_db)
):
    # In a real app, you would verify the refresh token properly
    # For now, we'll assume it's valid if provided (simple version for demo)
    user_id = refresh_data.get("user_id")
    if not user_id:
         raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    access_token = create_access_token(data={"sub": str(user_id)})
    return {"access_token": access_token}
