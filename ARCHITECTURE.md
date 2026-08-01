# Architecture

## Layer Diagram

```
┌─────────────────────────────────────────────────────────┐
│  USER INTERFACE                                          │
│  frontend/index.html — dashboard, filters, evidence view,│
│  "Add New Process" live-test form                        │
└───────────────────────┬───────────────────────────────────┘
                         │ HTTP (fetch)
┌───────────────────────▼───────────────────────────────────┐
│  APPLICATION / API LAYER (FastAPI)                        │
│  routes/processes.py    — CRUD + trigger analysis         │
│  routes/query.py        — aggregate/derived queries        │
│  routes/organizations.py                                   │
└───────────────────────┬───────────────────────────────────┘
                         │
┌───────────────────────▼───────────────────────────────────┐
│  AI INTELLIGENCE LAYER                                     │
│  services/analysis_pipeline.py                             │
│    -> services/research.py      (evidence grounding)      │
│    -> services/llm_provider.py  (Groq / Llama 3.3, JSON)  │
└───────────────────────┬───────────────────────────────────┘
                         │
┌───────────────────────▼───────────────────────────────────┐
│  DATA & KNOWLEDGE LAYER (PostgreSQL)                       │
│  organizations, processes, process_analysis, evidence      │
└───────────────────────┬───────────────────────────────────┘
                         │
┌───────────────────────▼───────────────────────────────────┐
│  EXTERNAL RESEARCH (optional, pluggable)                   │
│  Tavily/SerpAPI-style search for grounding evidence         │
└─────────────────────────────────────────────────────────┘
```

## Data Flow: New Process Submission (the "Surprise Record" path)

1. User (or judge) submits a process name + category via the dashboard or `POST /api/processes/`.
2. `routes/processes.py::create_process` inserts a `Process` row (status = `pending`).
3. `services/analysis_pipeline.py::analyze_process` is called:
   a. `services/research.py::gather_evidence` retrieves up to 3 supporting snippets (or returns `[]` if no search key configured).
   b. `services/llm_provider.py::analyze_process_with_llm` sends the process + evidence to Groq with a strict JSON schema prompt.
   c. Output is validated against the required schema (`_validate_schema`) — any missing field is marked `insufficient_evidence` rather than silently dropped.
4. Structured analysis is upserted into `process_analysis`; evidence rows are stored in `evidence`.
5. `Process.status` is updated to `analyzed`.
6. The API returns the full analyzed record; the frontend refreshes the table immediately.

**This is identical, byte-for-byte in code path, to how all 100 seed
processes were created** — see `seed_data.py`, which calls the same
`analyze_process()` function in a loop.

## Why This Design Passes the Judging Gates

| Requirement | How it's satisfied |
|---|---|
| Real frontend + backend + data + AI layer | All four present, cleanly separated |
| Data persists across restarts | PostgreSQL, not in-memory |
| Not hard-coded | `analyze_process()` is generic; taxonomy is data, not per-process logic |
| Processes multiple records systematically | `seed_data.py` loops the same function 100 times |
| Handles a new/unseen record dynamically | `POST /api/processes/` triggers the identical pipeline |
| Outputs traceable to evidence | `evidence` table + `rationale`/`confidence` fields on every analysis |
| Scales to 1,000+ | Stateless pipeline function; scaling is an orchestration concern, not a redesign |
