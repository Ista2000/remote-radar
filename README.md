# 🛰️ Remote Radar

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/Ista2000/remote-radar/ci.yml)](https://github.com/Ista2000/remote-radar/actions)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![License](https://img.shields.io/github/license/Ista2000/remote-radar)](./LICENSE)

**Remote Radar** is a side project I built to make job hunting way less painful.

I was tired of hopping across a dozen websites, copying descriptions, and writing the same cover letters again and again. So I decided to automate it. This tool scrapes remote jobs from different platforms and (soon!) uses LLMs to generate tailored applications — because job hunting shouldn’t be a full-time job.

---

## 🚀 Features

- 🔎 Aggregates remote jobs from multiple platforms (e.g., LinkedIn, Wellfound)
- 🧠 Auto-generates personalized job applications using LLMs
- 📅 Periodic scraping via background schedulers (every 6 hours)
- 🛡️ Built-in deduplication and database storage
- 🌐 A clean frontend to explore jobs and manage applications
- 🧪 Automated tests with CI and pre-commit hooks to keep things sane
- 🐳 Fully containerized with Docker and Docker Compose
- ⚡ Fast semantic search via ChromaDB and Groq’s LLaMA 3 models

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

```bash
git clone https://github.com/Ista2000/remote-radar.git
cd remote-radar
```

### 2. Install Dependencies

**Backend**
```bash
cd backend
poetry install
```

**Frontend**
```bash
cd frontend
npm install
```

### 3. Configure Environment Variables

**Backend** (`backend/.env`)
```
AUTH_SECRET_KEY=your-secret-key
AUTH_ALGORITHM=HS256
DATABASE_URL=your-db-url
GROQ_API_KEY=your-groq-key
LLM_MODELS=llama3-model-1,llama3-model-2
```

**Frontend** (`frontend/.env.local`)
```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### 4. Run the App

**Backend**
```bash
poetry run uvicorn main:app --reload
```

**Frontend**
```bash
npm run dev
```

---

## 🐳 Docker Setup

### Prerequisites
- Docker
- Docker Compose

### Run with Docker

```bash
docker-compose up --build
```

### Access the App
- Frontend: http://localhost:3000
- Backend (API Docs): http://localhost:8000/docs

---

## 🧾 Docker Compose Overview

```yaml
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

Remote Radar taps into Groq’s super fast LLaMA 3 models (like `llama3-70b-versatile`) for:

- Matching jobs with your resume
- Generating custom job applications
- Extracting important info from job posts

To try it out:
- Plug in your `GROQ_API_KEY` in the `.env`
- Define fallback models using `LLM_MODELS`

---

## 🔄 Background Scraping

Jobs are refreshed every 6 hours with `APScheduler`, all hooked into FastAPI's startup lifecycle.

Want to change how often it scrapes? You can tweak that in `scheduler.py`.

---

## ✅ Commit Quality & Tests

To keep things tidy, every commit should:
- ✅ Pass `pre-commit` hooks (ruff, black, mypy)
- ✅ Include/update backend tests under `backend/tests/`
- ✅ Build cleanly via GitHub Actions

CI will scream at you if you don’t 😉

---

## 📄 License

MIT. Do whatever you want. Just don’t sell it as-is, please.

---

## 🤝 Contributing

This started as a one-person effort, but I’d love help!

You can jump in by:
- 🧼 Adding new sites to scrape
- ✨ Building out features (dashboards, filters, alerts)
- 🧠 Improving the AI integration
- 🪲 Fixing bugs or edge cases
- 📈 Cleaning up the UI or docs

### How to Contribute
- Fork the repo 🍴
- Create an issue to track your work
- Make a feature branch
- Open a PR and tell me what’s new!

---

## 💡 Future Ideas

- 🤝 Find recruiter profiles & craft personalized intros
- 📩 Get email alerts for new matched jobs
- 💼 Dashboard to manage saved/applied jobs
- 🔍 Search and filter through listings
- 🧑‍💻 Score resumes for individual job fits

---

## 🌍 Join the Radar

Tired of mindless scrolling? Same.

That’s why I built **Remote Radar** — to help job seekers (like me) apply smarter, not harder.

Try it, break it, or improve it. Either way, I hope it saves you a few hours and gets you a few callbacks.
