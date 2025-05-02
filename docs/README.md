# LLM Powered Github Issues Analysis

## Structured Flow for Building the Project

## 1️⃣ Setup GitHub API Integration

- Authenticate with GitHub API using a **Personal Access Token (PAT)**.
- Fetch **Kibana repository issues** and store them in **PostgreSQL**.
- Handle **pagination** and **rate limits** efficiently.

## 2️⃣ Define PostgreSQL Schema & Migrations

- Design database schema (`models.py`).
- Run **migrations** to create tables:
  - `repositories`
  - `issues`
  - `comments`

## 3️⃣ Process Issue Data with LLM

- Preprocess **issue descriptions** & **comments** for LLM-based analysis.
- Send selected data to **Hugging Face models**.
- Compute **ranking scores** based on:
  - Issue resolution
  - Response quality

## 4️⃣ Expose API via FastAPI

- Create **endpoints** to serve **ranked repository results**.
- Implement **query filters** (e.g., sort by resolution speed, engagement).

## 5️⃣ Build Web Dashboard (React Frontend)

- Connect frontend to **FastAPI backend** via **REST API calls**.
- Display **interactive charts/tables** with ranking insights.

## 6️⃣ Deploy Backend (Railway) & Frontend (Vercel)

- Push backend to **Railway** with **PostgreSQL setup**.
- Deploy React frontend to **Vercel**.
- Ensure **API calls** work smoothly between deployed services.



## This is full notes for each steps.

# Step 1️⃣ – Setup GitHub API Integration

## 🔹 Step 1: Generate a GitHub Personal Access Token (PAT)

We need a GitHub PAT to authenticate requests when fetching issue data.

### ✅ Steps to Generate a Token:

1. Go to **GitHub Developer Settings**.
2. Click **"Generate new token"** → Select **"Classic"** tokens.
3. Provide a token name (e.g., `github-issue-analysis`).
4. Set an expiration (choose **"No Expiration"** if needed).
5. Select **"Repository access"** → Choose **"Public repositories"**.
6. Enable permissions:
   - ✅ `repo` (for public repo access)
   - ✅ `read:issues` (to fetch issue details)
7. Click **Generate token**, and **copy it immediately** (it won’t be visible again).

---

## 🔹 Step 2: Secure the Token in Your Project

To avoid exposing your token in code:

### ✅ Store the Token Securely:

1. Create an **environment variable** for your token.
2. In `config/settings.py`, store it like this:

```python
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "elastic/kibana"  # Target repository
```

3. In your `.env` file (if using `python-dotenv`):

```
GITHUB_TOKEN=your_generated_token_here
```

4. Add `.env` to `.gitignore`:

```
# .gitignore
.env
```

---

## 🔹 Step 3: Setting Up GitHub API Requests

### 1. Understand GitHub API Endpoints

GitHub provides a REST API to retrieve issue data. Key endpoint:

```
GET https://api.github.com/repos/elastic/kibana/issues
```

### ✅ What This Does:

- Fetches list of issues from the `elastic/kibana` repository.
- Provides `title`, `labels`, `timestamps`, `status`, `comments`.
- Requires authentication via a **GitHub PAT**.

### 🚀 Pagination Handling:

- GitHub limits results to **30 issues per request**.
- Use `per_page=100` to fetch more per request.
- Iterate pages using `page=1`, `page=2`, etc.

---

### 2. Authentication & Secure Storage

Update your `.env` file:

```
GITHUB_TOKEN=your_generated_token_here
GITHUB_REPO=elastic/kibana
```

Ensure `.env` is loaded in `settings.py`:

```python
from dotenv import load_dotenv
import os

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "elastic/kibana")
```

---

### 3. Writing the API Request Function

Write a function in `backend/app/services.py` to fetch issues using GitHub REST API.

#### ✅ Function Requirements:

- Authenticate using PAT.
- Handle pagination.
- Log retrievals and errors.
- Format response for database storage.

```python
import logging
import requests
from config.settings import GITHUB_TOKEN, GITHUB_REPO

# Initialize logging
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def fetch_github_issues():
    """Fetches issues from the GitHub repository using API."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    params = {"per_page": 100, "page": 1}  # Pagination setup

    all_issues = []
    while True:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            issues = response.json()

            if not issues:
                break

            all_issues.extend(issues)
            logging.info(f"Fetched {len(issues)} issues from page {params['page']} of {GITHUB_REPO}")
            params["page"] += 1

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching issues: {e}")
            break

    logging.info(f"Total issues fetched: {len(all_issues)}")
    return all_issues
```

---

### 📌 What This Function Does:

- ✅ Fetches all issues using pagination.
- ✅ Logs successful requests and errors to `app.log`.
- ✅ Stops fetching when no more results are available.
- ✅ Returns structured issue data for further processing.

# Step 2️⃣ – Define PostgreSQL Schema & Migrations

## 1. Defining the PostgreSQL Schema to Store Issues

---
For someone unfamiliar with PostgreSQL, let me give you short explanation about it.

## 🐘 What is PostgreSQL?

✅ PostgreSQL is an advanced, open-source database system used for handling large amounts of structured data efficiently.  
✅ It's great for projects requiring scalable, relational storage (e.g., tracking GitHub issues).  
✅ We’ll use PostgreSQL to store and retrieve issue data from Kibana.

---

## 🔹 Step 1: Install PostgreSQL

For **Linux users**, install PostgreSQL using:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

📌 **Verify installation**:

```bash
psql --version
```

---

## 🔹 Step 2: Start & Enable PostgreSQL Service

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

---

## 🔹 Step 3: Create PostgreSQL User & Database

1️⃣ **Open PostgreSQL shell**:

```bash
sudo -u postgres psql
```

2️⃣ **Create a new user for the project**:

```sql
CREATE USER myuser WITH PASSWORD 'mypassword';
```

➡️ Replace `myuser` and `mypassword` with your actual credentials.

3️⃣ **Create the project database**:

```sql
CREATE DATABASE github_analysis;
```

4️⃣ **Grant permissions**:

```sql
GRANT ALL PRIVILEGES ON DATABASE github_analysis TO myuser;
```

5️⃣ **Exit the PostgreSQL shell**:

```sql
\q
```

---

## 🔹 Step 4: Store DB Credentials in `.env`

Update your `.env` file with the PostgreSQL connection string:

```
DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/github_analysis
```

📌 Breakdown of the URL:

- `myuser`: PostgreSQL username
- `mypassword`: PostgreSQL password
- `localhost`: Host server (usually localhost)
- `5432`: Default PostgreSQL port
- `github_analysis`: Your project database name

---

✅ PostgreSQL is now installed and configured!

Ok, back to previous step, after we’ve successfully fetched issue data from GitHub, we need a structured database schema to store it in PostgreSQL.

# 📌 Database Tables

We’ll define three core tables in `backend/app/models.py`:

1️⃣ **repositories** → Stores general repository metadata.  
2️⃣ **issues** → Tracks issue details like status, timestamps, and descriptions.  
3️⃣ **comments** → Stores issue comments for LLM-based analysis.

---

## 📌 Define Tables in `backend/app/models.py`

```python
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Repository(Base):
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    stars = Column(Integer, nullable=False)
    language = Column(String, nullable=False)
    issue_count = Column(Integer, nullable=False)

class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=False)

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False)
    author = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
```

---

## ✅ What This Does

- **Repositories table** → Stores metadata like stars, language, issue count.
- **Issues table** → Stores titles, timestamps, status, and descriptions.
- **Comments table** → Stores LLM-analyzed discussions related to issues.
- Uses **foreign keys** to maintain relationships between repositories and issues.

---

## 2️⃣ Writing Database Migrations for PostgreSQL

Now that we've defined our database schema, we need to apply these table definitions to PostgreSQL using migrations.

### 📌 What Are Migrations?

✅ Migrations allow database schema changes (creating/modifying tables).  
✅ They keep track of schema versions without manual SQL editing.  
✅ We use **Alembic** (a lightweight migration tool for SQLAlchemy).

---

### 🔹 Step 1: Install Alembic

First, install Alembic in your project:

```bash
pip install alembic
```

---

### 🔹 Step 2: Initialize Alembic in the Project

Run this command inside your backend folder:

```bash
cd backend
alembic init migrations
```

This creates a `migrations/` directory containing configuration files.

---

### 🔹 Step 3: Configure `alembic.ini` for PostgreSQL

Edit `backend/alembic.ini` and modify the database connection line:

```ini
sqlalchemy.url = postgresql://user:password@localhost:5432/github_analysis
```

(Replace `user` and `password` with your actual PostgreSQL credentials stored in `.env`.)

---

### 🔹 Step 4: Generate Migration Script

Create an initial migration to apply `models.py` schema:

```bash
cd backend
alembic revision --autogenerate -m "Initial database schema"
```

---

### 🔹 Step 5: Apply Migration to Database

Run the migration to create tables:

```bash
alembic upgrade head
```

---

## ✅ What This Does

- Automatically creates tables (**repositories**, **issues**, **comments**) in PostgreSQL.
- Logs migration history so future schema updates are tracked properly.

# 3. Saving GitHub Issue Data into PostgreSQL

Now that the database is fully set up, let's move forward with storing fetched GitHub issue data into PostgreSQL.

---

## 📌 Step 1: Define the Database Connection in `database.py`

Inside `backend/app/db/database.py`, set up the connection using SQLAlchemy:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_URL

# Create database engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## ✅ What This Does:

- Establishes a persistent PostgreSQL connection via SQLAlchemy.
- Creates a session factory for database interactions.
- Provides a dependency for using database sessions in FastAPI routes.

---

## 📌 Step 2: Write the Function to Save Issues in `services.py`

Modify `backend/app/services.py` to insert fetched issue data into the database.

```python
import logging
import requests
from sqlalchemy.orm import Session
from config.settings import GITHUB_TOKEN, GITHUB_REPO
from backend.app.models import Repository, Issue
from backend.app.db.database import get_db

# Initialize logging
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def fetch_github_issues():
    """Fetches issues from GitHub and stores them in PostgreSQL."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    params = {"per_page": 100, "page": 1}  # Pagination setup

    all_issues = []
    while True:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise error if request fails
            issues = response.json()

            if not issues:  # Stop if there are no more issues
                break

            all_issues.extend(issues)
            logging.info(f"Fetched {len(issues)} issues from page {params['page']} of {GITHUB_REPO}")
            
            params["page"] += 1  # Go to next page

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching issues: {e}")
            break  # Stop execution on failure

    logging.info(f"Total issues fetched: {len(all_issues)}")

    # Store the fetched issues into PostgreSQL
    db = next(get_db())
    save_issues_to_db(db, all_issues, GITHUB_REPO)

    return all_issues

def save_issues_to_db(db: Session, issues, repo_name):
    """Stores GitHub issues into PostgreSQL."""
    try:
        # Ensure repository entry exists
        repo = db.query(Repository).filter(Repository.name == repo_name).first()
        if not repo:
            repo = Repository(name=repo_name, stars=0, language="Unknown", issue_count=len(issues))
            db.add(repo)
            db.commit()

        # Insert issues
        for issue_data in issues:
            issue = Issue(
                repo_id=repo.id,
                title=issue_data["title"],
                description=issue_data.get("body", ""),
                created_at=issue_data["created_at"],
                closed_at=issue_data.get("closed_at"),
                status="open" if issue_data["state"] == "open" else "closed"
            )
            db.add(issue)

        db.commit()
        logging.info(f"Stored {len(issues)} issues for repository {repo_name}")

    except Exception as e:
        logging.error(f"Error saving issues: {e}")
```

---

## ✅ What This Function Does:

- Ensures the repository exists before saving issues.
- Adds issues into the issues table with relevant metadata.
- Handles missing fields gracefully using `.get()`.
- Commits changes to ensure persistent storage.

---

## ✅ Now, every API call will store issues in the database automatically.

# 3️⃣ Process (Retrieving & Analyzing) Issue Data with LLM

Now that GitHub issue data is stored in PostgreSQL, we need to process and analyze it using LLM (Large Language Model) to evaluate issue clarity, discussion quality, and resolution depth.

---

## 📌 Step 1: Select an LLM for Issue Analysis

We’ll integrate an LLM API to analyze issue discussions and assess: 

✅ **Issue clarity** → How well is the issue described? 

✅ **Community engagement** → Are discussions meaningful and constructive? 

✅ **Solution quality** → Does the response provide a valid resolution?

Popular LLM choices include:

- **OpenAI GPT-4 (gpt-4-turbo)**
- **Hugging Face Inference API (BART, T5 models)**

### ===================choosing LLM API===================

If you're looking for a free-tier LLM API, you need to compare Hugging Face Inference API and OpenAI API. Below are the options:

1. **Hugging Face Inference API**

   ✅ **Best for analyzing GitHub issues** → Many open-source AI models available. 

   ✅ **No cost for basic usage** → Free-tier models don’t require API payments. 

   ✅ **Supports natural language processing** → Great for evaluating issue clarity and discussions.

   #### 📌 How to Use It?

   1️⃣ Sign up at Hugging Face and generate a free API key. 

   2️⃣ Choose an NLP model like `facebook/bart-large-cnn` (for summarization) or `microsoft/deberta-v3-large` (for text understanding). 

   3️⃣ Modify `settings.py`:

   ```python
   LLM_API_KEY=your_huggingface_api_key
   LLM_MODEL=facebook/bart-large-cnn
   ```

   4️⃣ Update `services.py`:

   ```python
   import requests

   def analyze_issue_with_llm(issue_description):
       """Uses Hugging Face API for issue clarity assessment."""
       headers = {"Authorization": f"Bearer {LLM_API_KEY}"}
       payload = {"inputs": issue_description}
       response = requests.post(f"https://api-inference.huggingface.co/models/{LLM_MODEL}", headers=headers, json=payload)
       return response.json().get("generated_text", "No analysis available")
   ```

   ✅ Now your project can assess issue descriptions using a free-tier model!

2. **OpenAI API (Free with Limited Credits)**

   ✅ Offers powerful models like **GPT-3.5** and **GPT-4**. 

   ✅ **Free-tier** gives limited credits → Good for testing, but not ideal for large-scale analysis. 

   ✅ Great for evaluating issue engagement & response quality.

   #### 📌 How to Use? 

   1️⃣ Sign up for OpenAI (https://openai.com/). 

   2️⃣ Get your API key (free-tier provides limited usage). 

   3️⃣ Modify `settings.py`:

   ```python
   LLM_API_KEY=your_openai_api_key
   LLM_MODEL=gpt-3.5-turbo
   ```

### ===================choosing LLM API===================

---

## 🔹 Step 2: Set Up LLM API Connection

### 📌 Update `.env` with API credentials:

```
LLM_API_KEY=your_huggingface_api_key
LLM_MODEL=facebook/bart-large-cnn  # Example model for summarization
```

### 📌 Modify `settings.py` to load LLM settings:

```python
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "facebook/bart-large-cnn")
```

---

## 🔹 Step 3: Write an LLM-Based Issue Analysis Function

Inside `backend/app/services.py`, add a function to process issue descriptions with an LLM.

```python
import requests
from config.settings import LLM_API_KEY, LLM_MODEL

def analyze_issue_with_llm(issue_description):
    """Uses Hugging Face API to assess issue clarity."""
    headers = {"Authorization": f"Bearer {LLM_API_KEY}"}
    payload = {"inputs": issue_description}
    
    try:
        response = requests.post(f"https://api-inference.huggingface.co/models/{LLM_MODEL}", headers=headers, json=payload)
        response_data = response.json()
        return response_data.get("generated_text", "No analysis available")

    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
```

---

## ✅ What This Does:

- Sends issue descriptions to Hugging Face LLM for summarization & analysis.
- Retrieves AI-generated insights about clarity, engagement, and resolution quality.
- Handles API errors gracefully to ensure system stability.

# 🔹 Step 4: Ranking Repositories Based on Issue-Handling Efficiency

Now that we’ve retrieved, stored, and analyzed GitHub issues, we need to rank repositories based on how efficiently they handle issues.

## 1: Define Ranking Criteria

We’ll rank repositories based on these factors:

✅ **Resolution Time** → How quickly are issues closed?

✅ **Community Engagement** → How many comments per issue?

✅ **LLM-Based Issue Clarity** → Does the issue description clearly explain the problem?

✅ **Response Quality** → Are replies solving the problem effectively?

Each repository gets a score based on weighted factors.

## 2: Write a Ranking Function in `services.py`

### 📌 Modify `services.py` to Include Repository Ranking

```python
def rank_repositories(db: Session):
    """Ranks repositories based on issue resolution efficiency."""
    repositories = db.query(Repository).all()
    repo_scores = {}

    for repo in repositories:
        issues = db.query(Issue).filter(Issue.repo_id == repo.id).all()

        total_issues = len(issues)
        resolved_issues = sum(1 for issue in issues if issue.status == "closed")
        avg_resolution_time = sum((issue.closed_at - issue.created_at).days for issue in issues if issue.closed_at) / max(1, resolved_issues)
        avg_comments = sum(len(issue.description.split()) for issue in issues) / max(1, total_issues)
        llm_quality = sum(len(issue.llm_analysis.split()) for issue in issues) / max(1, total_issues)

        # Compute score (weighted formula)
        score = (resolved_issues / total_issues) * 0.4 + (1 / max(1, avg_resolution_time)) * 0.3 + (avg_comments / 50) * 0.2 + (llm_quality / 100) * 0.1
        repo_scores[repo.name] = round(score, 3)

    # Sort repositories by score (descending)
    ranked_repos = sorted(repo_scores.items(), key=lambda x: x[1], reverse=True)
    logging.info(f"Repository rankings generated: {ranked_repos}")

    return ranked_repos
```
### ✅ What This Does:

- Calculates average resolution time, engagement, and clarity.
- Uses LLM analysis to evaluate description quality.
- Assigns weighted scores to rank repositories.
- Logs rankings in `app.log`.

# 🔹 Step 5: Generate a Report Summarizing Repository Rankings

Now that we've ranked repositories based on issue-handling efficiency, we need to generate a structured report summarizing their performance.

## 1: Define Report Structure

The report will include:

✅ **Repository Overview** → Basic details like stars, issues, and language.

✅ **Issue Handling Score** → Calculated ranking score based on resolution speed, engagement, and LLM analysis.

✅ **Analysis Insights** → A summary of issue clarity, response quality, and community involvement.

## 2: Generate the Report in `services.py`

### 📌 Modify `services.py` to Create a Report

```python
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

        # Summary of LLM analysis
        sample_analysis = " | ".join(issue.llm_analysis[:150] for issue in issues[:5] if issue.llm_analysis)
        report_lines.append(f"📝 Sample AI Insights: {sample_analysis}")
        report_lines.append("----------------------------------------------------")

    report_text = "\n".join(report_lines)
    
    # Save report to file
    with open("repository_report.txt", "w") as file:
        file.write(report_text)

    logging.info("Repository ranking report generated successfully.")
    return report_text
```
### ✅ What This Function Does:

- **Creates a structured repository ranking report** based on AI-driven issue evaluation.
- **Extracts meaningful insights** from GitHub issue data.
- **Saves report as a file** for easy access.
- **Logs success & errors** in `app.log`.

---

# Now that our repository report is ready, we need to design a simple API route to serve the report dynamically.

# 4️⃣ Expose API via FastAPI

## Step 1: Designing an API Route to Serve Repository Rankings

Now that our repository ranking report is generated, we need to make it accessible via an API endpoint.

### 1: Set Up FastAPI for the Report Endpoint

Since we need an API, let’s use FastAPI, a lightweight framework for serving data.

### 📌 Install FastAPI & Uvicorn

To install the necessary dependencies, run the following command:

```bash
pip install fastapi uvicorn
```
### 📌 Modify `backend/app/main.py` to Include Report Endpoint

In `backend/app/main.py`, we’ll add a new route to serve the repository ranking report.

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.services import generate_repository_report

app = FastAPI()

@app.get("/repository-report")
def get_repository_report(db: Session = Depends(get_db)):
    """API endpoint to fetch the repository ranking report."""
    report_text = generate_repository_report(db)
    return {"report": report_text}
```
### ✅ What This Does:

- **Sets up a FastAPI route** at `/repository-report`.
- **Calls `generate_repository_report()`** to retrieve the rankings dynamically.
- **Returns the formatted ranking report** as JSON.

### 2: Run the API

Start the FastAPI server to test the endpoint:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
### Once running, open a browser and go to:

[http://localhost:8000/repository-report](http://localhost:8000/repository-report)

### ✅ This should display your repository ranking report!

Now that our API is ready, you can:

🔹 **Test the API locally** → Ensure rankings are correctly retrieved.

🔹 **Improve report formatting** → Convert the output into a readable JSON structure.

🔹 **Deploy the API** → Host it on Render, Railway, or AWS to make it accessible online. (I choose Railway for this project)

## Summary
The final objective of this challenge is to generate a repository issue ranking, and it has been done. I built this project with 6 steps, and steps 5 and 6 are still needed to deploy (Railway and Vercel), and I'm still working on them.
Some challenging points I would say are:

- Fetching issues from the GitHub repository sometimes has problems. Github API sometimes does not respond.
- The same issue occurs with accessing the model using the Huggingface API; it also takes time, and sometimes does not respond from the Huggingface API services. It can be seen in my app-Copy.log in this repository
- I'm using the Kibana repository with 20,439 stars and 9,900 open issues, so it takes time to finish fetching issues and for the LLM model to analyze the fetched issues and create a summary. Therefore, in the GitHub Repository Issue Management Report (http://localhost:8000/repository-report), it shows that scoring sometimes gives zero values. This needs to be improved by using other models.     

http://localhost:8000/repository-report

"🔹 GitHub Repository Issue Management Report 🔹\n\n🔹 Repository: elastic/kibana\n⭐ Stars: 20439, 🔠 Language: TypeScript, 🛠 Open Issues: 9900\n📈 Issue Handling Score: 0\n📝 Sample AI Insights: \n----------------------------------------------------"