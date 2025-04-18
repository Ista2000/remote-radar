from fastapi import APIRouter

from ..constants import ROLES, LOCATIONS, SOURCES


router = APIRouter(
    prefix="/rls",
    tags=["rls"],
)

@router.get("/")
def get_valid_roles_locations_sources():
    return {
        "roles": ROLES,
        "locations": LOCATIONS,
        "sources": SOURCES,
    }
