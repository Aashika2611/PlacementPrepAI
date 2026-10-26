import os
from datetime import timedelta
from urllib.parse import quote_plus

from dotenv import load_dotenv


# Load variables from backend/.env regardless of the working directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key"
    )

    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY",
        "dev-jwt-secret-key"
    )

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_TOKEN_LOCATION = ["headers"]

    # MySQL
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_NAME = os.environ.get("DB_NAME", "placementprep_ai")
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", 5))
    MAX_CONTENT_LENGTH = MAX_UPLOAD_MB * 1024 * 1024
    ALLOWED_RESUME_EXTENSIONS = {"pdf"}

    # Frontend
    FRONTEND_ORIGIN = os.environ.get(
        "FRONTEND_ORIGIN",
        "http://localhost:5173"
    )

    # AI / LLM
    ANTHROPIC_API_KEY = os.environ.get(
        "ANTHROPIC_API_KEY",
        ""
    ).strip()

    ANTHROPIC_MODEL = os.environ.get(
        "ANTHROPIC_MODEL",
        "claude-sonnet-4-6"
    )

    AI_ENABLED = bool(ANTHROPIC_API_KEY)