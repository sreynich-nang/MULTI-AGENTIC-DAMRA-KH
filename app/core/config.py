import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    TEMP_DIR: str = "temp"
    OCR_UPLOAD_DIR: str = "temp/upload"
    OCR_MARKDOWN_DIR: str = "temp/ocr_markdown"
    APP_LOG_FILE: str = "log/app.log"

    class Config:
        env_file = ".env"

settings = Settings()
