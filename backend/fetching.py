import logging
from app.db.database import SessionLocal
from app.services import fetch_github_issues, save_issues_to_db

db = SessionLocal()
issues = fetch_github_issues()

if issues:
    save_issues_to_db(db, issues, "elastic/kibana")
    logging.info(f"✅ Successfully stored {len(issues)} issues in PostgreSQL.")
else:
    logging.error(f"❌ No issues were fetched, storage skipped.")
