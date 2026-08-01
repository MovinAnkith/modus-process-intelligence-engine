from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.analysis_pipeline import analyze_process

router = APIRouter(prefix="/api/processes", tags=["processes"])


@router.post("/", response_model=schemas.ProcessOut)
def create_process(payload: schemas.ProcessCreate, db: Session = Depends(get_db)):
    """
    Creates a new process AND immediately analyzes it via the same pipeline
    used for every seeded process. This endpoint is what a judge hits when
    they add 'Process 101' live during the demo.
    """
    process = models.Process(
        organization_id=payload.organization_id,
        name=payload.name,
        category=payload.category,
        description=payload.description,
    )
    db.add(process)
    db.commit()
    db.refresh(process)

    analyzed = analyze_process(db, process)
    return analyzed


@router.get("/", response_model=list[schemas.ProcessOut])
def list_processes(
    organization_id: int,
    category: str | None = None,
    automation_potential: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Process).filter(models.Process.organization_id == organization_id)
    if category:
        query = query.filter(models.Process.category == category)
    if automation_potential:
        query = query.join(models.ProcessAnalysis).filter(
            models.ProcessAnalysis.automation_potential == automation_potential
        )
    return query.all()


@router.get("/{process_id}", response_model=schemas.ProcessOut)
def get_process(process_id: int, db: Session = Depends(get_db)):
    process = db.query(models.Process).filter(models.Process.id == process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    return process


@router.post("/{process_id}/reanalyze", response_model=schemas.ProcessOut)
def reanalyze_process(process_id: int, db: Session = Depends(get_db)):
    process = db.query(models.Process).filter(models.Process.id == process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    return analyze_process(db, process)
