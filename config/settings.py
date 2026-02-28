import os
from dotenv import load_dotenv
load_dotenv()

APP_NAME     = "SuperBot"
APP_VERSION  = "2.0"
COMPANY_NAME = os.getenv("COMPANY_NAME", "Acme Corp")

# LLM
LLM_BACKEND  = os.getenv("LLM_BACKEND", "groq")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
OPENAI_API_KEY          = os.getenv("OPENAI_API_KEY", "")
AZURE_OPENAI_API_KEY    = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT   = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
AZURE_OPENAI_API_VERSION= os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
LLM_MAX_TOKENS  = int(os.getenv("LLM_MAX_TOKENS", "1500"))

# Database
DB_BACKEND  = os.getenv("DB_BACKEND", "sqlite")
SQLITE_PATH = os.getenv("SQLITE_PATH", "data/superbot.db")

# RAG
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
RAG_TOP_K       = int(os.getenv("RAG_TOP_K", "4"))
RAG_INDEX_PATH  = os.getenv("RAG_INDEX_PATH", "data/rag_index.pkl")
HR_PDF_DIR      = os.getenv("HR_PDF_DIR", "data/hr_policies")

# Jira
JIRA_BACKEND = os.getenv("JIRA_BACKEND", "mock")
JIRA_URL     = os.getenv("JIRA_URL", "")
JIRA_EMAIL   = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
JIRA_PROJECT   = os.getenv("JIRA_PROJECT", "ACME")

DATA_SOURCE = os.getenv("DATA_SOURCE", "sqlite")
