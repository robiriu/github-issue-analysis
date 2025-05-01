import logging
import requests
from sqlalchemy.orm import Session
from app.config.settings import GITHUB_TOKEN, GITHUB_REPO, LLM_API_KEY, LLM_MODEL
from app.models import Repository, Issue
from app.db.database import get_db

# Initialize logging
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def fetch_github_issues():
    """Fetches issues from GitHub and stores them in PostgreSQL."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues?state=all"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    params = {"per_page": 100, "page": 1}

    all_issues = []
    while params["page"] <= 99:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            issues = response.json()

            if not issues:
                break

            all_issues.extend(issues)
            logging.info(f"✅ Fetched {len(issues)} issues from page {params['page']} of {GITHUB_REPO}")
            params["page"] += 1

        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Error fetching issues: {e}")
            return []

    logging.info(f"✅ Total issues fetched: {len(all_issues)}")

    # Store fetched issues in PostgreSQL
    db = next(get_db())
    save_issues_to_db(db, all_issues, GITHUB_REPO)

    return all_issues

def fetch_repository_metadata(repo_name):
    """Fetches repository metadata from GitHub."""
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.get(f"https://api.github.com/repos/{repo_name}", headers=headers)
    
    if response.status_code != 200:
        logging.error(f"❌ Failed to fetch repository metadata for {repo_name}: {response.status_code}")
        return None

    return response.json()

def save_issues_to_db(db: Session, issues, repo_name):
    """Stores GitHub issues and repository metadata into PostgreSQL."""
    try:
        if not issues:
            logging.warning(f"⚠️ No issues found for {repo_name}. Skipping save.")
            return

        logging.info(f"✅ Preparing to save {len(issues)} issues for {repo_name}")

        # ✅ Fetch repository metadata
        repo_info = fetch_repository_metadata(repo_name)
        if not repo_info:
            return

        # ✅ Ensure repository entry exists in PostgreSQL
        repo = db.query(Repository).filter(Repository.name == repo_name).first()
        if not repo:
            repo = Repository(
                name=repo_name,
                stars=int(repo_info.get("stargazers_count", 0)),
                language=repo_info.get("language") if repo_info.get("language") else "Unknown",
                issue_count=len(issues)
            )
            db.add(repo)
            db.commit()
            logging.info(f"✅ Repository {repo_name} saved with {repo.stars} stars and language: {repo.language}")

        # ✅ Insert issues into PostgreSQL
        for issue_data in issues:
            issue_body = issue_data.get("body", "")
            llm_analysis = analyze_issue_with_llm(issue_body) if issue_body else "No description available"

            issue = Issue(
                repo_id=repo.id,
                title=issue_data["title"],
                description=issue_body,
                created_at=issue_data["created_at"],
                closed_at=issue_data.get("closed_at"),
                status="open" if issue_data["state"] == "open" else "closed",
                llm_analysis=llm_analysis
            )
            db.add(issue)

        # ✅ Commit data and verify count
        db.commit()
        stored_count = db.query(Issue).filter(Issue.repo_id == repo.id).count()
        logging.info(f"🛠 DB Check: {stored_count}/{len(issues)} issues stored for {repo_name}")

    except requests.exceptions.RequestException as req_err:
        logging.error(f"❌ Error fetching repository metadata: {req_err}")
    except Exception as e:
        logging.error(f"❌ Error saving issues: {e}")

def analyze_issue_with_llm(issue_description):
    """Uses Hugging Face API to assess issue clarity."""
    headers = {"Authorization": f"Bearer {LLM_API_KEY}"}
    payload = {"inputs": issue_description}

    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{LLM_MODEL}",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        response_data = response.json()
        
        logging.info(f"LLM Full Response: {response_data}")
        
        if "summary_text" not in response_data[0]:
            logging.error(f"Unexpected LLM response structure: {response_data}")
            return "Analysis failed"

        return response_data[0].get("summary_text", "No analysis available")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error analyzing issue with LLM: {e}")
        return "Analysis failed"

def rank_repositories(db: Session):
    """Ranks repositories based on issue resolution efficiency."""
    repositories = db.query(Repository).all()
    repo_scores = {}

    for repo in repositories:
        issues = db.query(Issue).filter(Issue.repo_id == repo.id).all()

        total_issues = len(issues)
        resolved_issues = sum(1 for issue in issues if issue.status == "closed")
        avg_resolution_time = sum((issue.closed_at - issue.created_at).days for issue in issues if issue.closed_at) / max(1, resolved_issues)

        if total_issues > 0:
            score = (resolved_issues / max(1, total_issues)) * 0.5 + (1 / max(1, avg_resolution_time)) * 0.5
        else:
            score = 0    
        repo_scores[repo.name] = round(score, 3)

    ranked_repos = sorted(repo_scores.items(), key=lambda x: x[1], reverse=True)
    logging.info(f"Repository rankings generated: {ranked_repos}")
    
    return ranked_repos

def generate_repository_report(db: Session):
    """Generates a report summarizing repository rankings."""
    ranked_repos = rank_repositories(db)
    report_lines = ["🔹 GitHub Repository Issue Management Report 🔹\n"]

    for repo_name, score in ranked_repos:
        repo = db.query(Repository).filter(Repository.name == repo_name).first()
        issues = db.query(Issue).filter(Issue.repo_id == repo.id).all()

        report_lines.append(f"🔹 Repository: {repo_name}")
        report_lines.append(f"⭐ Stars: {repo.stars}, 🔠 Language: {repo.language}, 🛠 Open Issues: {repo.issue_count}")
        report_lines.append(f"📈 Issue Handling Score: {score}")

        sample_analysis = " | ".join(issue.llm_analysis[:150] for issue in issues[:5] if issue.llm_analysis)
        report_lines.append(f"📝 Sample AI Insights: {sample_analysis}")
        report_lines.append("----------------------------------------------------")

    report_text = "\n".join(report_lines)
    
    with open("repository_report.txt", "w") as file:
        file.write(report_text)

    logging.info("Repository ranking report generated successfully.")
    return report_text
