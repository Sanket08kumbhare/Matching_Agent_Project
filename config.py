import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
USE_RAG = os.getenv("USE_RAG", "false").lower() == "true"
RESUME_DIR = os.getenv("RESUME_DIR", "data/resumes")
TOP_K = int(os.getenv("TOP_K", "10"))
