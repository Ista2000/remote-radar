from abc import abstractmethod
import logging
import time
from typing import List, Dict

from bs4 import BeautifulSoup
import requests

from ..models import Job
from ..deps import db_dependency

logger = logging.getLogger("uvicorn")


class ScraperBase:
    def __init__(self, source: str, db: db_dependency):
        self.source = source
        self.db = db
        self.urls = []
        self.job_listings = []

    @abstractmethod
    def fetch_job_listing_urls(self) -> List[str]:
        '''Fetch job listings from the source and populate self.urls.'''
        return None

    @abstractmethod
    def parse_job_title(self, soup: BeautifulSoup) -> str:
        '''Parse job title from the soup object fetched from the URL.'''
        return None

    @abstractmethod
    def parse_job_company(self, soup: BeautifulSoup) -> str:
        '''Parse job company from the soup object fetched from the URL.'''
        return None

    @abstractmethod
    def parse_job_location(self, soup: BeautifulSoup) -> str:
        '''Parse job location from the soup object fetched from the URL.'''
        return None

    @abstractmethod
    def parse_job_description(self, soup: BeautifulSoup) -> str:
        '''Parse job description from the soup object fetched from the URL.'''
        return None

    @abstractmethod
    def parse_posted_at(self, soup: BeautifulSoup) -> str:
        '''Parse the posted date from the soup object fetched from the URL.'''
        return None

    @abstractmethod
    def parse_or_fetch_salary(self, soup: BeautifulSoup) -> Dict[str, str]:
        '''Parse salary information from the soup object fetched from the URL.'''
        return {}

    
    def parse_job_details(self, url):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0"
            }
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            return {
                "title": self.parse_job_title(soup),
                "company": self.parse_job_company(soup),
                "location": self.parse_job_location(soup),
                "description": self.parse_job_description(soup),
                "url": url,
                "posted_at": self.parse_posted_at(soup),
                **self.parse_or_fetch_salary(soup)
            }
        except Exception as e:
            logger.error(f"Error parsing job details from {url}: {e}")
            return {
                "title": None,
                "company": None,
                "location": None,
                "description": None,
                "url": url,
                "posted_at": None,
                "salary_min": None,
                "salary_max": None,
                "salary_currency": None,
                "salary_from_levels_fyi": False,
            }

    def save_to_db(self, jobs: List[Dict]):
        self.db.bulk_save_objects([
            Job(
                title=job_dict["title"],
                company=job_dict["company"],
                location=job_dict["location"],
                description=job_dict["description"],
                url=job_dict["url"],
                source=self.source,
                salary_min=job_dict.get("salary_min"),
                salary_max=job_dict.get("salary_max"),
                salary_currency=job_dict.get("salary_currency", "USD"),
                salary_from_levels_fyi=job_dict.get("salary_from_levels_fyi", False),
                posted_at=job_dict["posted_at"],
            ) for job_dict in jobs if 'title' in job_dict and job_dict['title'] is not None
        ])
        self.db.commit()

    def log_jobs(self, jobs: List[Dict]):
        for job in jobs:
            logger.info(f"""
Job Details for {job['url']}
Title: {job['title']}
Company: {job['company']}
Location: {job['location']}
Description: {job['description']}
Posted At: {job['posted_at']}
Source: {self.source}
Salary Min: {job.get('salary_min')}
Salary Max: {job.get('salary_max')}
Salary Currency: {job.get('salary_currency', 'USD')}
Salary From Levels FYI: {job.get('salary_from_levels_fyi', False)}
""")

    def run(self):
        """Main method to run the scraper."""
        start_time = time.time()
        self.fetch_job_listing_urls()
        jobs = [self.parse_job_details(job_listing_url) for job_listing_url in self.urls]
        self.log_jobs(jobs)
        # self.save_to_db(jobs)
        end_time = time.time()
        logger.info(f"Scraping completed in {end_time - start_time:.2f} seconds.")
