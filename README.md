# 🛰️ Remote Radar

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/Ista2000/remote-radar/ci.yml)](https://github.com/Ista2000/remote-radar/actions)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![License](https://img.shields.io/github/license/Ista2000/remote-radar)](./LICENSE)

**Remote Radar** is an intelligent job aggregator that scrapes remote job listings from multiple websites and uses LLMs to automatically generate tailored job applications. Designed for developers and remote job seekers who want to cut through the noise and apply smarter.

---

## 🚀 Features

- 🔎 Aggregates remote jobs from multiple platforms (e.g., LinkedIn, Wellfound, etc.)
- 🧠 Auto-generates personalized applications using LLMs [WIP]
- 📅 Periodic scraping via background schedulers
- 🛡️ Built-in deduplication and DB storage using SQLAlchemy

---

## 📦 Tech Stack

- **Backend**: FastAPI
- **Scraping**: BeautifulSoup
- **Scheduling**: APScheduler
- **ORM**: SQLAlchemy
- **AI**: Langchain + Groq (LLaMA 3 models)
- **Dev tools**: Poetry, MyPy, Black, Pytest

---

## 🧰 Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/Ista2000/remote-radar.git
cd remote-radar/backend
```

### 2. Install dependencies
```bash
poetry install
```

### 3. Set up environment variables

Create a `.env` file in the `backend` folder:
```env
AUTH_SECRET_KEY=Your API Secret Key to be used for FastAPI
AUTH_ALGORITHM=HS256
API_URL=http://localhost:8000
DATABASE_URL=Database URL to be used
GROQ_API_KEY=Your groq API Key
LLM_MODEL=list of Groq LLM models to be used in order of fallback
```

### 4. Run the app
```bash
poetry run uvicorn main:app --reload
```

---

## 🧪 Running Tests

```bash
poetry run pytest
```

---

## 🧹 Linting & Formatting

This project uses `pre-commit` hooks. To manually run:

```bash
poetry run pre-commit run --all-files --verbose
```

To install pre-commit hooks:

```bash
poetry run pre-commit install
```

---

## 📂 Project Structure

Here is an overview of the directory structure and the purpose of each file/folder:
```
remote-radar/
├── backend/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                        # Entry point for the FastAPI application
│   │   ├── database.py                    # Database configuration and session management
│   │   ├── models.py                      # SQLAlchemy models for database tables
│   │   ├── deps.py                        # Dependency injection for FastAPI routes
│   │   ├── scrapers/                      # Scrapers for fetching job listings
│   │   ├── routers/                       # API route handlers
│   │   ├── llm/                           # LLM-related utilities and integrations
│   ├── tests/                             # Unit and integration tests
│   ├── .env                               # Environment variables for the application
│   ├── .pre-commit-config.yaml            # Pre-commit hooks configuration
│   ├── pyproject.toml                     # Poetry configuration file
│   ├── README.md                          # Project documentation
```


## 🧠 LLM Integration

Remote Radar supports Groq’s blazing fast LLaMA 3 models (like `llama-3.1-70b-versatile`) for generating custom job applications.

You can configure your preferred model in the `.env` or inside the app code.

---

## 📅 Background Scraping

Jobs are scraped automatically every 6 hours using APScheduler via FastAPI lifespan hooks.

---

## 🧪 Commit Checks

Every commit must:
- Pass pre-commit hooks (`ruff`, `black`, `mypy`)
- Include changes under `backend/tests/` to ensure test coverage updates

Failing any of these will block the commit.

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE).

---

## 🤝 Contributing

Feel free to open issues or PRs if you want to improve scraping coverage, add new features, or optimize the LLM integrations.

---

## 💡 Future Ideas
- Fetch recruiter profiles in source and draft messages to them based on resume and job description
- Email alerts for matched job postings
- User dashboard with saved applications
- Web frontend to review and apply manually
