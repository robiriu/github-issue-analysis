from app.db.database import SessionLocal
from app.services import fetch_github_issues, generate_repository_report

db = SessionLocal()

# ✅ Fetch GitHub issues and save them
fetch_github_issues()  

# ✅ Trigger report refresh **immediately**, without waiting for full completion
report_text = generate_repository_report(db)
print(report_text)  # ✅ Display latest report in terminal/logs
