# AI Campus Assistant

A hackathon-ready campus information assistant built with Python, Flask, SQLite/MySQL-compatible SQLAlchemy, and an optional local Ollama LLM.

## Features
- Natural-language campus Q&A
- Automatic intent/category detection
- Separate conversation threads with auto titles
- Context-aware follow-up questions
- Source-backed answers
- Campus data for exams, faculty, rooms, events, notices, FAQs
- Admin dashboard to add/update campus records
- REST API endpoints
- Works without an AI API key using a deterministic retrieval fallback
- Optional Ollama integration for richer conversational responses

## Run locally

```bash
cd ai_campus_assistant
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python seed.py
python run.py
```

Open http://127.0.0.1:5000

Demo admin login: `admin` / `admin123` (change it before deployment).

## Optional AI
Install Ollama separately and run a model such as `llama3.2` locally, then set:

```env
OLLAMA_ENABLED=true
OLLAMA_MODEL=llama3.2
OLLAMA_URL=http://localhost:11434
```

The application still works if Ollama is unavailable.

## MySQL
Set `DATABASE_URL` in `.env`, for example:

```env
DATABASE_URL=mysql+pymysql://root:password@localhost/campus_assistant
```

## Project structure

```text
app/
  __init__.py
  models.py
  routes.py
  assistant.py
  templates/
  static/
seed.py
run.py
requirements.txt
.env.example
```

## Important
The included campus information is **demo data**. Replace it with verified institutional information before presenting it as real campus data.
