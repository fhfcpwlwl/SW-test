"""Utility functions for the application."""
import os
from pathlib import Path
from typing import Optional
from uuid import uuid4

import numpy as np

from config import ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE
from logger import setup_logger

logger = setup_logger(__name__)


def validate_file_upload(filename: str, file_size: Optional[int] = None) -> tuple[bool, Optional[str]]:
    """Validate uploaded file metadata."""
    if not filename:
        return False, "파일 이름이 없습니다."

    if file_size is not None and file_size > MAX_UPLOAD_SIZE:
        return False, f"파일 크기가 너무 큽니다. 최대 {MAX_UPLOAD_SIZE / (1024 * 1024):.1f}MB까지 가능합니다."

    file_ext = Path(filename).suffix.lower().lstrip(".")
    if not file_ext or file_ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        return False, f"지원하지 않는 파일 형식입니다. 허용 형식: {allowed}"

    return True, None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safer filesystem usage."""
    sanitized = os.path.basename(filename)
    for char in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
        sanitized = sanitized.replace(char, "_")
    return sanitized


def create_safe_filename(filename: str) -> str:
    """Create a unique, safe filename for uploads."""
    sanitized = sanitize_filename(filename)
    if not sanitized or sanitized.startswith("."):
        sanitized = "upload"
    return f"{uuid4().hex}_{sanitized}"


def ensure_directory(path: Path) -> bool:
    """Ensure directory exists."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as exc:
        logger.error("Failed to create directory %s: %s", path, exc)
        return False


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def clean_analysis_result(result: dict) -> dict:
    """Clean and format analysis result for JSON serialization."""
    cleaned = {}
    for key, value in result.items():
        if isinstance(value, (float, np.floating)):
            cleaned[key] = round(float(value), 2)
        elif isinstance(value, (int, np.integer)):
            cleaned[key] = int(value)
        elif isinstance(value, dict):
            cleaned[key] = clean_analysis_result(value)
        elif isinstance(value, list):
            cleaned[key] = [clean_analysis_result(item) if isinstance(item, dict) else item for item in value]
        else:
            cleaned[key] = value
    return cleaned
