import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    DB_NAME = os.getenv("DB_NAME", "attendance.db")
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

config = Config()