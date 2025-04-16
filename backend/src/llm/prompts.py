EXTRACTJOB_FROM_PAGE_DATA_TEMPLATE = """
### SCRAPED TEXT FROM WEBSITE:
{page_data}
### INSTRUCTION:
The scraped text is from a job listing page from {source}.
Your job is to extract from the job posting and present the following keys and values in JSON format:
`description`, `required_experience`, `salary_min`, `salary_max`, `salary_currency`, `salary_from_levels_fyi`.
Content of the `description` should be as is but in html with some formatting to prettify it using <hX>, <b>, <em> tags.
`salary_from_levels_fyi` is a boolean indicating whether salary was available at source was was fetched from levels.fyi.
If the salary information is not available then use the following data (data may be null) then set them as null:
### SCRAPED TEXT FROM LEVELS.FYI:
{levels_fyi_page_data}
### VALID JSON (NO PREAMBLE)
### DO NOT OUTPUT ANYTHING APART FROM JSON OBJECT
"""
