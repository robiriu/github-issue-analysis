from fastapi import FastAPI, Depends
from app.routes import router
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services import generate_repository_report

# Initialize FastAPI app
app = FastAPI(title="GitHub Issue Analysis", description="Ranks repositories based on issue-handling efficiency")

app.include_router(router)

@app.get("/repository-report")
def get_repository_report(db: Session = Depends(get_db)):
    """API endpoint to fetch the repository ranking report."""
    report_text = generate_repository_report(db)
    return {"report": report_text}

# Health check endpoint
@app.get("/health")
def health_check():
    """Simple health check to verify API is running."""
    return {"status": "ok"}
