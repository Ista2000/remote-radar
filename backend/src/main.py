import logging

from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .scrapers import linkedin
from .database import engine
from .routers import auth
from .models import Base

logger = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for the FastAPI app"""
    scheduler = BackgroundScheduler()
    logger.info("Starting background jobs scheduler...")
    linkedin.scrape_linkedin_jobs()  # Initial run of the job
    scheduler.add_job(linkedin.scrape_linkedin_jobs, "interval", hours=6)
    scheduler.start()
    yield
    logger.info("Shutting down background jobs scheduler...")
    scheduler.shutdown()


app = FastAPI(
    title="Remote Radar API",
    description="Backend API for Remote Radar application",
    version="0.1.0",
    lifespan=lifespan,
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
