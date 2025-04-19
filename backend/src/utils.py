from datetime import datetime
from dateutil.relativedelta import relativedelta
import bcrypt
import re

from .constants import LOCATION_GEO_IDS_FOR_LINKEDIN


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        bytes(plain_password, encoding="utf-8"),
        bytes(hashed_password, encoding="utf-8"),
    )


def hash_password(password: str) -> str:
    return str(
        bcrypt.hashpw(
            bytes(password, encoding="utf-8"),
            bcrypt.gensalt(),
        ),
        encoding="utf-8",
    )


def get_posted_date(relative_date_str: str) -> datetime:
    # Remove "Reposted" or "Updated" words if present, and normalize the string
    relative_date_str = relative_date_str.replace("Reposted", "").strip()

    # Patterns for recognizing common time intervals
    time_patterns = {
        "minute": r"(\d+)\s*(minute|min|mins?|m)",
        "hour": r"(\d+)\s*(hour|hrs?|h)",
        "day": r"(\d+)\s*(day|d|days?)",
        "week": r"(\d+)\s*(week|w|weeks?)",
        "month": r"(\d+)\s*(month|mo|months?)",
        "year": r"(\d+)\s*(year|yr|years?)",
    }

    # Try matching the patterns
    for unit, pattern in time_patterns.items():
        match = re.search(pattern, relative_date_str)
        if match:
            value = int(match.group(1))
            if unit == "minute":
                return datetime.now() - relativedelta(minutes=value)
            elif unit == "hour":
                return datetime.now() - relativedelta(hours=value)
            elif unit == "day":
                return datetime.now() - relativedelta(days=value)
            elif unit == "week":
                return datetime.now() - relativedelta(weeks=value)
            elif unit == "month":
                return datetime.now() - relativedelta(months=value)
            elif unit == "year":
                return datetime.now() - relativedelta(years=value)

    # If no matching patterns, return the current time (Fallback case)
    return datetime.now()

def get_normalized_locations_list_string():
    return [f"{city}, {country}" for country, city_dict in LOCATION_GEO_IDS_FOR_LINKEDIN.items() for city in city_dict.keys()]
