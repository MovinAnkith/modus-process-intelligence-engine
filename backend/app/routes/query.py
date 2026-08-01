from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/query", tags=["query"])


@router.get("/top-ai-potential", response_model=list[schemas.ProcessOut])
def top_ai_potential(organization_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """'Show the 10 processes with highest AI potential.'"""
    return (
        db.query(models.Process)
        .join(models.ProcessAnalysis)
        .filter(models.Process.organization_id == organization_id)
        .filter(models.ProcessAnalysis.automation_potential == "High")
        .limit(limit)
        .all()
    )


@router.get("/human-led", response_model=list[schemas.ProcessOut])
def human_led(organization_id: int, db: Session = Depends(get_db)):
    """'Which processes should remain predominantly human-led?'"""
    return (
        db.query(models.Process)
        .join(models.ProcessAnalysis)
        .filter(models.Process.organization_id == organization_id)
        .filter(models.ProcessAnalysis.automation_potential == "Low")
        .all()
    )


@router.get("/by-category-summary")
def category_summary(organization_id: int, db: Session = Depends(get_db)):
    """Aggregate counts of automation potential per category - computed on
    the fly from stored structured data, no LLM call needed."""
    rows = (
        db.query(
            models.Process.category,
            models.ProcessAnalysis.automation_potential,
            func.count(models.Process.id),
        )
        .join(models.ProcessAnalysis)
        .filter(models.Process.organization_id == organization_id)
        .group_by(models.Process.category, models.ProcessAnalysis.automation_potential)
        .all()
    )
    summary: dict[str, dict[str, int]] = {}
    for category, potential, count in rows:
        summary.setdefault(category, {})[potential] = count
    return summary


@router.get("/{process_id}/evidence", response_model=list[schemas.EvidenceOut])
def process_evidence(process_id: int, db: Session = Depends(get_db)):
    """'Show me the research supporting Process 37.'"""
    return db.query(models.Evidence).filter(models.Evidence.process_id == process_id).all()
