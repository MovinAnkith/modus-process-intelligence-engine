# NorthStar Retail — 100 Process Intelligence Engine

Built for the MODUS Enterprise AI Build Challenge — Assignment 2.

An AI application that systematically analyzes ~100 real retail/e-commerce
business processes for AI transformation opportunity — automation
potential, risks, benefits, and evidence-backed rationale — and can
analyze any **new** process submitted live, through the exact same
pipeline used to build the original 100.

---

## Architecture

```
React-free HTML/JS Dashboard  →  FastAPI Backend  →  Groq LLM (Llama 3.3)
      (frontend/)                  (backend/app/)         ↕
                                         ↓            Research/Evidence
                                  PostgreSQL              (optional)
                                  (db/schema.sql)
```

- **UI**: Single-page dashboard (`frontend/index.html`) — no build step, opens directly in a browser.
- **API layer**: FastAPI (`backend/app/routes/`) — REST endpoints for processes, organizations, and aggregate queries.
- **AI intelligence layer**: `backend/app/services/analysis_pipeline.py` — the single reusable function every process (seeded or live) passes through.
- **Data layer**: PostgreSQL — processes, structured analysis, and evidence are all persisted and survive restarts.
- **External research**: `backend/app/services/research.py` — optional web search grounding (pluggable provider).

See `ARCHITECTURE.md` for the detailed data flow diagram.

---

## Setup

### 1. Prerequisites
- Python 3.10+
- PostgreSQL running locally (or a free-tier hosted instance e.g. Render/Railway/Supabase)
- A free Groq API key from [console.groq.com](https://console.groq.com)

### 2. Database
```bash
createdb modus_process_engine
psql -d modus_process_engine -f db/schema.sql
```

### 3. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: set DATABASE_URL and GROQ_API_KEY

uvicorn app.main:app --reload --port 8000
```

### 4. Seed the 100 processes
In a second terminal (with venv active):
```bash
cd backend
python -m app.seed_data
```
This creates the "NorthStar Retail Group" organization and analyzes all
100 processes one by one through the live pipeline (not hard-coded rows).

### 5. Frontend
Just open `frontend/index.html` in a browser (backend must be running on
`localhost:8000`). No build step required.

---

## The "Surprise Record" Test

Click **"+ Add New Process"** in the dashboard, enter any process name and
category (e.g. "Return Fraud Detection", "Order Management"), and submit.
It runs through `POST /api/processes/` → `analyze_process()` — the exact
same function used for all 100 seeded processes. No code changes, no
manual intervention.

---

## Key API Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /api/processes/` | Add + analyze a new process (used for live surprise test) |
| `GET /api/processes/?organization_id=1` | List processes, filterable by category / automation_potential |
| `GET /api/query/top-ai-potential?organization_id=1` | Top processes by AI potential |
| `GET /api/query/human-led?organization_id=1` | Processes that should stay human-led |
| `GET /api/query/{process_id}/evidence` | Research evidence backing a specific process |
| `GET /api/query/by-category-summary?organization_id=1` | Aggregate counts per category |

---

## Libraries & Licenses (all free/open-source)

| Library | License | Purpose |
|---|---|---|
| FastAPI | MIT | API framework |
| SQLAlchemy | MIT | ORM |
| PostgreSQL | PostgreSQL License (permissive) | Database |
| Groq SDK | MIT | LLM API client (free tier) |
| psycopg2-binary | LGPL | Postgres driver |

If Groq's free tier becomes unavailable, `llm_provider.py` is a single
abstracted module — swapping to another OpenAI-compatible free-tier
provider (e.g. Cerebras, local Ollama model) requires changing only that
file.

---

## What I Personally Built vs AI-Assisted

I designed the database schema, the layered architecture (routes /
services / models separation), the analysis pipeline contract, and the
process taxonomy. AI coding assistants (Claude, GitHub Copilot) were used
to accelerate writing boilerplate code (route handlers, SQLAlchemy model
definitions) based on my design decisions — I can explain every component
in this repository.

---

## If Given 1,000 Processes Instead of 100

No architectural change is required for correctness — `analyze_process()`
is already data-driven and stateless per record. For performance at that
scale, I would:
1. Move seeding to an async task queue (Celery/background tasks) to parallelize LLM calls.
2. Add pagination to `GET /api/processes/` (already indexed by category/organization).
3. Cache aggregate query results briefly to avoid recomputation on every dashboard load.

The core pipeline itself does not change — only the orchestration around it scales.
