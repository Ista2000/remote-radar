from typing import Dict, List

from .scraper_base import ScraperBase
from .linkedin import LinkedInScraper

class ScraperFactory:
    """
    A factory class to create scraper instances based on the provided scraper type.
    """
    
    def __init__(self, db):
        self.scrappers: Dict[str, ScraperBase] = {
            "linkedin": LinkedInScraper(db),
            # Add other scrappers here as needed
        }
    
    def get_scraper(self, source: str):
        """
        Returns an instance of the scraper based on the source.
        
        :param source: The source for which to create a scraper.
        :return: An instance of the corresponding scraper class.
        """
        if source not in self.scrappers:
            raise ValueError(f"Scraper for {source} not found.")
        
        return self.scrappers[source]

    def get_all_scrapers(self) -> List[ScraperBase]:
        """
        Returns a list of all available scrapers.
        
        :return: A list of all available scrapers.
        """
        return list(self.scrappers.values())

