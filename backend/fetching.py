#!/usr/bin/env python3
import logging
from app.db.database import SessionLocal
from app.services import fetch_github_issues, generate_repository_report

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.info("Starting GitHub issues fetch...")
    fetch_github_issues()
    logging.info("Finished fetching issues.")

    # Generate and print repository report using the latest data
    db = SessionLocal()
    logging.info("Generating repository report...")
    report = generate_repository_report(db)
    print(report)

if __name__ == "__main__":
    main()
