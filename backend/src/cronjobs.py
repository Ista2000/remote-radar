from bs4 import BeautifulSoup
import requests
import logging

logger = logging.getLogger("uvicorn")

def scrape_linkedin_jobs(query="software engineer", location="remote", num_jobs=5):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={location}&f_WT=2&position=1&pageNum=0"

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []

    for job_card in soup.select("ul.jobs-search__results-list li"):
        title_elem = job_card.find("h3")
        company_elem = job_card.find("h4")
        location_elem = job_card.find("span", class_="job-search-card__location")
        link_elem = job_card.find("a", href=True)
        if link_elem is None:
            continue
        job_url = "https://www.linkedin.com/" + '/'.join(link_elem['href'].split('?')[0].split('/')[3:])

        job_response = requests.get(job_url, headers=headers)
        job_soup = BeautifulSoup(job_response.text, "html.parser")
        description_elem = job_soup.find('div', class_='description__text description__text--rich').get_text(strip=True)

        if title_elem and company_elem and link_elem and description_elem:
            # Extract the job URL from the href attribute
            jobs.append({
                "title": title_elem.get_text(strip=True),
                "company": company_elem.get_text(strip=True),
                "location": location_elem.get_text(strip=True) if location_elem else None,
                "url": job_url,
                "description": description_elem,
            })
        if len(jobs) >= num_jobs:
            break

    for job in jobs:
        logger.info(f"\nJob Title: {job['title']}\nCompany: {job['company']}\nLocation: {job['location']}\nURL: {job['url']}\nDescription: {job['description']}\n")