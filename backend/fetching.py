from app.db.database import SessionLocal
from app.services import fetch_github_issues
db = SessionLocal()
fetch_github_issues()  # This fetches issues and calls save_issues_to_db internally
