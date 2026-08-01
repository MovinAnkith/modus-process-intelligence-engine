from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/organizations", tags=["organizations"])


@router.post("/", response_model=schemas.OrganizationOut)
def create_organization(payload: schemas.OrganizationCreate, db: Session = Depends(get_db)):
    org = models.Organization(name=payload.name, industry=payload.industry)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@router.get("/", response_model=list[schemas.OrganizationOut])
def list_organizations(db: Session = Depends(get_db)):
    return db.query(models.Organization).all()
