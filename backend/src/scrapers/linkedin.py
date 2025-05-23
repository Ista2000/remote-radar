import logging
import traceback

import requests
from bs4 import BeautifulSoup

from ..constants import LOCATION_GEO_IDS_FOR_LINKEDIN
from ..utils import get_posted_date
from .scraper_base import ScraperBase

logger = logging.getLogger("uvicorn")


class LinkedInScraper(ScraperBase):
    def __init__(self, db, role, num_jobs_per_location=1):
        super().__init__(source="LinkedIn", role=role, db=db)
        self.num_jobs_per_location = num_jobs_per_location

    def fetch_job_listing_urls(self):
        logger.info("Fetching job listings from LinkedIn...")
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            for country, city_dict in LOCATION_GEO_IDS_FOR_LINKEDIN.items():
                for city, geoId in city_dict.items():
                    self.location_to_urls[f"{city}, {country}"] = []
                    for page_num in range(0, 1):
                        url = f"https://www.linkedin.com/jobs/search/?keywords={self.role}&f_WT=2&geoId={geoId}&position=1&pageNum={page_num}"
                        response = requests.get(url, headers=headers)
                        soup = BeautifulSoup(response.text, "html.parser")

                        for job_card in soup.select("ul.jobs-search__results-list li"):
                            link_elem = job_card.find("a", href=True)
                            if link_elem is not None:
                                self.location_to_urls[f"{city}, {country}"].append(
                                    "https://www.linkedin.com/"
                                    + "/".join(
                                        link_elem["href"].split("?")[0].split("/")[3:]
                                    )
                                )
                                if (
                                    len(self.location_to_urls[f"{city}, {country}"])
                                    >= self.num_jobs_per_location
                                ):
                                    break
                        if (
                            len(self.location_to_urls[f"{city}, {country}"])
                            >= self.num_jobs_per_location
                        ):
                            break
        except Exception:
            logger.error(
                f"Error fetching job listings from LinkedIn: {traceback.format_exc()}"
            )
        finally:
            logger.info(f"Fetched all job listings")

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
