from datetime import datetime
import json
import logging
import traceback
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from groq import RateLimitError
from pydantic import BaseModel, Field
from sqlalchemy import case, desc

from ..deps import db_dependency, job_collection, llm, user_dependency
from ..models import Job, User

router = APIRouter(
    prefix="/job",
    tags=["job"],
)

logger = logging.getLogger("uvicorn")


class JobModel(BaseModel):
    title: str = Field(
        description="Job title",
        examples=["Front-end developer", "DevOps Engineer (Entry level)"],
    )
    company: str = Field(description="Job company", examples=["Google", "Microsoft"])
    location: str = Field(description="Job location", examples=["Bengaluru, India"])
    description: str = Field(description="Job description (formatted as HTML)")
    url: str = Field(description="Original job URL")
    source: str = Field(description="Job source", examples=["LinkedIn"])
    role: str = Field(description="Job role", examples=["Software Engineer"])

    salary_min: Optional[int] = Field(
        description="Minimum salary offered", examples=[50000]
    )
    salary_max: Optional[int] = Field(
        description="Maximum salary offered", examples=[200000]
    )
    salary_currency: str = Field(description="Salary currency", examples=["USD"])
    salary_from_levels_fyi: bool = Field(
        description="Was salary information sourced from levels.fyi", examples=[False]
    )
    required_experience: int = Field(
        description="Minimum years of experience required", examples=[3]
    )
    remote: bool = Field(description="Is the job remote available", examples=[True])

    posted_at: datetime = Field(
        description="Time and date of posting (approx)",
        examples=["2025-04-20T16:30:23.161919+00:00"],
    )
    is_active: bool = Field(description="Is the job active or expired", examples=[True])


@router.get(
    "/",
    response_model=JobModel,
    summary="Get job",
    description="Get a specific job from URL.",
    response_description="Returns a job from the provided URL.",
)
def get_job(db: db_dependency, url: str = Query(description="URL of the scraped job")):
    """Get job from url"""
    try:
        return db.query(Job).filter(Job.url == url).first()
    except Exception as e:
        logger.error(f"Error while fetching job with url {url}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed to fetch job at {url}",
        )


@router.get(
    "/recommended",
    response_model=dict[str, list[JobModel]],
    summary="Get recommended jobs for the user",
    description="Returns a mapping of role → recommended job listings based on user's resume.",
    response_description="A mapping of role → recommended job listings based on user's resume.",
)
def recommended_jobs(
    user: user_dependency,
    db: db_dependency,
    role: Optional[str] = Query(
        None, description="Role filter to get recommended jobs"
    ),
    sort_by: str = Query(
        "relevance",
        description="Sort by experience required (increasing or decreasing), "
        "average salary or relevance (One of `relevance`, `salary`, `inc_experience`, `desc_experience)",
        examples=["inc_experience"],
    ),
):
    """Get all recommended jobs for the user based on their resume keywords"""
    resume_text = db.query(User.resume_text).filter(User.email == user["email"]).first()
    if resume_text is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User not authenticated",
        )
    resume_text_json = resume_text[0]
    if not resume_text_json:
        return {"NULL": db.query(Job).filter(Job.is_active == True).all()}

    resume_text_grouped_by_roles: dict = json.loads(resume_text_json)
    if role:
        resume_text_grouped_by_roles = {role: resume_text_grouped_by_roles[role]}

    role_to_urls = dict(
        zip(
            list(resume_text_grouped_by_roles.keys()),
            job_collection.query(
                query_texts=[
                    " ".join(keywords)
                    for keywords in resume_text_grouped_by_roles.values()
                ],
                n_results=100,
                include=[],
            )["ids"],
        )
    )
    jobs = (
        db.query(Job)
        .filter(
            Job.url.in_(
                list(set(url for urls in role_to_urls.values() for url in urls))
            ),
            Job.is_active == True,
        )
        .all()
    )
    url_to_job = {job.url: job for job in jobs}

    def sort_func(job: Job, role: str):
        if sort_by == "desc_experience":
            return int(job.required_experience)
        elif sort_by == "inc_experience":
            return 15 - int(job.required_experience)
        elif sort_by == "salary":
            return (
                (int(job.salary_min) + int(job.salary_max)) / 2
                if job.salary_min and job.salary_max
                else 0
            )
        else:
            return len(role_to_urls) - role_to_urls[role].index(job.url)

    return {
        role: sorted(
            [url_to_job[url] for url in urls if url in url_to_job],
            key=lambda job: sort_func(job, role),
            reverse=True,
        )
        for role, urls in role_to_urls.items()
    }


@router.get(
    "/search",
    response_model=dict[str, list[JobModel]],
    summary="Search jobs",
    description="Returns a mapping of role → recommended job listings based on search query.",
    response_description="A mapping of role → recommended job listings based on search query.",
)
def search_jobs(
    user: user_dependency,
    db: db_dependency,
    search_query: str = Query(
        "",
        description="Search keyword(s) for the job title or description",
        examples=["Software%20Engineer%20in%20Bengaluru"],
    ),
    location: str = Query(
        "",
        description="Preferred job location",
        examples=["Bengaluru,%20India"],
    ),
    source: str = Query(
        "",
        description="Source of the job listing",
        examples=["LinkedIn", "Glassdoor", "Indeed", "Wellfound"],
    ),
    role: str = Query(
        "", description="Preferred job role", examples=["Software%20Engineer", "Ninja"]
    ),
    remote: bool = Query(
        False, description="Filter by remote preference", examples=[True, False]
    ),
    min_experience_years: Optional[int] = Query(
        None, description="Minimum years of experience required", examples=[1, 2, 3]
    ),
    max_experience_years: Optional[int] = Query(
        None, description="Maximum years of experience required", examples=[10, 11, 12]
    ),
    sort_by: str = Query(
        "relevance",
        description="Sort by experience required (increasing or decreasing), "
        "average salary or relevance (One of `relevance`, `salary`, `inc_experience`, `desc_experience)",
        examples=["inc_experience"],
    ),
):
    """Search for jobs based on the provided search query and optional filters"""
    # Extract job URLs from the job collection
    job_listings = db.query(Job)
    ordering = None
    if search_query:
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
        job_listings = job_listings.filter(Job.url.in_(job_urls), Job.is_active == True)
    if sort_by == "inc_experience":
        job_listings = job_listings.order_by(Job.required_experience)
    if sort_by == "desc_experience":
        job_listings = job_listings.order_by(desc(Job.required_experience))
    elif sort_by == "salary":
        job_listings = job_listings.order_by(
            desc((Job.salary_min + Job.salary_max) / 2)
        )
    else:
        job_listings = job_listings.order_by(ordering)
    if location:
        job_listings = job_listings.filter(Job.location == location)
    if source:
        job_listings = job_listings.filter(Job.source == source)
    if role:
        job_listings = job_listings.filter(Job.role == role)
    if min_experience_years is not None:
        job_listings = job_listings.filter(
            Job.required_experience >= min_experience_years
        )
    if max_experience_years is not None:
        job_listings = job_listings.filter(
            Job.required_experience <= max_experience_years
        )
    if remote:
        job_listings = job_listings.filter(Job.remote == True)

    jobs = job_listings.all()
    return dict(
        (role, list(job for job in jobs if job.role == role))
        for role in set(job.role for job in jobs)
    )


@router.get(
    "/generate-cover",
    response_model=str,
    summary="Generate cover letter",
    description="Generates and returns cover letter for a particular job "
    "based on job description and the resume data of the user",
    response_description="String representing cover letter.",
)
def generate_cover(
    user: user_dependency,
    db: db_dependency,
    job_url: str = Query(
        description="Job URL for which to generate a cover letter for.",
        examples=["inc_experience"],
    ),
):
    logger.info(job_url)
    try:
        job_info = (
            db.query(Job.company, Job.description, Job.role)
            .filter(Job.url == job_url)
            .first()
        )
        if job_info is None:
            raise ValueError("Job with specified URL does not exist.")
        company, job_description, role = job_info.tuple()
        user_info = (
            db.query(User.resume_text, User.full_name)
            .filter(User.email == user["email"])
            .first()
        )
        if user_info is None:
            raise ValueError("User not authenticated.")
        user_resume_data, name = user_info.tuple()
        return llm.generate_cover_letter(
            resume_data=json.loads(user_resume_data)[role],
            company=company,
            name=name,
            job_description=job_description,
        )
    except RateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Hit rate limit for the LLM models on the server",
        )
    except Exception as e:
        logger.error(f"Error trying to generate cover letter: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )
