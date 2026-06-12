"""Single-process Flask app for cloud deployment."""
import base64
from pathlib import Path

from flask import Flask, jsonify, make_response, render_template, request

from app import DEFAULT_RESULT, merge_result_data
from config import PYTORCH_MODEL_ENABLED, PYTORCH_MODEL_PATH, UPLOAD_DIR
from logger import setup_logger
from pytorch_report import build_pytorch_personalized_report
from skin_analyzer import build_pytorch_advice, ensure_face_image, parse_skin_mbti
from torch_skin_model import load_pytorch_model, predict_pytorch_skin_model
from utils import clean_analysis_result, create_safe_filename, validate_file_upload

logger = setup_logger(__name__)

app = Flask(__name__)

pytorch_model_bundle = None
if PYTORCH_MODEL_ENABLED:
    try:
        pytorch_model_bundle = load_pytorch_model()
        logger.info("Successfully loaded PyTorch model: %s", PYTORCH_MODEL_PATH)
    except FileNotFoundError:
        logger.warning("PyTorch model not found at %s", PYTORCH_MODEL_PATH)
    except Exception as exc:
        logger.error("Error loading PyTorch model: %s", exc)

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.route("/")
def home():
    """Serve the main upload and survey page."""
    response = make_response(render_template("index.html"))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/health")
def health():
    """Health check endpoint for the deployed service."""
    return jsonify(
        {
            "status": "ok",
            "service": "flask-deploy",
            "model_loaded": pytorch_model_bundle is not None,
        }
    ), 200


@app.route("/analyze", methods=["GET"])
def analyze_get():
    """Informational endpoint for direct GET access."""
    return jsonify({"message": "Use the form on / to upload an image for analysis."}), 200


@app.route("/analyze", methods=["POST"])
def analyze():
    """Analyze an uploaded photo without requiring a separate backend process."""
    saved_file_path = None
    try:
        if pytorch_model_bundle is None:
            logger.error("PyTorch model is not loaded")
            return render_template(
                "index.html",
                error="AI 모델이 아직 준비되지 않았습니다. 잠시 후 다시 시도해 주세요.",
            ), 503

        file = request.files.get("photo")
        if not file or file.filename == "":
            logger.warning("Analyze request received with no file")
            return render_template("index.html", error="사진 파일을 선택해 주세요."), 400

        file_bytes = file.read()
        mime_type = file.mimetype or "image/jpeg"
        preview_data = base64.b64encode(file_bytes).decode("utf-8")
        preview_url = f"data:{mime_type};base64,{preview_data}"

        is_valid, error_msg = validate_file_upload(file.filename, len(file_bytes))
        if not is_valid:
            logger.warning("Invalid file upload: %s", error_msg)
            return render_template("index.html", error=error_msg), 400

        saved_file_path = UPLOAD_DIR / create_safe_filename(file.filename)
        saved_file_path.write_bytes(file_bytes)
        logger.info("Saved upload: %s", saved_file_path)

        ensure_face_image(str(saved_file_path))

        pytorch_result = predict_pytorch_skin_model(
            str(saved_file_path),
            bundle=pytorch_model_bundle,
        )
        if not pytorch_result or not isinstance(pytorch_result.get("analysis"), dict):
            raise RuntimeError("PyTorch prediction did not return a valid analysis payload.")

        skin_mbti = parse_skin_mbti(request.form.to_dict(flat=True))
        analysis = {
            "age": "-",
            "gender": "-",
            **pytorch_result["analysis"],
        }
        result = {
            "filename": file.filename,
            "content_type": mime_type,
            "uploaded_preview": preview_url,
            "status": "success",
            "analysis": analysis,
            "advice": build_pytorch_advice(analysis, skin_mbti),
            "skin_mbti": skin_mbti,
            "report": build_pytorch_personalized_report(analysis, skin_mbti),
        }

        rendered_result = merge_result_data(DEFAULT_RESULT, clean_analysis_result(result))
        return render_template("result.html", result=rendered_result), 200

    except ValueError as exc:
        logger.warning("Validation error: %s", exc)
        return render_template("index.html", error=str(exc)), 400
    except Exception as exc:
        logger.error("Analysis error: %s", exc, exc_info=True)
        return render_template(
            "index.html",
            error="분석 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
        ), 500
    finally:
        if saved_file_path and Path(saved_file_path).exists():
            try:
                Path(saved_file_path).unlink()
            except OSError as exc:
                logger.warning("Failed to remove temporary upload %s: %s", saved_file_path, exc)


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    logger.warning("404 error: %s", request.path)
    return render_template("index.html", error="요청한 페이지를 찾을 수 없습니다."), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    logger.error("500 error: %s", error)
    return render_template("index.html", error="서버 내부 오류가 발생했습니다."), 500
