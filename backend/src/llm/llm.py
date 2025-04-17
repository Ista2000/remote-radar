import json
import logging
import os
import traceback
from typing import Optional
from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser, JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from groq import RateLimitError
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
    ) -> dict[str, str]:
        """Extract job details from the url."""
        for llm in self.llms:
            try:
                chain = (
                    PromptTemplate(template=EXTRACT_JOB_FROM_PAGE_DATA_TEMPLATE)
                    | llm
                    | PydanticOutputParser(pydantic_object=Job)
                )
                response: Job = chain.invoke(
                    {
                        "page_data": page_data,
                        "source": source,
                    }
                )
                return response.model_dump()
            except RateLimitError as e:
                logger.error(f"Error extracting job details: {e}")
                continue
            except Exception:
                logger.error(f"Error extracting job details: {traceback.format_exc()}")
                return {}
        return {}

    def extract_skills_from_resume(
        self, resume_data: str, preferred_roles: list[str]
    ) -> dict[str, str]:
        """Extract skills from resume"""
        for llm in self.llms:
            try:
                return (
                    PromptTemplate(template=EXTRACT_KEYWORDS_FROM_RESUME_TEMPLATE)
                    | llm
                    | JsonOutputParser()
                ).invoke(
                    {"resume_data": resume_data, "roles": "\n".join(preferred_roles)}
                )
            except RateLimitError as e:
                logger.error(f"Error extracting keywords from user resume data: {e}")
                continue
            except Exception:
                logger.error(
                    f"Error extracting keywords from user resume data: {traceback.format_exc()}"
                )
                return {}
        return {}
