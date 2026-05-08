"""Flask frontend for the skin analysis experience."""
import base64
import io
from copy import deepcopy

import requests
from flask import Flask, jsonify, make_response, render_template, request

from config import BACKEND_URL
from logger import setup_logger
from utils import create_safe_filename, validate_file_upload

logger = setup_logger(__name__)

app = Flask(__name__)

DEFAULT_RESULT = {
    "filename": "-",
    "content_type": "-",
    "uploaded_preview": None,
    "analysis": {
        "age": "-",
        "gender": "-",
        "pytorch_predicted_class": "-",
        "pytorch_confidence": 0,
        "pytorch_class_scores": {},
    },
    "advice": [],
    "skin_mbti": {
        "code": "UNKNOWN",
        "dry_oily": {"label": "-"},
        "sensitive_resistant": {"label": "-"},
        "pigmented_nonpigmented": {"label": "-"},
        "wrinkled_tight": {"label": "-"},
    },
    "report": {
        "overall_score": 0,
        "overall_level": "분석 준비 중",
        "summary": "아직 분석 결과가 없습니다.",
        "top_concerns": [],
        "condition_cards": [],
        "product_recommendations": [],
        "routine": {
            "morning": [],
            "evening": [],
        },
        "disclaimer": "결과를 불러오지 못했습니다. 다시 시도해 주세요.",
    },
}


def merge_result_data(defaults, incoming):
    """Recursively merge result data so templates can render safely."""
    if not isinstance(defaults, dict):
        return incoming if incoming is not None else defaults

    merged = deepcopy(defaults)
    if not isinstance(incoming, dict):
        return merged

    for key, value in incoming.items():
        if key in merged and isinstance(merged[key], dict):
            merged[key] = merge_result_data(merged[key], value)
        else:
            merged[key] = value
    return merged


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
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "flask"}), 200


@app.route("/test")
def test():
    """Simple sanity-check endpoint."""
    return jsonify({"message": "Flask 서버가 정상 동작 중입니다."}), 200


@app.route("/analyze", methods=["GET"])
def analyze_get():
    """Informational endpoint for direct GET access."""
    return jsonify(
        {
            "message": "이 경로는 분석 전송용입니다. 브라우저에서는 http://127.0.0.1:5000 에서 이용해 주세요."
        }
    ), 200


@app.route("/analyze", methods=["POST"])
def analyze():
    """Receive the form, forward it to the backend, and render the result page."""
    try:
        file = request.files.get("photo")
        if not file or file.filename == "":
            logger.warning("Analyze request received with no file")
            return render_template("index.html", error="사진 파일을 선택해 주세요."), 400

        file_size = getattr(file, "content_length", None)
        if file_size is None:
            file.seek(0, 2)
            file_size = file.tell()
            file.seek(0)

        is_valid, error_msg = validate_file_upload(file.filename, file_size)
        if not is_valid:
            logger.warning("Invalid file upload: %s", error_msg)
            file.seek(0)
            return render_template("index.html", error=error_msg), 400

        file.seek(0)
        file_bytes = file.read()
        mime_type = file.mimetype or "image/jpeg"
        preview_data = base64.b64encode(file_bytes).decode("utf-8")
        preview_url = f"data:{mime_type};base64,{preview_data}"

        files = {"file": (create_safe_filename(file.filename), io.BytesIO(file_bytes), mime_type)}
        data = request.form.to_dict(flat=True)

        logger.info("Sending analysis request for file: %s", file.filename)
        response = requests.post(BACKEND_URL, files=files, data=data, timeout=30)

        if response.status_code == 400:
            error_data = response.json()
            error_msg = error_data.get("error", "잘못된 요청입니다.")
            logger.warning("Backend returned 400: %s", error_msg)
            return render_template("index.html", error=f"사진 분석에 실패했습니다. {error_msg}"), 400

        if response.status_code == 503:
            error_data = response.json()
            error_msg = error_data.get("error", "AI 모델이 준비되지 않았습니다.")
            logger.error("Backend returned 503: %s", error_msg)
            return render_template("index.html", error=error_msg), 503

        if response.status_code != 200:
            logger.error("Backend returned %s", response.status_code)
            return render_template("index.html", error="서버 오류가 발생했습니다."), 500

        result = merge_result_data(DEFAULT_RESULT, response.json())
        result["uploaded_preview"] = preview_url
        logger.info("Analysis completed successfully")
        return render_template("result.html", result=result), 200

    except requests.exceptions.Timeout:
        logger.error("Backend request timeout")
        return render_template("index.html", error="분석 응답 시간이 초과되었습니다."), 504
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to backend")
        return render_template(
            "index.html",
            error="분석 서버에 연결할 수 없습니다. 백엔드가 실행 중인지 확인해 주세요.",
        ), 503
    except Exception as exc:
        logger.error("Error processing analysis: %s", exc)
        return render_template("index.html", error=f"오류가 발생했습니다: {exc}"), 500


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


if __name__ == "__main__":
    logger.info("Starting Flask application")
    app.run(debug=True, host="127.0.0.1", port=5000)
