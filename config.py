"""Configuration management for the skin analysis application."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
IMAGE_DIR = DATA_DIR / "images"
MODEL_DIR = PROJECT_ROOT / "model"
UPLOAD_DIR = PROJECT_ROOT / "uploads"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"
LOGS_DIR = PROJECT_ROOT / "logs"

for directory in [MODEL_DIR, UPLOAD_DIR, DATA_DIR, IMAGE_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "skin_model.h5"


def _default_pytorch_model_path() -> Path:
    """Resolve a sensible default location for the external .pth file."""
    configured = os.getenv("PYTORCH_MODEL_PATH")
    if configured:
        return Path(configured)

    home = Path.home()
    candidates = [
        home / "OneDrive" / "Desktop" / "skin_model_best.pth",
        home / "OneDrive" / "바탕 화면" / "skin_model_best.pth",
        home / "Desktop" / "skin_model_best.pth",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[0]


PYTORCH_MODEL_PATH = _default_pytorch_model_path()
PYTORCH_MODEL_ENABLED = os.getenv("PYTORCH_MODEL_ENABLED", "True").lower() == "true"
PYTORCH_MODEL_LABELS = [
    label.strip()
    for label in os.getenv("PYTORCH_MODEL_LABELS", "class_0,class_1").split(",")
    if label.strip()
]
MODEL_INPUT_SHAPE = (
    int(os.getenv("MODEL_INPUT_HEIGHT", "224")),
    int(os.getenv("MODEL_INPUT_WIDTH", "224")),
    int(os.getenv("MODEL_INPUT_CHANNELS", "3")),
)
MODEL_BATCH_SIZE = int(os.getenv("MODEL_BATCH_SIZE", "16"))
MODEL_EPOCHS = int(os.getenv("MODEL_EPOCHS", "20"))

FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

FASTAPI_HOST = os.getenv("FASTAPI_HOST", "127.0.0.1")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", "8000"))
BACKEND_URL = os.getenv("BACKEND_URL", f"http://{FASTAPI_HOST}:{FASTAPI_PORT}/analyze-skin")

MAX_UPLOAD_SIZE = int(float(os.getenv("MAX_UPLOAD_SIZE_MB", "50")) * 1024 * 1024)
ALLOWED_EXTENSIONS = {
    ext.strip().lower()
    for ext in os.getenv("ALLOWED_EXTENSIONS", "png,jpg,jpeg,gif,bmp,webp").split(",")
    if ext.strip()
}

TARGET_IMAGE_SIZE = (
    int(os.getenv("TARGET_IMAGE_WIDTH", "320")),
    int(os.getenv("TARGET_IMAGE_HEIGHT", "320")),
)
FACE_DETECTION_MIN_SIZE = (
    int(os.getenv("FACE_DETECTION_MIN_WIDTH", "30")),
    int(os.getenv("FACE_DETECTION_MIN_HEIGHT", "30")),
)
FACE_DETECTION_SCALE_FACTOR = float(os.getenv("FACE_DETECTION_SCALE_FACTOR", "1.1"))
FACE_DETECTION_MIN_NEIGHBORS = int(os.getenv("FACE_DETECTION_MIN_NEIGHBORS", "3"))

WRINKLE_THRESHOLD = int(os.getenv("WRINKLE_THRESHOLD", "50"))
PORES_THRESHOLD = int(os.getenv("PORES_THRESHOLD", "50"))
REDNESS_THRESHOLD = int(os.getenv("REDNESS_THRESHOLD", "40"))
ACNE_THRESHOLD = int(os.getenv("ACNE_THRESHOLD", "45"))
PIGMENTATION_THRESHOLD = int(os.getenv("PIGMENTATION_THRESHOLD", "40"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "[%(asctime)s] %(levelname)s - %(name)s: %(message)s")
LOG_FILE_PATH = Path(os.getenv("LOG_FILE_PATH", "logs/app.log"))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))

SKIN_ADVICE = {
    "wrinkles": "\uC8FC\uB984 \uAC1C\uC120\uC744 \uC704\uD574 \uD0C4\uB825 \uCF00\uC5B4\uC640 \uC790\uC678\uC120 \uCC28\uB2E8\uC744 \uD568\uAED8 \uAD00\uB9AC\uD574\uBCF4\uC138\uC694.",
    "pores": "\uBAA8\uACF5 \uBD80\uB2F4\uC774 \uB192\uC544 \uBCF4\uC5EC \uD53C\uC9C0 \uC870\uC808\uACFC \uC800\uC790\uADF9 \uAC01\uC9C8 \uCF00\uC5B4\uB97C \uBCD1\uD589\uD558\uB294 \uD3B8\uC774 \uC88B\uC2B5\uB2C8\uB2E4.",
    "redness": "\uBD89\uC740\uAE30\uAC00 \uBCF4\uC774\uBA74 \uC9C4\uC815 \uC131\uBD84 \uC911\uC2EC\uC73C\uB85C \uB8E8\uD2F4\uC744 \uB2E8\uC21C\uD654\uD574\uBCF4\uC138\uC694.",
    "acne_inflamed": "\uC5FC\uC99D\uC131 \uC5EC\uB4DC\uB984\uC774 \uBCF4\uC77C \uB54C\uB294 \uC790\uADF9\uC801\uC778 \uC2A4\uD06C\uB7FD\uBCF4\uB2E4 \uC9C4\uC815\uACFC \uAD6D\uC18C \uCF00\uC5B4\uAC00 \uC6B0\uC120\uC785\uB2C8\uB2E4.",
    "acne_noninflamed": "\uD654\uC774\uD2B8\uD5E4\uB4DC\uC640 \uBE14\uB799\uD5E4\uB4DC \uACBD\uD5A5\uC774 \uBCF4\uC774\uBA74 BHA \uB610\uB294 PHA \uC911\uC2EC\uC758 \uCF00\uC5B4\uAC00 \uB3C4\uC6C0\uC774 \uB429\uB2C8\uB2E4.",
    "pigmentation": "\uC0C9\uC18C\uCE68\uCC29\uC740 \uBE0C\uB77C\uC774\uD2B8\uB2DD \uC138\uB7FC\uACFC \uAFB8\uC900\uD55C \uC120\uCF00\uC5B4\uB97C \uAC19\uC774 \uC7A1\uC544\uC8FC\uB294 \uAC83\uC774 \uC88B\uC2B5\uB2C8\uB2E4.",
    "sagging": "\uCC98\uC9D0 \uC2E0\uD638\uAC00 \uBCF4\uC774\uBA74 \uD0C4\uB825 \uC131\uBD84\uACFC \uBCF4\uC2B5 \uC7A5\uBCBD \uCF00\uC5B4\uB97C \uD568\uAED8 \uAC00\uC838\uAC00\uBCF4\uC138\uC694.",
    "dryness": "\uAC74\uC870\uAC10\uC774 \uC788\uB2E4\uBA74 \uC138\uB77C\uB9C8\uC774\uB4DC\uC640 \uBCF4\uC2B5 \uD06C\uB9BC\uC73C\uB85C \uC218\uBD84 \uC190\uC2E4\uC744 \uC904\uC5EC\uC8FC\uC138\uC694.",
}
