from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

import httpx

from schemas.schemas import (
    UserCreate, UserLogin, ShowUsers, ResetPasswordRequest,
    ResetPasswordConfirm, GoogleToken, TokenData
)
from models import User
from core.db import db_dependency
from utils.auth import hash_password, verify_password, generate_token, get_current_user

router = APIRouter()


@router.post("/register", response_model=ShowUsers)
async def register(user: UserCreate, db: db_dependency):
    result = await db.execute(select(User).filter(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login")
async def login(user: UserLogin, db: db_dependency):
    result = await db.execute(select(User).filter(User.email == user.email))
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid Email or password")

    access_token = generate_token({
        "sub": db_user.email,
        "user_id": db_user.id
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/token")
async def login_for_access_token(
    db: db_dependency,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    result = await db.execute(select(User).filter(User.email == form_data.username))
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid Email or password")

    access_token = generate_token({
        "sub": db_user.email,
        "user_id": db_user.id
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/profile", response_model=ShowUsers)
async def get_profile(db: db_dependency, user: TokenData = Depends(get_current_user)):
    result = await db.execute(select(User).filter(User.email == user.username))
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user


@router.post("/forgot-password")
async def forgot_password(db: db_dependency, user: ResetPasswordRequest):
    result = await db.execute(select(User).filter(User.email == user.email))
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail="Email not found")

    reset_token = generate_token(data={"sub": db_user.email})

    return {
        "message": "Reset token generated successfully",
        "reset_token": reset_token
    }


@router.post("/reset-password")
async def reset_password(db: db_dependency, data: ResetPasswordConfirm):
    result = await db.execute(select(User).filter(User.email == data.email))
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.password = hash_password(data.new_password)
    await db.commit()

    return {"message": "Password has been reset successfully"}


@router.post("/google-auth")
async def google_login(db: db_dependency, token_data: GoogleToken):
    id_token = token_data.id_token

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}")
            google_resp = response.json()

        if "email" not in google_resp:
            raise HTTPException(status_code=400, detail="Invalid Google token")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google token verification failed: {str(e)}")

    result = await db.execute(select(User).filter(User.email == google_resp["email"]))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            username=google_resp.get("name", "googleuser"),
            email=google_resp["email"],
            password="dummy"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    access_token = generate_token({
        "sub": user.email,
        "user_id": user.id
    })

    return {
        "access_token": access_token,
        "user": {"username": user.username, "email": user.email},
        "token_type": "bearer"
    }
