import os
from dotenv import load_dotenv

# Only load .env locally (safe fallback)
load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set")

    if not SECRET_KEY:
        raise ValueError("SECRET_KEY is not set")