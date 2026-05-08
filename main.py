"""FastAPI backend for skin analysis."""
from typing import Optional
import os

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import UPLOAD_DIR
from logger import setup_logger
from skin_analyzer import analyze_image, build_personalized_report, parse_skin_mbti
from skin_model import MODEL_PATH, load_model, predict_skin_analysis
from utils import clean_analysis_result, sanitize_filename, validate_file_upload

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
try:
    model = load_model()
    logger.info("Successfully loaded AI model: %s", MODEL_PATH)
except FileNotFoundError:
    logger.warning("AI model not found. Continuing with image analysis only.")
except Exception as exc:
    logger.error("Error loading model: %s", exc)

os.makedirs(UPLOAD_DIR, exist_ok=True)


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
        "version": "2.0.0",
    }


@app.post("/analyze-skin")
async def analyze_skin(request: Request, file: UploadFile = File(...)) -> JSONResponse:
    """Analyze skin from an uploaded image."""
    file_path = None
    try:
        if not file or not file.filename:
            logger.warning("Analysis request with no file")
            return JSONResponse(status_code=400, content={"error": "파일 이름이 없습니다."})

        is_valid, error_msg = validate_file_upload(file.filename)
        if not is_valid:
            logger.warning("Invalid file: %s", error_msg)
            return JSONResponse(status_code=400, content={"error": error_msg})

        form = await request.form()
        preinfo = {k: v for k, v in form.items() if k != "file"}

        sanitized_name = sanitize_filename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, sanitized_name)

        contents = await file.read()
        with open(file_path, "wb") as handle:
            handle.write(contents)

        logger.info("Saved upload: %s", file_path)

        analysis_result = analyze_image(file_path)

        if model is not None:
            try:
                model_result = predict_skin_analysis(file_path, model=model)
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

        result = clean_analysis_result(result)
        logger.info("Analysis completed successfully")
        return JSONResponse(content=result, status_code=200)

    except ValueError as exc:
        logger.warning("Validation error: %s", exc)
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except Exception as exc:
        logger.error("Analysis error: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"분석 중 오류가 발생했습니다: {exc}"},
        )
    finally:
        pass


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting FastAPI server")
    uvicorn.run(app, host="127.0.0.1", port=8000)
