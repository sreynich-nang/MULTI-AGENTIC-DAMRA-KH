import logging
import os
import shutil
import time
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ocr_llama_maker.ocr_service import ocr_service
from app.core.config import settings
from app.core.exception import OCRQuotaExceededError
from app.schemas.schemas import OCRUploadResponse

router = APIRouter(prefix="/ocr", tags=["OCR"])
logger = logging.getLogger(__name__)

ALLOWED_OCR_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}

@router.post("/upload", response_model=OCRUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    original_name = file.filename or ""
    _, extension = os.path.splitext(original_name.lower())
    logger.info("OCR upload request received: filename=%s extension=%s", original_name, extension)

    if extension not in ALLOWED_OCR_EXTENSIONS:
        logger.warning("Rejected OCR upload due to unsupported file type: filename=%s", original_name)
        raise HTTPException(
            status_code=400,
            detail="Only PDF and image files are allowed (.pdf, .png, .jpg, .jpeg, .bmp, .tif, .tiff, .webp).",
        )

    safe_file_name = os.path.basename(original_name)

    # 1. Store the file in the OCR upload temp directory
    temp_file_path = os.path.join(settings.OCR_UPLOAD_DIR, safe_file_name)
    os.makedirs(settings.OCR_UPLOAD_DIR, exist_ok=True)
    logger.info("Saving upload to temp path: %s", temp_file_path)

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info("Upload saved successfully: %s", temp_file_path)
        
        # 2. Process the file with OCR and Gemini
        logger.info("Starting OCR processing: filename=%s", safe_file_name)
        start_time = time.perf_counter()
        output_path, content = await ocr_service.process_file(
            file_path=temp_file_path, 
            file_name=safe_file_name
        )
        end_time = time.perf_counter()
        elapsed_time = round(end_time - start_time, 2)
        logger.info("OCR processing completed: filename=%s output=%s time=%.2fs", safe_file_name, output_path, elapsed_time)

        return {
            "status": "success",
            "message": f"Successfully processed {safe_file_name}",
            "output_file": os.path.basename(output_path),
            "content": content,
            "process_time": elapsed_time
        }
    except OCRQuotaExceededError as e:
        logger.warning(
            "OCR request hit Gemini quota: filename=%s error=%s",
            safe_file_name,
            str(e),
        )
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        logger.exception("OCR upload processing failed: filename=%s error=%s", safe_file_name, str(e))
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Optionally clean up the temp file
        # if os.path.exists(temp_file_path):
        #     os.remove(temp_file_path)
        pass
