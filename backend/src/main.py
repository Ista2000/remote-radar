import logging
from contextlib import asynccontextmanager
import os

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .constants import LOCATION_GEO_IDS_FOR_LINKEDIN, STATIC_DIR_PATH
from .database import engine
from .deps import get_db
from .models import Base
from .routers import auth, job, rls
from .scrapers.scraper_factory import ScraperFactory

logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for the FastAPI app"""
    scheduler = BackgroundScheduler()
    logger.info("Starting background jobs scheduler...")
    db_gen = get_db()
    db = next(db_gen)  # Get the database session
    for scraper in ScraperFactory(db).get_all_scrapers():
        scraper.run()  # Initial run to fetch data immediately
        # Schedule the scraper to run every 6 hours
        scheduler.add_job(
            scraper.run,
            trigger="interval",
            seconds=60 * 60 * 6,  # Run every 6 hours
        )
    try:
        next(db_gen)  # Ensure the database session is yielded
    except StopIteration:
        pass
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

os.makedirs(STATIC_DIR_PATH, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR_PATH), name="static")

Base.metadata.create_all(bind=engine)  # Create database tables

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from this origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


@app.get("/")
async def root():
    """Root endpoint returning a welcome message"""
    return {"message": "Welcome to Remote Radar API"}


app.include_router(auth.router)  # Include the auth router
app.include_router(job.router)  # Include the job router
app.include_router(rls.router)  # Include the rls router
