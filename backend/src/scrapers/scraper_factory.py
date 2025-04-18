from ..constants import ROLES
from .linkedin import LinkedInScraper
from .scraper_base import ScraperBase


class ScraperFactory:
    """
    A factory class to create scraper instances based on the provided scraper type.
    """

    def __init__(self, db) -> None:
        self.scrapers: dict[str, list[ScraperBase]] = {
            "LinkedIn": list(LinkedInScraper(db, role) for role in ROLES),
            # Add other scrappers here as needed
        }

    def get_scraper(self, source: str) -> ScraperBase:
        """
        Returns an instance of the scraper based on the source.

        :param source: The source for which to create a scraper.
        :return: An instance of the corresponding scraper class.
        """
        if source not in self.scrapers:
            raise ValueError(f"Scraper for {source} not found.")

        return self.scrapers[source]

    def get_all_scrapers(self) -> list[ScraperBase]:
        """
        Returns a list of all available scrapers.

        :return: A list of all available scrapers.
        """
        return list(scraper for scrapers in self.scrapers.values() for scraper in scrapers)
