import logging
import traceback

import requests
from bs4 import BeautifulSoup

from ..utils import get_posted_date
from .scraper_base import ScraperBase

logger = logging.getLogger("uvicorn")


class LinkedInScraper(ScraperBase):
    def __init__(self, db, role="software engineer", num_jobs=5):
        super().__init__(source="LinkedIn", role=role, db=db)
        self.num_jobs = num_jobs

    def fetch_job_listing_urls(self):
        logger.info("Fetching job listings from LinkedIn...")
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            for page_num in range(0, 1):
                url = f"https://www.linkedin.com/jobs/search/?keywords={self.role}&f_WT=2&position=1&pageNum={page_num}"

                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")

                for job_card in soup.select("ul.jobs-search__results-list li"):
                    link_elem = job_card.find("a", href=True)
                    if link_elem is not None:
                        self.urls.append(
                            "https://www.linkedin.com/"
                            + "/".join(link_elem["href"].split("?")[0].split("/")[3:])
                        )
                        if len(self.urls) >= self.num_jobs:
                            break
                if len(self.urls) >= self.num_jobs:
                    break
        except Exception:
            logger.error(
                f"Error fetching job listings from LinkedIn: {traceback.format_exc()}"
            )
        finally:
            logger.info(f"Fetched {len(self.urls)} job listings.")

    def parse_job_title(self, soup):
        title_elem = soup.find("h1", class_="top-card-layout__title")
        if title_elem:
            return title_elem.get_text(strip=True)
        return None

    def parse_job_company(self, soup):
        company_elem = soup.find("a", class_="topcard__org-name-link")
        if company_elem:
            return company_elem.get_text(strip=True)
        return None

    def parse_job_location(self, soup):
        location_elem = soup.find(
            "span", class_="topcard__flavor topcard__flavor--bullet"
        )
        if location_elem:
            return location_elem.get_text(strip=True)
        return None

    def parse_job_description(self, soup):
        description_elem = soup.find(
            "div", class_="description__text description__text--rich"
        )
        if description_elem:
            return description_elem.get_text(strip=True, separator=" ")
        return None

    def parse_posted_at(self, soup):
        time_elem = soup.find("time", class_="aside-job-card__listdate--new")
        if time_elem is None:
            time_elem = soup.find("time", class_="aside-job-card__listdate")
        if time_elem is None:
            return None
        time_elem = time_elem.get_text(strip=True)
        return get_posted_date(time_elem)

    def parse_required_experience(self, soup):
        return None
