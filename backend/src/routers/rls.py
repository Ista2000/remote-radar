from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..constants import LOCATION_GEO_IDS_FOR_LINKEDIN, ROLES, SOURCES


router = APIRouter(
    prefix="/rls",
    tags=["rls"],
)


class RLSResponseModel(BaseModel):
    roles: list[str] = Field(
        description="List of all supported roles for which jobs are scraped by Remote Radar.",
        examples=["Software Engineer", "Engineering Manager"],
    )
    locations: dict[str, list[str]] = Field(
        description="Mapping of country → list of cities for which jobs are scraped by Remote Radar.",
        examples=[{"India": ["Bengaluru", "Hyderabad"]}],
    )
    sources: list[str] = Field(
        description="List of all sources supported by Remote Radar for scraping.",
        examples=["Linkedin"],
    )


@router.get(
    "/",
    response_model=RLSResponseModel,
    summary="What's supported?",
    description="Get all roles, locations and sources that are supported by Remote Radar.",
    response_description="All roles, locations and sources that are supported by Remote Radar.",
)
def get_valid_roles_locations_sources():
    return {
        "roles": ROLES,
        "locations": dict(
            (country, list(city_dict.keys()))
            for country, city_dict in LOCATION_GEO_IDS_FOR_LINKEDIN.items()
        ),
        "sources": SOURCES,
    }
