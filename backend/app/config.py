import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/modus_process_engine")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY", "")
APP_ENV = os.getenv("APP_ENV", "development")
