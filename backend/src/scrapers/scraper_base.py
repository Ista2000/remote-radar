import logging
from sqlite3 import IntegrityError
import traceback
import requests
import time
from abc import abstractmethod
from bs4 import BeautifulSoup
from typing import Callable, Dict, List, Optional

from ..deps import db_dependency, job_collection, llm
from ..models import Job

logger = logging.getLogger("uvicorn")


class ScraperBase:
    def __init__(self, source: str, role: str, db: db_dependency):
        self.source = source
        self.role = role
        self.db = db
        self.location_to_urls: Dict[str, list[str]] = {}
        self.job_listings: List[Dict[str, str]] = []

    @abstractmethod
    def fetch_job_listing_urls(self) -> None:
        """Fetch job listings from the source and populate self.urls."""
        pass

    @abstractmethod
    def parse_job_title(self, soup: BeautifulSoup) -> str:
        """Parse job title from the soup object fetched from the URL."""
        pass

    @abstractmethod
    def parse_job_company(self, soup: BeautifulSoup) -> str:
        """Parse job company from the soup object fetched from the URL."""
        pass

    @abstractmethod
    def parse_job_location(self, soup: BeautifulSoup) -> str:
        """Parse job location from the soup object fetched from the URL."""
        pass

    @abstractmethod
    def parse_job_description(self, soup: BeautifulSoup) -> str:
        """Parse job description from the soup object fetched from the URL."""
        pass

    @abstractmethod
    def parse_required_experience(self, soup: BeautifulSoup) -> Optional[str]:
        """Parse required experience from the soup object fetched from the URL."""
        pass

    @abstractmethod
    def parse_posted_at(self, soup: BeautifulSoup) -> str:
        """Parse the posted date from the soup object fetched from the URL."""
        pass

    def infer_job_details(
        self, page_data: str, company: str, location: str
    ) -> dict[str, str]:
        """Infer job details using LLM."""
        try:
            return llm.extract_job_from_page_data(
                page_data=page_data,
                source=self.source,
            )
        except Exception:
            logger.error(f"Error inferring job details: {traceback.format_exc()}")
            return {}

    def add_job_details_to_collection(self, job_details: list[dict[str, str]]) -> None:
        """Add job details to the collection."""
        try:
            job_collection.add(
                documents=[
                    job_detail["title"] + job_detail["description"]
                    for job_detail in job_details
                ],
                ids=[job_detail["url"] for job_detail in job_details],
            )
        except Exception as e:
            logger.error(f"Error adding job details to collection: {e}")

    def parse_job_details(self, url: str, location: str):
        logger.info(f"Parsing job details from {url}...")
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            page_data = soup.find("div", class_="top-card-layout__card").get_text(
                strip=True, separator=" "
            )
            page_data += soup.find(
                "div", class_="description__text description__text--rich"
            ).get_text(strip=True, separator=" ")
            company = self.parse_job_company(soup)
            job_details = {
                **self.infer_job_details(page_data, company, location),
                "title": self.parse_job_title(soup),
                "company": company,
                "location": location,
                "url": url,
                "posted_at": self.parse_posted_at(soup),
                "role": self.role,
            }
            if "description" not in job_details:
                description = self.parse_job_description(soup)
                if description:
                    job_details["description"] = description
            return job_details
        except Exception as e:
            logger.error(
                f"Error parsing job details from {url}: {traceback.format_exc()}"
            )
            return {
                "title": None,
                "company": None,
                "location": None,
                "description": None,
                "required_experience": None,
                "url": url,
                "posted_at": None,
                "salary_min": None,
                "salary_max": None,
                "salary_currency": None,
                "salary_from_levels_fyi": False,
                "role": self.role,
                "remote": None,
            }

    def save_to_db(self, jobs: list[dict]):
        try:
            self.db.bulk_save_objects(
                [
                    Job(
                        title=job_dict["title"],
                        company=job_dict["company"],
                        location=job_dict["location"],
                        role=job_dict["role"],
                        description=job_dict["description"],
                        required_experience=job_dict.get("required_experience"),
                        url=job_dict["url"],
                        source=self.source,
                        salary_min=job_dict.get("salary_min"),
                        salary_max=job_dict.get("salary_max"),
                        salary_currency=job_dict.get("salary_currency", "USD"),
                        salary_from_levels_fyi=job_dict.get(
                            "salary_from_levels_fyi", False
                        ),
                        posted_at=job_dict["posted_at"],
                        remote=job_dict["remote"],
                    )
                    for job_dict in jobs
                    if "title" in job_dict and job_dict["title"] is not None
                ]
            )
            self.db.commit()
        except IntegrityError:
            logger.error(
                f"Integrity error while saving to DB: {traceback.format_exc()}"
            )
            self.db.rollback()
        except Exception:
            logger.error(f"Error while saving to DB: {traceback.format_exc()}")
            self.db.rollback()

    def log_jobs(self, jobs: list[dict]):
        for job in jobs:
            logger.info(
                f"""
Job Details for {job["url"]}
Title: {job["title"]}
Role: {job["role"]}
Company: {job["company"]}
Location: {job["location"]}
Required Experience: {job.get("required_experience")}
Description: {job["description"]}
Posted At: {job["posted_at"]}
Source: {self.source}
Salary Min: {job.get("salary_min")}
Salary Max: {job.get("salary_max")}
Salary Currency: {job.get("salary_currency", "USD")}
Salary From Levels FYI: {job.get("salary_from_levels_fyi", False)}
"""
            )

    def run(self):
        """Main method to run the scraper."""
        start_time = time.time()
        self.fetch_job_listing_urls()
        logger.info(
            f"Fetched {sum(len(urls) for urls in self.location_to_urls.values())} " +
            f"job listings in {time.time() - start_time:.2f} seconds."
        )
        parse_jobs_start_time = time.time()
        jobs = [
            self.parse_job_details(job_listing_url, location)
            for location, job_listing_urls in self.location_to_urls.items()
            for job_listing_url in job_listing_urls
        ]
        logger.info(
            f"Parsed {len(jobs)} job listings in {time.time() - parse_jobs_start_time:.2f} seconds."
        )
        save_jobs_start_time = time.time()
        self.save_to_db(jobs)
        self.add_job_details_to_collection(jobs)
        logger.info(
            f"Saved {len(jobs)} job listings to the database in {time.time() - save_jobs_start_time:.2f} seconds."
        )
        logger.info(f"Scraping completed in {time.time() - start_time:.2f} seconds.")
