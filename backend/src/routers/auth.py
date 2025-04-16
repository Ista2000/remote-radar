import json
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import BaseModel

from ..utils import hash_password, verify_password
from ..constants import DEFAULT_TOKEN_EXPIRE_MINUTES
from ..deps import db_dependency
from ..models import User

load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

SECRET_KEY = str(os.getenv("AUTH_SECRET_KEY", ""))
ALGORITHM = str(os.getenv("AUTH_ALGORITHM", ""))


class UserCreateRequest(BaseModel):
    email: str
    password: str
    full_name: str
    experience_years: Optional[int] = None
    preferred_roles: list[str] = []
    preferred_locations: list[str] = []
    preferred_sources: list[str] = []
    receive_email_alerts: bool = False
    is_admin: bool = False
    resume_url: Optional[str] = None
    resume_text: Optional[str] = None
    resume_parsed: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


def authenticate_user(username: str, password: str, db) -> Optional[User]:
    """Authenticate user with username and password"""
    user: User = db.query(User).filter(User.email == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(
    email: str,
    expires_delta: timedelta = timedelta(minutes=DEFAULT_TOKEN_EXPIRE_MINUTES),
):
    """Create a JWT access token"""
    to_encode: dict[str, Any] = {"sub": email}
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreateRequest, db: db_dependency):
    """Create a new user"""
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        experience_years=user.experience_years,
        preferred_roles=json.dumps(user.preferred_roles),
        preferred_locations=json.dumps(user.preferred_locations),
        preferred_sources=json.dumps(user.preferred_sources),
        receive_email_alerts=user.receive_email_alerts,
        is_admin=user.is_admin,
        resume_url=user.resume_url,
        resume_text=user.resume_text,
        resume_parsed=user.resume_parsed,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    """Login user and return access token"""
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(email=user.email)
    return {"access_token": access_token, "token_type": "bearer"}
