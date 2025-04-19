import os

DEFAULT_TOKEN_EXPIRE_MINUTES = 15
STATIC_DIR_PATH = os.path.abspath("static/")

# Roles for which scrapers will scrape the job data. Please keep the list sorted alphabetically.
ROLES = [
    "Software Engineer"
]

# Locations and their LinkedIn GeoIds for which data will be scraped.
# Please keep the list sorted alphabetically.
LOCATION_GEO_IDS_FOR_LINKEDIN = {
    "India": {
        "Bengaluru": 105214831,
        "Hyderabad": 105556991,
        # "Chennai": 4301223432,
        # "Pune": 4318592375,
        # "Delhi": 4208914352,
    },
    "United States": {
        "San Francisco Bay Area": 90000084,
        "New York": 105080838,
        # "Seattle": 105147929,
        # "Austin": 105184003,
        # "Los Angeles": 105112890,
    }
}

# Sources for which scrapers have been implemented.
# Make sure that the string matches exactly with `source` in the scraper.
# Please keep the list sorted alphabetically.
SOURCES = [
    "LinkedIn"
]
