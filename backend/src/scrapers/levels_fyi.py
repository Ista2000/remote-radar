import logging
from langchain_community.document_loaders import WebBaseLoader

logger = logging.getLogger("uvicorn")


def scrape_levels_fyi(company: str, role: str, location: str) -> str:
    """
    Scrape Levels.fyi for salary information based on company, role, and location.
    """
    company = company.replace(" ", "-").lower()
    role = role.replace(" ", "-").lower()
    location = location.replace(" ", "-").lower()
    location = location[: location.index(",") if "," in location else len(location)]
    # Construct the URL for Levels.fyi
    try:
        url = f"https://www.levels.fyi/companies/{company}/salaries/{role}/locations/{location}"
        logger.info(f"Scraping Levels.fyi for URL: {url}")
        loader = WebBaseLoader(url)
        data = loader.load().pop().page_content
        return data
    except Exception as e:
        print(f"Error scraping Levels.fyi for URL {url}: {e}")
        return ""
