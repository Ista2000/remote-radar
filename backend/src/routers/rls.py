from fastapi import APIRouter

from ..constants import LOCATION_GEO_IDS_FOR_LINKEDIN, ROLES, SOURCES


router = APIRouter(
    prefix="/rls",
    tags=["rls"],
)

@router.get("/")
def get_valid_roles_locations_sources():
    return {
        "roles": ROLES,
        "locations": dict(
            (country, list(city_dict.keys())) for country, city_dict in LOCATION_GEO_IDS_FOR_LINKEDIN.items()
        ),
        "sources": SOURCES,
    }
