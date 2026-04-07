class OCRQuotaExceededError(Exception):
	"""Raised when external OCR provider quota is exhausted."""


class OCRProcessingError(Exception):
	"""Raised for OCR processing failures that are not quota-related."""
