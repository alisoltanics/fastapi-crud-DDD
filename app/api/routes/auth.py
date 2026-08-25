from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from app.api.deps import SessionDep
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import Token, Login
from app.schemas.user import UserCreate, UserPublic

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
def register(user_data: UserCreate, session: SessionDep):
    existing_user = session.exec(select(User).where(User.username == user_data.username)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    existing_email = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
):
    user = session.exec(select(User).where(User.username == form_data.username)).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.username)
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login/json", response_model=Token)
def login_json(user_data: Login, session: SessionDep):
    user = session.exec(select(User).where(User.username == user_data.username)).first()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.username)
    return Token(access_token=access_token, token_type="bearer")
