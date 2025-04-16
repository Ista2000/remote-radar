import json
import logging
import os
import traceback
from typing import Optional
from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from ..scrapers.levels_fyi import scrape_levels_fyi
from .prompts import *

load_dotenv()

GROQ_API_KEY = str(os.getenv("GROQ_API_KEY", ""))
LLM_MODEL = json.loads(
    str(os.getenv("LLM_MODEL", '["llama-3.1-70b-versatile", "llama-3.1-8b-instant"]'))
)

logger = logging.getLogger("uvicorn")


class Job(BaseModel):
    description: str = Field(
        "Description of the job prettified with HTML tags like <b>, <em>, etc."
    )
    required_experience: Optional[int] = Field(
        "Minimum years of required experience for the job"
    )
    salary_min: Optional[int] = Field("Minimum salary offered by the job")
    salary_max: Optional[int] = Field("Maximum salary offered by the job")
    salary_currency: Optional[str] = Field("Currency of the salary offered by the job")
    salary_from_levels_fyi: bool = Field(
        "Did the salary need to be fetched from levels.fyi"
    )


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
                parser = PydanticOutputParser(pydantic_object=Job)
                chain_extract = (
                    PromptTemplate(template=EXTRACTJOB_FROM_PAGE_DATA_TEMPLATE)
                    | llm
                    | parser
                )
                response: Job = chain_extract.invoke(
                    {
                        "page_data": page_data,
                        "levels_fyi_page_data": scrape_levels_fyi(
                            company=company,
                            role=role,
                            location=location,
                        ),
                        "source": source,
                    }
                )
                return response.model_dump()
            except Exception:
                logger.error(f"Error extracting job details: {traceback.format_exc()}")
                continue
        return {}
