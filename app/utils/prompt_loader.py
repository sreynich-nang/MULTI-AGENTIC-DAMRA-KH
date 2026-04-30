import os
import functools
from typing import Optional
from app.core.config import settings

# Path to the prompts directory
PROMPTS_DIR = settings.PROMPTS_DIR

@functools.lru_cache(maxsize=32)
def load_prompt(filename: str) -> str:
    """
    Loads a prompt from a markdown file in the prompts directory.
    Uses lru_cache to avoid repeated disk reads.
    
    Args:
        filename: The name of the file (e.g., 'ocr_prompts.md')
        
    Returns:
        The content of the prompt file as a string.
        
    Raises:
        FileNotFoundError: If the prompt file does not exist.
    """
    file_path = os.path.join(PROMPTS_DIR, filename)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Prompt file not found: {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def get_prompt_path(filename: str) -> str:
    """Returns the absolute path to a prompt file."""
    return os.path.join(PROMPTS_DIR, filename)
