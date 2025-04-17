import json
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import case

from ..deps import db_dependency, job_collection, user_dependency
from ..models import Job, User

router = APIRouter(
    prefix="/job",
    tags=["job"],
)

logger = logging.getLogger("uvicorn")


@router.get("/")
def get_job(db: db_dependency, url: str):
    """Get job from url"""
    try:
        return db.query(Job).filter(Job.url == url).first[0]
    except Exception as e:
        logger.error(f"Error while fetching job with url {url}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed to fetch job at {url}",
        )


@router.get("/recommended")
def recommended_jobs(
    user: user_dependency, db: db_dependency, role: Optional[str] = None
):
    """Get all jobs"""
    # Query the jobs table for all job listings
    resume_text_json = (
        db.query(User.resume_text).filter(User.email == user["email"]).first()[0]
    )
    if not resume_text_json:
        return db.query(Job).all()
    resume_text_grouped_by_roles: dict = json.loads(resume_text_json)
    if role:
        resume_text_grouped_by_roles = {role: resume_text_grouped_by_roles[role]}
    role_to_urls = dict(
        zip(
            list(resume_text_grouped_by_roles.keys()),
            job_collection.query(
                query_texts=list(
                    " ".join(keywords)
                    for keywords in resume_text_grouped_by_roles.values()
                ),
                n_results=2,
                include=[],
            )["ids"],
        )
    )

    jobs = db.query(Job).filter(
        Job.url.in_(list(set(url for urls in role_to_urls.values() for url in urls)))
    )
    url_to_job = dict((job.url, job) for job in jobs)
    return {
        role: [url_to_job[url] for url in urls] for role, urls in role_to_urls.items()
    }


@router.get("/search")
def search_jobs(
    user: user_dependency,
    db: db_dependency,
    search_query: str,
    location: str = "",
    source: str = "",
    role: str = "",
    experience_years: Optional[int] = None,
):
    """Search for jobs based on the provided search query and optional filters"""

    # Extract job URLs from the job collection
    job_urls = list(
        job_collection.query(
            query_texts=[(role + " " + search_query).strip()],
            n_results=5,
            include=[],
        )["ids"][0]
    )
    ordering = case({val: idx for idx, val in enumerate(job_urls)}, value=Job.url)
    # Query jobs table for job listings with given
    # job urls filtered by the optional filters with ordering
    job_listings = db.query(Job).filter(Job.url.in_(job_urls)).order_by(ordering)
    if len(location) > 0:
        job_listings = job_listings.filter(Job.location == location)
    if len(source) > 0:
        job_listings = job_listings.filter(Job.source == source)
    if len(role) > 0:
        job_listings = job_listings.filter(Job.role == role)
    if experience_years is not None:
        job_listings = job_listings.filter(Job.required_experience <= experience_years)
    # Convert the query result to a list of dictionaries
    return job_listings.all()
