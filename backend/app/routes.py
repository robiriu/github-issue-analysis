from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services import generate_repository_report

router = APIRouter()

@router.get("/")
def root():
    return {"message": "GitHub Issue Management API is running!"}

@router.get("/repository-report")
def repository_report(db: Session = Depends(get_db)):
    """Generates repository ranking report."""
    return generate_repository_report(db)
