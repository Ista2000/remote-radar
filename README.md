# 🛰️ Remote Radar

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/Ista2000/remote-radar/ci.yml)](https://github.com/Ista2000/remote-radar/actions)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![License](https://img.shields.io/github/license/Ista2000/remote-radar)](./LICENSE)

**Remote Radar** is an intelligent job aggregator that scrapes remote job listings from multiple websites and uses LLMs to automatically generate tailored job applications. It’s built for developers and remote job seekers who want to **apply smarter, not harder.**

---

## 🚀 Features

- 🔎 Aggregates remote jobs from multiple platforms (e.g., LinkedIn, Wellfound)
- 🧠 Auto-generates personalized job applications using LLMs (WIP)
- 📅 Periodic scraping via background schedulers (every 6 hours)
- 🛡️ Built-in deduplication and database storage
- 🌐 Beautiful frontend to explore jobs and manage applications
- 🧪 Automated tests with CI and strict commit quality control
- 🐳 Fully containerized with Docker and Docker Compose
- ⚡ Lightning-fast job matching via ChromaDB and Groq’s LLaMA 3 models

---

## 📦 Tech Stack

| Layer       | Tools                                                                 |
|-------------|------------------------------------------------------------------------|
| **Frontend**| Next.js, Chakra UI                                                     |
| **Backend** | FastAPI, SQLAlchemy, APScheduler                                       |
| **Scraping**| BeautifulSoup                                                          |
| **AI/LLM**  | LangChain, Groq (LLaMA 3), ChromaDB                                     |
| **DevOps**  | Docker, Docker Compose, Poetry, Pre-commit, Pytest, GitHub Actions     |

---

## 🧰 Getting Started

### 1. Clone the Repository

```
git clone https://github.com/Ista2000/remote-radar.git
cd remote-radar
```
### 2. Install Dependencies
Backend
```
cd backend
poetry install
```
Frontend
```
cd frontend
npm install
```
### 3. Configure Environment Variables
Backend (`backend/.env`)
```
AUTH_SECRET_KEY=your-secret-key
AUTH_ALGORITHM=HS256
DATABASE_URL=your-db-url
GROQ_API_KEY=your-groq-key
LLM_MODELS=llama3-model-1,llama3-model-2
```
Frontend (frontend/.env.local)
```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```
### 4. Run the App
Backend
```
poetry run uvicorn main:app --reload
```
Frontend
```
npm run dev
```

---

## 🐳 Docker Setup
### Prerequisites
- Docker
- Docker Compose

### Run with Docker
```
docker-compose up --build
```
### Access the App
- Frontend: http://localhost:3000
- Backend (API Docs): http://localhost:8000/docs

---

## 🧾 Docker Compose Overview

```
services:
  backend:
    build:
      context: ./backend
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

  frontend:
    build:
      context: ./frontend
    ports:
      - "3000:3000"
    env_file:
      - .env.local
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: remote_radar
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
```

---

## 📁 Project Structure

```
remote-radar/
├── backend/
│   ├── src/
│   │   ├── main.py                # FastAPI entrypoint
│   │   ├── database.py            # DB config & session
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── deps.py                # Dependency injection
│   │   ├── utils.py               # Helper functions
│   │   ├── scrapers/              # Job scraping logic
│   │   ├── routers/               # API routes
│   │   ├── llm/                   # LLM utilities
│   ├── tests/                     # Backend tests
│   ├── Dockerfile
│   ├── .env                       # Need to create
│   └── pyproject.toml
├── frontend/
│   ├── app/                       # Next.js application
│   │   ├── auth/                  # Login/Sign-up pages
│   │   ├── components/            # Reusable UI components
│   │   ├── context/               # React contexts
│   │   ├── hooks/                 # Custom hooks
│   ├── public/                    # Static files
│   ├── Dockerfile
│   ├── .env.local                 # Need to create
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## 🧠 LLM Integration
Remote Radar uses Groq’s blazing fast LLaMA 3 models (e.g., `llama3-70b-versatile`) for:
- Resume matching
- Personalized application generation
- Keyword extraction from job descriptions

To use:
- Add your `GROQ_API_KEY` to `.env`
- Specify fallback models via `LLM_MODELS`

---

## 🔄 Background Scraping
Jobs are scraped every 6 hours using `APScheduler` hooked into FastAPI's lifespan events.

Want to change the frequency? Modify the `interval_seconds` in `scheduler.py`.

## ✅ Commit Quality & Tests
Every commit must:
- ✅ Pass pre-commit checks (ruff, black, mypy)
- ✅ Include/Update backend tests under backend/tests/
- ✅ Build cleanly in CI via GitHub Actions

Failing any of these will block the commit.

---

## 📄 License
Licensed under the [MIT License](https://github.com/Ista2000/remote-radar/blob/main/LICENSE).

---

## 🤝 Contributing
We welcome contributions of all kinds! 🚀

You can help by:
- 🧼 Improving scraping coverage
- ✨ Adding new features or dashboards
- 🤖 Enhancing LLM usage
- 🪲 Reporting bugs
- 📈 Improving documentation

### How to Contribute
- Fork the repo 🍴
- Create an issue to link with your contribution
- Create a feature branch 🔧
- Open a PR with a clear description ✅
---
## 💡 Future Ideas
- 🤝 Match recruiter profiles and draft personalized messages
- 📩 Email alerts for personalized job matches
- 💼 Dashboard with saved & applied jobs
- 🔍 Search and filtering for job listings
- 🧑‍💻 Resume analysis and scoring

## 🌍 Join the Radar
Tired of endlessly scrolling job boards? Let **Remote Radar** do the heavy lifting.

Stay focused on what matters — **getting the right job, faster**.