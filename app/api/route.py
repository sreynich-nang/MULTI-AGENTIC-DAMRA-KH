from fastapi import APIRouter

from app.api.routes.ocr import router as ocr_router


router = APIRouter()

# Register all endpoint modules from app/api/routes here.
router.include_router(ocr_router)
