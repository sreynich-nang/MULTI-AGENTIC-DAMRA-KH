import logging
import os

from fastapi import FastAPI
from app.core.config import settings
from app.api.route import router as api_router


def setup_logging() -> None:
    os.makedirs(os.path.dirname(settings.APP_LOG_FILE), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(settings.APP_LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


setup_logging()

app = FastAPI(title="MULTI-AGENTIC-DAMRA-KH OCR API")

# Include aggregated API routers
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the OCR API Service"}
