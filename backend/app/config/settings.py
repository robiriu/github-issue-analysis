import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# GitHub API Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "elastic/kibana")

# PostgreSQL Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# LLM API Configuration (Free-tier OpenAI or Hugging Face)
LLM_API_KEY = os.getenv("LLM_API_KEY")  # Add your LLM API key here
LLM_MODEL = os.getenv("LLM_MODEL", "microsoft/deberta-v3-large")  # Default model

# General App Settings
DEBUG_MODE = os.getenv("DEBUG_MODE", "False") == "True"
