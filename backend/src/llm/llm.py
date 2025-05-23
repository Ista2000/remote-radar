import json
import logging
import os
import traceback
from typing import Optional
from dotenv import load_dotenv
from langchain_core.output_parsers import (
    PydanticOutputParser,
    JsonOutputParser,
    StrOutputParser,
)
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from groq import RateLimitError
from pydantic import BaseModel, Field

from ..constants import ROLES
from ..scrapers.levels_fyi import scrape_levels_fyi
from .prompts import *

load_dotenv()

GROQ_API_KEY = str(os.getenv("GROQ_API_KEY", ""))
LLM_MODELS = json.loads(
    str(os.getenv("LLM_MODELS", '["llama-3.1-70b-versatile", "llama-3.1-8b-instant"]'))
)

logger = logging.getLogger("uvicorn")


class Job(BaseModel):
    description: str = Field(
        description="Description of the job prettified with HTML tags like <b>, <em>, etc."
    )
    required_experience: Optional[int] = Field(
        description="Minimum years of required experience for the job"
    )
    salary_min: Optional[int] = Field(description="Minimum salary offered by the job")
    salary_max: Optional[int] = Field(description="Maximum salary offered by the job")
    salary_currency: Optional[str] = Field(
        description="Currency of the salary offered by the job"
    )
    salary_from_levels_fyi: bool = Field(
        description="Did the salary need to be fetched from levels.fyi"
    )
    remote: bool = Field(description="Is the job remotely available")


class LLM:
    """Class to interact with the LLM API."""

    def __init__(self) -> None:
        self.llms = [
            ChatGroq(  # type: ignore[call-arg]
                temperature=0,
                groq_api_key=GROQ_API_KEY,
                model_name=model_name,
            )
            for model_name in LLM_MODELS
        ]

    def extract_job_from_page_data(
        self,
        page_data: str,
        source: str,
    ) -> dict[str, str]:
        """Extract job details from the url."""
        for idx, llm in enumerate(self.llms):
            try:
                chain = (
                    PromptTemplate(
                        template=EXTRACT_JOB_FROM_PAGE_DATA_TEMPLATE,
                        input_variables=["page_data", "source"],
                    )
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
                if idx == len(self.llms) - 1:
                    logger.error(
                        f"Rate limit hit for all models: {traceback.format_exc()}"
                    )
                else:
                    logger.warning(
                        f"Rate limit hit for {LLM_MODELS[idx]}: {traceback.format_exc()}"
                    )
                    logger.warning(f"Falling back to {LLM_MODELS[idx + 1]}")
                continue
            except Exception:
                logger.error(f"Error extracting job details: {traceback.format_exc()}")
                return {}
        return {}

    def extract_skills_from_resume(
        self, resume_data: str, preferred_roles: Optional[list[str]]
    ) -> dict[str, str]:
        """Extract skills from resume"""
        if preferred_roles is None or len(preferred_roles) == 0:
            return {}
        for idx, llm in enumerate(self.llms):
            try:
                return (
                    PromptTemplate(
                        template=EXTRACT_KEYWORDS_FROM_RESUME_TEMPLATE,
                        input_variables=["resume_data", "roles"],
                    )
                    | llm
                    | JsonOutputParser()
                ).invoke(
                    {"resume_data": resume_data, "roles": "\n".join(preferred_roles)}
                )
            except RateLimitError as e:
                if idx == len(self.llms) - 1:
                    logger.error(
                        f"Rate limit hit for all models: {traceback.format_exc()}"
                    )
                else:
                    logger.warning(
                        f"Rate limit hit for {LLM_MODELS[idx]}: {traceback.format_exc()}"
                    )
                    logger.warning(f"Falling back to {LLM_MODELS[idx + 1]}")
                continue
            except Exception:
                logger.error(
                    f"Error extracting keywords from user resume data: {traceback.format_exc()}"
                )
                return {}
        return {}

    def generate_cover_letter(
        self, resume_data: str, job_description: str, company: str, name: str
    ):
        for idx, llm in enumerate(self.llms):
            try:
                return (
                    PromptTemplate(
                        template=GENERATE_COVER_LETTER_TEMPLATE,
                        input_variables=[
                            "resume_data",
                            "job_description",
                            "name",
                            "company",
                        ],
                    )
                    | llm
                    | StrOutputParser()
                ).invoke(
                    {
                        "resume_data": resume_data,
                        "job_description": job_description,
                        "name": name,
                        "company": company,
                    }
                )
            except RateLimitError as e:
                if idx == len(self.llms) - 1:
                    logger.error(
                        f"Rate limit hit for all models: {traceback.format_exc()}"
                    )
                    raise e
                else:
                    logger.warning(
                        f"Rate limit hit for {LLM_MODELS[idx]}: {traceback.format_exc()}"
                    )
                    logger.warning(f"Falling back to {LLM_MODELS[idx + 1]}")
                continue
            except Exception:
                logger.error(
                    f"Error extracting keywords from user resume data: {traceback.format_exc()}"
                )
                return {}
        return {}
