import logging
import os
import traceback
from typing import Annotated

import chromadb
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .llm.llm import LLM
from .database import SessionLocal

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger("uvicorn")

SECRET_KEY = str(os.getenv("AUTH_SECRET_KEY", ""))
ALGORITHM = str(os.getenv("AUTH_ALGORITHM", ""))

llm = LLM()
chromadb_client = chromadb.Client()
job_collection = chromadb_client.create_collection(
    name="job_collection", metadata={"hnsw:space": "cosine"}
)


def get_db():
    """Dependency that provides a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")
oauth2_bearer_dependency = Annotated[str, Depends(oauth2_bearer)]


async def get_current_user(token: oauth2_bearer_dependency):
    """Dependency that retrieves the current user from the token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = str(payload.get("sub", ""))
        if username == "":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return {"username": username}
    except JWTError:
        logger.error(
            f"Error while trying to verify user with token {token}: {traceback.format_exc()}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from None


user_dependency = Annotated[dict, Depends(get_current_user)]
