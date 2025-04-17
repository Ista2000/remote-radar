EXTRACT_JOB_FROM_PAGE_DATA_TEMPLATE = """
### SCRAPED TEXT FROM WEBSITE:
{page_data}
### INSTRUCTION:
The scraped text is from a job listing page from {source}.
Your job is to extract from the job posting and present the following keys and values in JSON format:
`description`, `required_experience`, `salary_min`, `salary_max`, `salary_currency`, `salary_from_levels_fyi`.
Content of the `description` should be as is but in html with some formatting to prettify it using <hX>, <b>, <em> tags.
`salary_from_levels_fyi` is a boolean indicating whether salary was available at source was was fetched from levels.fyi.
`required_experience` is the minimum number of years of experience required for the job.
### VALID JSON (NO PREAMBLE)
### DO NOT OUTPUT ANYTHING APART FROM JSON OBJECT
"""
EXTRACT_KEYWORDS_FROM_RESUME_TEMPLATE = """
### USER RESUME DATA
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
