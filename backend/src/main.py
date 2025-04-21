from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
import logging
from contextlib import asynccontextmanager
import os

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .constants import EXPIRE_JOBS_AFTER_DAYS, STATIC_DIR_PATH
from .database import engine
from .deps import job_collection
from .models import Base, Job
from .routers import auth, job, rls
from .scrapers.scraper_factory import ScraperFactory

logger = logging.getLogger("uvicorn")


def run_all_scrapers(db: Session, scheduler: BackgroundScheduler) -> None:
    for scraper in ScraperFactory(db).get_all_scrapers():
        scraper.run()  # Initial run to fetch data immediately
        # Schedule the scraper to run every 6 hours
        scheduler.add_job(
            scraper.run,
            trigger="interval",
            seconds=60 * 60 * 6,  # Run every 6 hours
        )


def mark_jobs_inactive(db: Session) -> None:
    try:
        cutoff_date = datetime.now(timezone.utc) - relativedelta(
            days=EXPIRE_JOBS_AFTER_DAYS
        )
        old_jobs = (
            db.query(Job)
            .filter(Job.posted_at < cutoff_date, Job.is_active == True)
            .all()
        )

        for job in old_jobs:
            job.is_active = False
        db.commit()
        print(f"{len(old_jobs)} jobs marked as inactive.")
    except Exception as e:
        print(f"Error marking old jobs inactive: {e}")
        db.rollback()
    finally:
        db.close()


def expire_jobs(db: Session) -> None:
    try:
        old_jobs = db.query(Job).filter(Job.is_active == False).all()

        for job in old_jobs:
            db.delete(job)
        db.commit()
        job_collection.delete(ids=[job.url for job in old_jobs])
        print(f"{len(old_jobs)} jobs deleted.")
    except Exception as e:
        print(f"Error marking old jobs inactive: {e}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for the FastAPI app"""
    scheduler = BackgroundScheduler()
    logger.info("Starting background jobs scheduler...")
    db_gen = get_db()
    db = next(db_gen)  # Get the database session
    run_all_scrapers(db=db, scheduler=scheduler)
    scheduler.add_job(
        mark_jobs_inactive,
        args=[db],
        trigger="interval",
        seconds=60 * 60 * 24,  # Run everyday
    )
    scheduler.add_job(
        expire_jobs,
        args=[db],
        trigger="interval",
        seconds=60 * 60 * 24,  # Run everyday
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
    allow_origins=["http://localhost:3000", "http://frontend:3000"],  # Allow requests from this origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(auth.router)  # Include the auth router
app.include_router(job.router)  # Include the job router
app.include_router(rls.router)  # Include the rls router
