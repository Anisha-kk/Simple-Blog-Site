import os
from dotenv import load_dotenv

load_dotenv("secret.env")  # loads .env into environment

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
   
