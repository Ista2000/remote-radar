import os

DEFAULT_TOKEN_EXPIRE_MINUTES = 15
STATIC_DIR_PATH = os.path.abspath("static/")

# Roles for which scrapers will scrape the job data. Please keep the list sorted alphabetically.
ROLES = [
    "Software Engineer"
]

# Locations for which scrapers will scrape the job data. Please keep the list sorted alphabetically.
LOCATIONS = {
    "India": [
        "Bengaluru"
    ],
    "United States": [
        "New York",
        "Redmond",
    ]
}

# Sources for which scrapers have been implemented.
# Make sure that the string matches exactly with `source` in the scraper.
# Please keep the list sorted alphabetically.
SOURCES = [
    "LinkedIn"
]
