import logging
import os
import base64
try:
    import google.genai as genai
    from google.genai import types
except ImportError:
    genai = None
from app.core.config import settings
from app.core.exception import OCRQuotaExceededError
from app.utils.prompt_loader import load_prompt

logger = logging.getLogger(__name__)

# Supported MIME types for Gemini multimodal input
_MIME_MAP = {
    ".pdf":  "application/pdf",
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".bmp":  "image/bmp",
    ".tif":  "image/tiff",
    ".tiff": "image/tiff",
    ".webp": "image/webp",
}




class OCRService:
    def __init__(self):
        self.client = None
        if genai is None:
            logger.error("google-genai is not installed. OCR endpoint will fail until dependency is installed.")
            return

        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        logger.info("OCRService initialised with Gemini %s (no local models).", settings.GEMINI_MODEL)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def process_file(self, file_path: str, file_name: str) -> tuple[str, str]:
        """
        Send the uploaded file directly to Gemini for OCR/text extraction.

        Returns:
            (output_path, markdown_content)
        """
        logger.info(
            "OCRService started: file_name=%s file_path=%s", file_name, file_path
        )

        if self.client is None:
            raise RuntimeError(
                "Missing dependency: google-genai. Install it to use OCR processing."
            )

        _, extension = os.path.splitext(file_name.lower())
        mime_type = _MIME_MAP.get(extension, "application/octet-stream")

        # Read file and encode inline
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        logger.info(
            "Sending file to Gemini: file_name=%s mime_type=%s size_bytes=%d",
            file_name, mime_type, len(file_bytes),
        )

        try:
            prompt = load_prompt("ocr_prompts.md")
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=[
                    prompt,
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
                ]
            )
        except Exception as exc:
            message = str(exc)
            lowered = message.lower()
            is_quota_error = (
                "resourceexhausted" in lowered
                or "quota exceeded" in lowered
                or "429" in lowered
            )

            if is_quota_error:
                logger.warning("Gemini quota exceeded for file_name=%s", file_name)
                raise OCRQuotaExceededError(
                    "Gemini API quota exceeded. Check billing/quota and retry later."
                ) from exc

            raise
        extracted_markdown: str = response.text or ""

        logger.info(
            "Gemini OCR completed: file_name=%s output_chars=%d",
            file_name, len(extracted_markdown),
        )

        if not extracted_markdown.strip():
            logger.error("Gemini returned empty content: file_name=%s", file_name)
            raise ValueError("Gemini returned empty content for the uploaded file.")

        # Persist the markdown output
        output_path = self._save_markdown(file_name, extracted_markdown)
        return output_path, extracted_markdown

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _save_markdown(self, file_name: str, content: str) -> str:
        base_name = os.path.splitext(file_name)[0]
        output_file = f"{base_name}.md"
        output_path = os.path.join(settings.OCR_MARKDOWN_DIR, output_file)

        os.makedirs(settings.OCR_MARKDOWN_DIR, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info("Markdown saved: output_path=%s", output_path)
        return output_path


ocr_service = OCRService()
