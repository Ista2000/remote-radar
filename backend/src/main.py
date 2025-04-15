from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine
from .routers import auth
from .models import Base, User

app = FastAPI(
    title="Remote Radar API",
    description="Backend API for Remote Radar application",
    version="0.1.0"
)

Base.metadata.create_all(bind=engine)  # Create database tables

app.add_middleware(
    CORSMiddleware,
    allow_origins=["htpp://localhost:3000"], # Allow requests from this origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def root():
    """Root endpoint returning a welcome message"""
    return {"message": "Welcome to Remote Radar API"}

app.include_router(auth.router)  # Include the auth router
