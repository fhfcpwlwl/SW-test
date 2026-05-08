"""FastAPI backend for skin analysis."""
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import FASTAPI_HOST, FASTAPI_PORT, PYTORCH_MODEL_ENABLED, PYTORCH_MODEL_PATH, UPLOAD_DIR
from logger import setup_logger
from skin_analyzer import analyze_image, build_personalized_report, parse_skin_mbti
from skin_model import MODEL_PATH, load_model, predict_skin_analysis
from torch_skin_model import load_pytorch_model, predict_pytorch_skin_model
from utils import clean_analysis_result, create_safe_filename, validate_file_upload

logger = setup_logger(__name__)

app = FastAPI(
    title="Skin Analysis API",
    description="API for analyzing skin conditions from uploaded face images.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model: Optional[object] = None
pytorch_model_bundle: Optional[dict] = None
try:
    model = load_model()
    logger.info("Successfully loaded AI model: %s", MODEL_PATH)
except FileNotFoundError:
    logger.warning("AI model not found. Continuing with image analysis only.")
except Exception as exc:
    logger.error("Error loading model: %s", exc)

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
        "message": "Skin Analysis API v2.0",
        "status": "running",
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
        "model_loaded": model is not None,
        "pytorch_model_loaded": pytorch_model_bundle is not None,
        "version": "2.0.0",
    }


@app.post("/analyze-skin")
async def analyze_skin(request: Request, file: UploadFile = File(...)) -> JSONResponse:
    """Analyze skin from an uploaded image."""
    saved_file_path: Optional[Path] = None
    try:
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

        analysis_result = analyze_image(str(saved_file_path))

        if model is not None:
            try:
                model_result = predict_skin_analysis(str(saved_file_path), model=model)
                if model_result:
                    if isinstance(model_result.get("analysis"), dict):
                        analysis_result["analysis"].update(model_result["analysis"])
                    advice_result = model_result.get("advice")
                    if isinstance(advice_result, list):
                        analysis_result.setdefault("advice", []).extend(advice_result)
                    elif isinstance(advice_result, str) and advice_result:
                        analysis_result.setdefault("advice", []).append(advice_result)
            except Exception as exc:
                logger.warning("Model prediction failed: %s", exc)

        if pytorch_model_bundle is not None:
            try:
                pytorch_result = predict_pytorch_skin_model(str(saved_file_path), bundle=pytorch_model_bundle)
                if pytorch_result and isinstance(pytorch_result.get("analysis"), dict):
                    analysis_result["analysis"].update(pytorch_result["analysis"])
            except Exception as exc:
                logger.warning("PyTorch model prediction failed: %s", exc)

        skin_mbti = parse_skin_mbti(preinfo)
        report = build_personalized_report(analysis_result["analysis"], skin_mbti)

        result = {
            "filename": file.filename,
            "content_type": file.content_type,
            "status": "success",
            **analysis_result,
            "skin_mbti": skin_mbti,
            "report": report,
        }

        logger.info("Analysis completed successfully")
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
