"""FastAPI backend for .pth-based skin analysis."""
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import FASTAPI_HOST, FASTAPI_PORT, PYTORCH_MODEL_ENABLED, PYTORCH_MODEL_PATH, UPLOAD_DIR
from logger import setup_logger
from skin_analyzer import (
    build_pytorch_advice,
    build_pytorch_personalized_report,
    ensure_face_image,
    parse_skin_mbti,
)
from torch_skin_model import load_pytorch_model, predict_pytorch_skin_model
from utils import clean_analysis_result, create_safe_filename, validate_file_upload

logger = setup_logger(__name__)

app = FastAPI(
    title="Skin Analysis API",
    description="API for analyzing skin conditions from uploaded face images.",
    version="2.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pytorch_model_bundle: Optional[dict] = None

if PYTORCH_MODEL_ENABLED:
    try:
        pytorch_model_bundle = load_pytorch_model()
        logger.info("Successfully loaded PyTorch model: %s", PYTORCH_MODEL_PATH)
    except FileNotFoundError:
        logger.warning("PyTorch model not found at %s", PYTORCH_MODEL_PATH)
    except Exception as exc:
        logger.error("Error loading PyTorch model: %s", exc)

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
def root() -> dict:
    """Root endpoint with API information."""
    return {
        "message": "Skin Analysis API v2.1",
        "status": "running",
        "analysis_model": "pytorch",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze-skin",
        },
    }


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "analysis_model": "pytorch",
        "pytorch_model_loaded": pytorch_model_bundle is not None,
        "version": "2.1.0",
    }


@app.post("/analyze-skin")
async def analyze_skin(request: Request, file: UploadFile = File(...)) -> JSONResponse:
    """Analyze skin from an uploaded image using the external .pth model only."""
    saved_file_path: Optional[Path] = None
    try:
        if pytorch_model_bundle is None:
            logger.error("PyTorch model is not loaded")
            return JSONResponse(
                status_code=503,
                content={"error": "AI 모델이 아직 준비되지 않았습니다. 잠시 후 다시 시도해 주세요."},
            )

        if not file or not file.filename:
            logger.warning("Analysis request with no file")
            return JSONResponse(status_code=400, content={"error": "파일 이름이 없습니다."})

        contents = await file.read()
        is_valid, error_msg = validate_file_upload(file.filename, len(contents))
        if not is_valid:
            logger.warning("Invalid file: %s", error_msg)
            return JSONResponse(status_code=400, content={"error": error_msg})

        form = await request.form()
        preinfo = {key: value for key, value in form.items() if key != "file"}

        saved_file_path = UPLOAD_DIR / create_safe_filename(file.filename)
        saved_file_path.write_bytes(contents)
        logger.info("Saved upload: %s", saved_file_path)

        ensure_face_image(str(saved_file_path))

        pytorch_result = predict_pytorch_skin_model(str(saved_file_path), bundle=pytorch_model_bundle)
        if not pytorch_result or not isinstance(pytorch_result.get("analysis"), dict):
            raise RuntimeError("PyTorch prediction did not return a valid analysis payload.")

        skin_mbti = parse_skin_mbti(preinfo)
        analysis = {
            "age": "-",
            "gender": "-",
            **pytorch_result["analysis"],
        }
        report = build_pytorch_personalized_report(analysis, skin_mbti)
        advice = build_pytorch_advice(analysis, skin_mbti)

        result = {
            "filename": file.filename,
            "content_type": file.content_type,
            "status": "success",
            "analysis": analysis,
            "advice": advice,
            "skin_mbti": skin_mbti,
            "report": report,
        }

        logger.info("PyTorch-only analysis completed successfully")
        return JSONResponse(content=clean_analysis_result(result), status_code=200)

    except ValueError as exc:
        logger.warning("Validation error: %s", exc)
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except Exception as exc:
        logger.error("Analysis error: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "분석 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."},
        )
    finally:
        await file.close()
        if saved_file_path and saved_file_path.exists():
            try:
                saved_file_path.unlink()
            except OSError as exc:
                logger.warning("Failed to remove temporary upload %s: %s", saved_file_path, exc)


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting FastAPI server")
    uvicorn.run(app, host=FASTAPI_HOST, port=FASTAPI_PORT)
