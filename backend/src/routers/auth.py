import json
import logging
import os
from datetime import datetime, timedelta, timezone
import re
from sqlite3 import DataError
import traceback
from typing import Annotated, Any, Optional

from dotenv import load_dotenv
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
import pdfplumber
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ValidationError,
    ValidationInfo,
    field_validator,
)
import sqlalchemy
import sqlalchemy.exc
from sqlalchemy.orm import Session

from ..utils import get_normalized_locations_list_string, hash_password, verify_password
from ..constants import DEFAULT_TOKEN_EXPIRE_MINUTES, ROLES, SOURCES, STATIC_DIR_PATH
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


class UserModel(BaseModel):
    id: int = Field(description="User ID in the backend database")
    email: EmailStr = Field(description="Email ID of the user")
    full_name: str = Field(description="Full name of the user")
    experience_years: Optional[int] = Field(
        description="Industry experience of the user"
    )
    preferred_roles: str = Field(description="Preferred roles of the user (JSON)")
    preferred_locations: str = Field(
        description="Preferred locations of the user (JSON)"
    )
    preferred_sources: str = Field(description="Preferred sources of the user (JSON)")
    receive_email_alerts: bool = Field(
        description="Did the user opt-in to receive email alerts"
    )
    resume_url: Optional[str] = Field(description="Resume URL of the user")


class UserCreateRequest(BaseModel):
    email: EmailStr = Field(description="Email ID of the user")
    password: str = Field(description="Password of the user")
    repeat_password: str = Field(description="Repeat password")
    full_name: str = Field(description="Full name of the user")
    experience_years: Optional[int] = Field(
        None, description="Industry experience of the user"
    )
    preferred_roles: list[str] = Field(
        [], description="Preferred roles of the user (JSON)"
    )
    preferred_locations: list[str] = Field(
        [], description="Preferred locations of the user (JSON)"
    )
    preferred_sources: list[str] = Field(
        [], description="Preferred sources of the user (JSON)"
    )
    receive_email_alerts: bool = Field(
        False, description="Did the user opt-in to receive email alerts"
    )

    @field_validator("password")
    def validate_password(cls, password: str):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must include at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must include at least one lowercase letter")
        if not re.search(r"[0-9]", password):
            raise ValueError("Password must include at least one digit")
        return password

    @field_validator("repeat_password")
    def passwords_match(cls, repeat_password: str, info: ValidationInfo):
        password = info.data.get("password")
        if password and repeat_password != password:
            raise ValueError("Passwords do not match.")
        return repeat_password

    @field_validator("full_name")
    def validate_full_name(cls, v: str):
        if len(v) == 0:
            raise ValueError("Field required")
        if " " not in v:
            raise ValueError("Both first name and last name is required")
        return v

    @field_validator("preferred_roles")
    def validate_preferred_roles(cls, v: list[str]):
        invalid_roles = [role for role in v if role not in ROLES]
        if invalid_roles:
            raise ValueError(f"Invalid roles: {', '.join(invalid_roles)}")
        return v

    @field_validator("preferred_locations")
    def validate_preferred_locations(cls, v: list[str]):
        all_valid_locations = get_normalized_locations_list_string()
        invalid_locations = [
            location for location in v if location not in all_valid_locations
        ]
        if len(invalid_locations) > 0:
            raise ValueError(f"Invalid locations: {', '.join(invalid_locations)}")
        return v

    @field_validator("preferred_sources")
    def validate_preferred_sources(cls, v: list[str]):
        invalid_sources = [source for source in v if source not in SOURCES]
        if invalid_sources:
            raise ValueError(f"Invalid sources: {', '.join(invalid_sources)}")
        return v


class UserUpdateRequest(BaseModel):
    password: Optional[str] = Field(None, description="Password of the user")
    repeat_password: Optional[str] = Field(None, description="Password of the user")
    full_name: Optional[str] = Field(None, description="Full name of the user")
    experience_years: Optional[int] = Field(
        None, description="Industry experience of the user"
    )
    preferred_roles: Optional[list[str]] = Field(
        None, description="Preferred roles of the user (JSON)"
    )
    preferred_locations: Optional[list[str]] = Field(
        None, description="Preferred locations of the user (JSON)"
    )
    preferred_sources: Optional[list[str]] = Field(
        None, description="Preferred sources of the user (JSON)"
    )
    receive_email_alerts: Optional[bool] = Field(
        None, description="Did the user opt-in to receive email alerts"
    )

    @field_validator("password")
    def validate_password(cls, password: Optional[str]):
        if password is None:
            return password
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must include at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must include at least one lowercase letter")
        if not re.search(r"[0-9]", password):
            raise ValueError("Password must include at least one digit")
        return password

    @field_validator("repeat_password")
    def passwords_match(cls, repeat_password: Optional[str], info: ValidationInfo):
        password = info.data.get("password")
        if password and repeat_password != password:
            raise ValueError("Passwords do not match.")
        return repeat_password

    @field_validator("full_name")
    def validate_full_name(cls, v: Optional[str]):
        if v is None:
            return v
        if len(v) == 0:
            raise ValueError("Field required")
        if " " not in v:
            raise ValueError("Both first name and last name is required")
        return v

    @field_validator("preferred_roles")
    def validate_preferred_roles(cls, v: Optional[list[str]]):
        if v is None:
            return v
        invalid_roles = [role for role in v if role not in ROLES]
        if invalid_roles:
            raise ValueError(f"Invalid roles: {', '.join(invalid_roles)}")
        return v

    @field_validator("preferred_locations")
    def validate_preferred_locations(cls, v: Optional[list[str]]):
        if v is None:
            return v
        all_valid_locations = get_normalized_locations_list_string()
        invalid_locations = [
            location for location in v if location not in all_valid_locations
        ]
        if len(invalid_locations) > 0:
            raise ValueError(f"Invalid locations: {', '.join(invalid_locations)}")
        return v

    @field_validator("preferred_sources")
    def validate_preferred_sources(cls, v: Optional[list[str]]):
        if v is None:
            return v
        invalid_sources = [source for source in v if source not in SOURCES]
        if invalid_sources:
            raise ValueError(f"Invalid sources: {', '.join(invalid_sources)}")
        return v


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


@router.get(
    "/",
    response_model=UserModel,
    summary="Get myself",
    description="Get user data for the authenticated user (myself)",
    response_description="User data for myself",
)
def get_myself(email: user_dependency, db: db_dependency):
    user: User = db.query(User).filter(User.email == email["email"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated"
        )
    return user


@router.get(
    "/{user_email}",
    response_model=UserModel,
    summary="Get user",
    description="Get user data for the the user with given email.",
    response_description="User data for the the user with given email.",
)
def get_user(email: user_dependency, db: db_dependency, user_email: str):
    user: User = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserModel,
    summary="Create user",
    description="Create user with given data.",
    response_description="User data for created user.",
)
async def create_user(
    user: Annotated[str, Form()],
    db: db_dependency,
    resume: UploadFile | str = File(None),
):
    """Create a new user"""
    try:
        user_obj = UserCreateRequest.model_validate_json(user)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=json.loads(e.json()),
        )
    hashed_password = hash_password(user_obj.password)
    resume_text = None
    resume_file_path = None

    if resume and not isinstance(resume, str):
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
            is_admin=False,
            resume_url=(
                os.path.join("static", user_obj.email, resume.filename)
                if resume and not isinstance(resume, str)
                else None
            ),
            resume_text=resume_text,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
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


@router.patch(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=UserModel,
    summary="Edit user",
    description="Edit user with given data. Users can only call this endpoint for themselves.",
    response_description="Updated user data for the user.",
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "updated_user": {
                                "type": "string",
                                "format": "json",
                                "description": "A JSON string matching the UserUpdateRequest model",
                                "examples": [
                                    json.dumps(
                                        {
                                            "full_name": "Jane Doe",
                                            "experience_years": 3,
                                            "preferred_roles": ["Frontend", "DevOps"],
                                            "preferred_locations": [
                                                "Remote",
                                                "Bengaluru",
                                            ],
                                            "preferred_sources": ["LinkedIn", "Indeed"],
                                            "receive_email_alerts": True,
                                        },
                                        indent=2,
                                    )
                                ],
                            },
                            "resume": {
                                "type": "string",
                                "format": "binary",
                                "description": "Optional resume file to upload",
                            },
                        },
                        "required": ["updated_user"],
                    }
                }
            }
        }
    },
)
async def update_user(
    email: user_dependency,
    db: db_dependency,
    updated_user: Annotated[str, Form()],
    resume: UploadFile | str = File(None),
):
    """Update current user's details"""
    try:
        user_obj = UserUpdateRequest.model_validate_json(updated_user)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=json.loads(e.json()),
        )

    user: User = db.query(User).filter(User.email == email["email"]).first()
    resume_text = None
    resume_file_path = None

    if resume and not isinstance(resume, str):
        if resume.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported for resumes",
            )
        try:
            resume_file_path = os.path.join(
                STATIC_DIR_PATH, user.email, resume.filename
            )
            os.makedirs(os.path.dirname(resume_file_path), exist_ok=True)
            with open(resume_file_path, "wb") as f:
                f.write(await resume.read())

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

    if resume_text:
        resume_text = json.dumps(
            llm.extract_skills_from_resume(resume_text, user_obj.preferred_roles)
        )

    try:
        user.full_name = user_obj.full_name or user.full_name
        user.experience_years = user_obj.experience_years or user.experience_years
        user.preferred_roles = (
            json.dumps(user_obj.preferred_roles)
            if user_obj.preferred_roles
            else user.preferred_roles
        )
        user.preferred_locations = (
            json.dumps(user_obj.preferred_locations)
            if user_obj.preferred_locations
            else user.preferred_locations
        )
        user.preferred_sources = (
            json.dumps(user_obj.preferred_sources)
            if user_obj.preferred_sources
            else user.preferred_sources
        )
        user.receive_email_alerts = (
            user_obj.receive_email_alerts
            if user_obj.receive_email_alerts is not None
            else user.receive_email_alerts
        )

        if resume and not isinstance(resume, str):
            user.resume_url = os.path.join("static", user.email, resume.filename)
            user.resume_text = resume_text

        db.commit()
        db.refresh(user)
        return user

    except Exception as e:
        db.rollback()
        logger.error(f"Error while updating user: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user information.",
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
