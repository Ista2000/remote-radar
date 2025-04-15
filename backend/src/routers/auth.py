from datetime import datetime, timedelta, timezone
import json
from typing import Annotated
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
import os
from ..models import User
from ..constants import DEFAULT_TOKEN_EXPIRE_MINUTES
from ..deps import bcrypt_context, db_dependency

load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

SECRET_KEY = os.getenv("AUTH_SECRET_KEY")
ALGORITHM = os.getenv("AUTH_ALGORITHM")

class UserCreateRequest(BaseModel):
    email: str
    password: str
    full_name: str
    experience_years: int = None
    preferred_roles: list[str] = []
    preferred_locations: list[str] = []
    preferred_sources: list[str] = []
    receive_email_alerts: bool = False
    is_admin: bool = False
    resume_url: str = None
    resume_text: str = None
    resume_parsed: str = None

class Token(BaseModel):
    access_token: str
    token_type: str

def authenticate_user(username: str, password: str, db):
    """Authenticate user with username and password"""
    user = db.query(User).filter(User.email == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(email: str, expires_delta: timedelta = timedelta(minutes=DEFAULT_TOKEN_EXPIRE_MINUTES)):
    """Create a JWT access token"""
    to_encode = {'sub': email}
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreateRequest, db: db_dependency):
    """Create a new user"""
    hashed_password = bcrypt_context.hash(user.password)
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
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    """Login user and return access token"""
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(email=user.email)
    return {"access_token": access_token, "token_type": "bearer"}