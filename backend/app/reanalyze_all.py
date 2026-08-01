"""
Re-runs analyze_process() on every existing process - used after adding
evidence grounding (SEARCH_API_KEY) so all 101 processes get re-analyzed
with real research backing them.
"""
from app.database import SessionLocal
from app import models
from app.services.analysis_pipeline import analyze_process


def reanalyze_all():
    db = SessionLocal()
    try:
        processes = db.query(models.Process).all()
        print(f"Re-analyzing {len(processes)} processes with evidence grounding...")
        for i, process in enumerate(processes, start=1):
            analyze_process(db, process)
            print(f"  [{i}/{len(processes)}] Re-analyzed: {process.name}")
        print("Re-analysis complete.")
    finally:
        db.close()


if __name__ == "__main__":
    reanalyze_all()
