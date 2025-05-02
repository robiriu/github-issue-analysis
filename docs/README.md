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
- Send selected data to **OpenAI API** or **Hugging Face models**.
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
