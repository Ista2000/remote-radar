EXTRACT_JOB_FROM_PAGE_DATA_TEMPLATE = """
### SCRAPED TEXT FROM WEBSITE:
{page_data}
### INSTRUCTION:
The scraped text is from a job listing page from {source}.
Your job is to extract from the job posting and present the following keys and values in JSON format:
`description`, `required_experience`, `salary_min`, `salary_max`, `salary_currency`, `salary_from_levels_fyi`, `remote`.
`description` should clearly communicate everything about the job, responsibilities, required qualifications, preferred qualifications and necessary disclaimers.
Modify the `description` as an HTML document by adding <h1> tags, A LOT OF <b>, <em> and <p> tags, and <ul> and <li> tags for listing but DO NOT CHANGE THE TEXT CONTENT.
`salary_from_levels_fyi` should be false.
`required_experience` is the minimum number of years of experience required for the job.
`remote` is a Boolean value representing whether the job is available remotely.
### VALID JSON (NO PREAMBLE)
### DO NOT OUTPUT ANYTHING APART FROM JSON OBJECT
"""


EXTRACT_KEYWORDS_FROM_RESUME_TEMPLATE = """
### USER RESUME DATA:
{resume_data}
### INSTRUCTION:
The user resume text is provided parsed using a pdfplumber.
Your job is to extract all the relevant keywords relevant for the following roles:
{roles}
The output should be a one line json representing role as key and keywords as values.
The values should contain at most 100 and at least 5 unique keywords ranked from most relevant to least.
### VALID JSON (NO PREAMBLE)
### DO NOT OUTPUT ANYTHING APART FROM JSON OBJECT
"""

GENERATE_COVER_LETTER_TEMPLATE = """
### USER RESUME DATA:
{resume_data}

### JOB DESCRIPTION:
{job_description}

### MY NAME IS {name}

### INSTRUCTION:
Generate a personalized cover letter email for a recruiter from {company} regarding a job opening whose job description is provided above.
The cover letter should be personalized using the resume data and job description.
The cover letter should have less than 200 words.

### NO PREAMBLE
"""
