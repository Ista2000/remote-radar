import json
import logging
import os
from datetime import datetime, timedelta, timezone
import re
from sqlite3 import DataError
import traceback
from typing import Annotated, Any, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
import pdfplumber
from pydantic import BaseModel
import sqlalchemy
import sqlalchemy.exc
from sqlalchemy.orm import Session

from ..utils import hash_password, verify_password
from ..constants import DEFAULT_TOKEN_EXPIRE_MINUTES, STATIC_DIR_PATH
from ..deps import db_dependency, llm, user_dependency
from ..models import User

load_dotenv()

logger = logging.getLogger("uvicorn")

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


class UserModel(BaseModel):
    id: int
    email: str
    full_name: str
    experience_years: Optional[int]
    preferred_roles: str
    preferred_locations: str
    preferred_sources: str
    receive_email_alerts: bool
    resume_url: Optional[str]


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserModel


def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
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


@router.get("/", response_model=UserModel)
def get_myself(email: user_dependency, db: db_dependency):
    user: User = db.query(User).filter(User.email == email["email"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated"
        )
    return user


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: Annotated[str, Form()], db: db_dependency, resume: UploadFile = File(None)
):
    """Create a new user"""
    try:
        user_data = json.loads(user)
        user_obj = UserCreateRequest(**user_data)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.msg,
        )
    hashed_password = hash_password(user_obj.password)
    resume_text = None
    resume_file_path = None

    if resume:
        if resume.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported for resumes",
            )
        try:
            # Save the file to the uploads directory
            resume_file_path = os.path.join(
                STATIC_DIR_PATH, user_obj.email, resume.filename
            )
            os.makedirs(os.path.dirname(resume_file_path), exist_ok=True)
            with open(resume_file_path, "wb") as f:
                f.write(await resume.read())

            # Parse the resume text
            with pdfplumber.open(resume_file_path) as pdf:
                resume_text = re.sub(
                    r"[\n\t\r]+",
                    " ",
                    "\n".join(page.extract_text() for page in pdf.pages),
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process the resume: {str(e)}",
            )
    if resume_text is not None and len(user_obj.preferred_roles) > 0:
        resume_text = json.dumps(
            llm.extract_skills_from_resume(resume_text, user_obj.preferred_roles)
        )
    else:
        resume_text = None
    try:
        db_user = User(
            email=user_obj.email,
            hashed_password=hashed_password,
            full_name=user_obj.full_name,
            experience_years=user_obj.experience_years,
            preferred_roles=json.dumps(user_obj.preferred_roles),
            preferred_locations=json.dumps(user_obj.preferred_locations),
            preferred_sources=json.dumps(user_obj.preferred_sources),
            receive_email_alerts=user_obj.receive_email_alerts,
            is_admin=user_obj.is_admin,
            resume_url=(
                os.path.join("static", user_obj.email, resume.filename)
                if resume
                else None
            ),
            resume_text=resume_text,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        user_dict: dict = jsonable_encoder(db_user)
        user_dict.pop("hashed_password", None)
        return user_dict
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        error_message = str(e.orig)
        logger.error(f"Error while trying to create user: {traceback.format_exc()}")
        if "UNIQUE constraint failed" in error_message:
            # Example: "UNIQUE constraint failed: users.email"
            match = re.search(r"UNIQUE constraint failed: (\w+)\.(\w+)", error_message)
            if match:
                _, column = match.groups()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A user with this {column} already exists.",
                )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user due to a database constraint.",
        )
    except DataError as e:
        db.rollback()
        logger.error(f"Error while trying to create user: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid data format or value provided.",
        )
    except sqlalchemy.exc.SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error while trying to create user: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred. Please try again later.",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error while trying to create user: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the user.",
        )


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
    return {"access_token": access_token, "token_type": "bearer", "user": user}
