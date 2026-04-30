from pydantic import BaseModel


class OCRUploadResponse(BaseModel):
	status: str
	message: str
	output_file: str
	content: str
	process_time: float