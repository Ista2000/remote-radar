import json
import logging
import os
import traceback
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

from ..scrapers.levels_fyi import scrape_levels_fyi
from .prompts import *

load_dotenv()

GROQ_API_KEY = str(os.getenv("GROQ_API_KEY", ""))
LLM_MODEL = json.loads(
    str(os.getenv("LLM_MODEL", '["llama-3.1-70b-versatile", "llama-3.1-8b-instant"]'))
)

logger = logging.getLogger("uvicorn")


class LLM:
    """Class to interact with the LLM API."""

    def __init__(self) -> None:
        self.llms = [
            ChatGroq(
                temperature=0,
                groq_api_key=GROQ_API_KEY,
                model_name=model_name,
            )
            for model_name in LLM_MODEL
        ]

    def extract_job_from_page_data(
        self,
        page_data: str,
        source: str,
        company: str,
        role: str,
        location: str,
    ) -> dict[str, str]:
        """Extract job details from the url."""
        for llm in self.llms:
            try:
                chain_extract = (
                    PromptTemplate(template=EXTRACTJOB_FROM_PAGE_DATA_TEMPLATE) | llm
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
            except Exception:
                logger.error(f"Error extracting job details: {traceback.format_exc()}")
                continue
        return {}
