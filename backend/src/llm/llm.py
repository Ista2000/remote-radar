import json
import logging
import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

from ..scrapers.levels_fyi import scrape_levels_fyi
from .prompts import *

load_dotenv()

GROQ_API_KEY = str(os.getenv("GROQ_API_KEY", ""))

logger = logging.getLogger("uvicorn")


class LLM:
    """Class to interact with the LLM API."""

    def __init__(self):
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=GROQ_API_KEY,
            model_name="llama-3.1-8b-instant",
        )

    def extract_job_from_page_data(
        self,
        page_data: str,
        source: str,
        company: str,
        role: str,
        location: str,
    ) -> dict[str, str]:
        """Extract job details from the url."""
        try:
            chain_extract = (
                PromptTemplate(template=EXTRACTJOB_FROM_PAGE_DATA_TEMPLATE) | self.llm
            )
            response: str = chain_extract.invoke(
                {
                    "page_data": page_data,
                    "levels_fyi_page_data": scrape_levels_fyi(
                        company=company,
                        role=role,
                        location=location,
                    ),
                    "source": source,
                }
            ).content
            return json.loads(response[8:-4])
        except Exception as e:
            logger.error(f"Error extracting job details: {e}")
            return {}
