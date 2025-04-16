from typing import Optional
from fastapi import APIRouter
from sqlalchemy import case

from ..deps import db_dependency, job_collection, user_dependency
from ..models import Job

router = APIRouter(
    prefix="/job",
    tags=["job"],
)


@router.get("/")
def all_jobs(user: user_dependency, db: db_dependency):
    """
    Get all jobs.

    :param user: The current user.
    :param db: The database session.
    :return: A list of all job listings.
    """
    # Query the jobs table for all job listings
    return db.query(Job).all()


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
    """
    Search for jobs based on the provided search query and optional filters.

    :param form_data: The search query and optional filters.
    :param db: The database session.
    :return: A list of job listings matching the search criteria.
    """

    # Extract job URLs from the job collection
    job_urls = [
        job["url"]
        for job in job_collection.query(
            query_texts=[(role + " " + search_query).strip()],
            n_results=5,
            include=["metadatas"],
        )["metadatas"][0]
    ]
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
