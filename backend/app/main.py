from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import processes, query, organizations

# Creates tables on startup if they don't exist (in addition to db/schema.sql)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MODUS 100 Process Intelligence Engine",
    description="Analyzes business processes for AI transformation opportunity, at scale.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(organizations.router)
app.include_router(processes.router)
app.include_router(query.router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "modus-process-engine"}
