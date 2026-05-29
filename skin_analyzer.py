"""Skin analysis helpers for the web app."""
from typing import Any, Dict, List

import cv2
import numpy as np
from PIL import Image

from config import (
    FACE_DETECTION_MIN_NEIGHBORS,
    FACE_DETECTION_MIN_SIZE,
    FACE_DETECTION_SCALE_FACTOR,
    SKIN_ADVICE,
    TARGET_IMAGE_SIZE,
)
from hyafilia_products import PRODUCTS
from logger import setup_logger

logger = setup_logger(__name__)


def clamp_score(value: float) -> int:
    """Clamp a numeric value into a 0-100 score."""
    return int(np.clip(round(value), 0, 100))


def score_to_level(score: int, inverse: bool = False) -> str:
    """Convert a numeric score to a qualitative label."""
    normalized = 100 - score if inverse else score
    if normalized >= 75:
        return "\uB192\uC74C"
    if normalized >= 50:
        return "\uC8FC\uC758"
    if normalized >= 25:
        return "\uBCF4\uD1B5"
    return "\uB0AE\uC74C"


class SkinAnalyzer:
    """Skin analysis using simple computer vision heuristics."""

    def __init__(self) -> None:
        cascade_names = [
            "haarcascade_frontalface_default.xml",
            "haarcascade_frontalface_alt2.xml",
            "haarcascade_frontalface_alt.xml",
        ]
        self.face_cascades = [
            (name, cv2.CascadeClassifier(cv2.data.haarcascades + name))
            for name in cascade_names
        ]

    @staticmethod
    def _load_image_bgr(image_path: str) -> np.ndarray | None:
        """Load an image safely on Windows paths that may contain non-ASCII characters."""
        try:
            data = np.fromfile(image_path, dtype=np.uint8)
            if data.size == 0:
                return None
            image = cv2.imdecode(data, cv2.IMREAD_COLOR)
            return image
        except Exception as exc:
            logger.warning("Failed to load image bytes for %s: %s", image_path, exc)
            return None

    def detect_face(self, image_path: str) -> bool:
        """Detect whether the image contains a face."""
        try:
            available_cascades = [
                (name, classifier)
                for name, classifier in self.face_cascades
                if not classifier.empty()
            ]
            if not available_cascades:
                logger.warning(
                    "OpenCV cascade files could not be loaded in this environment. "
                    "Skipping strict face detection for %s.",
                    image_path,
                )
                return True

            image = self._load_image_bgr(image_path)
            if image is None:
                logger.warning("Could not load image for face detection: %s", image_path)
                return True

            height, width = image.shape[:2]
            if max(width, height) > 1200:
                scale = 1200 / max(width, height)
                image = cv2.resize(image, (int(width * scale), int(height * scale)))

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)

            for name, classifier in available_cascades:
                try:
                    faces = classifier.detectMultiScale(
                        gray,
                        scaleFactor=max(1.05, FACE_DETECTION_SCALE_FACTOR),
                        minNeighbors=max(2, FACE_DETECTION_MIN_NEIGHBORS),
                        minSize=FACE_DETECTION_MIN_SIZE,
                    )
                    if len(faces) > 0:
                        logger.debug(
                            "Face detected with %s: %s faces in %s",
                            name,
                            len(faces),
                            image_path,
                        )
                        return True
                except cv2.error as exc:
                    logger.warning("Cascade %s failed during face detection: %s", name, exc)

            logger.warning("No faces detected in image: %s", image_path)
            return False
        except Exception as exc:
            logger.error("Face detection failed: %s", exc, exc_info=True)
            return False

    @staticmethod
    def _rgb_to_hsv(rgb: np.ndarray) -> np.ndarray:
        """Convert RGB image data to HSV."""
        rgb = rgb.astype("float32") / 255.0
        maxc = np.max(rgb, axis=-1)
        minc = np.min(rgb, axis=-1)
        diff = maxc - minc

        h = np.zeros_like(maxc)
        mask = diff != 0
        safe_diff = np.where(mask, diff, 1.0)
        rc = (maxc - rgb[..., 0]) / safe_diff
        gc = (maxc - rgb[..., 1]) / safe_diff
        bc = (maxc - rgb[..., 2]) / safe_diff

        red_mask = mask & (maxc == rgb[..., 0])
        green_mask = mask & (maxc == rgb[..., 1])
        blue_mask = mask & (maxc == rgb[..., 2])

        h[red_mask] = (bc - gc)[red_mask]
        h[green_mask] = (2.0 + rc - bc)[green_mask]
        h[blue_mask] = (4.0 + gc - rc)[blue_mask]
        h = (h / 6.0) % 1.0

        s = np.zeros_like(maxc)
        s[maxc != 0] = diff[maxc != 0] / maxc[maxc != 0]
        return np.dstack([h, s, maxc])

    @staticmethod
    def _estimate_age_and_gender(arr: np.ndarray, contrast: float) -> Dict[str, Any]:
        """Heuristic demographic estimate for demo UI only."""
        age = int(np.clip(18 + (contrast / 12) + (np.mean(arr[..., 0] < 100) * 25), 18, 60))
        gender = "Female" if np.mean(arr[..., 1]) > np.mean(arr[..., 0]) else "Male"
        return {"age": age, "gender": gender}

    @staticmethod
    def _build_advice(metrics: Dict[str, Any]) -> List[str]:
        """Create short advice snippets from the measured metrics."""
        advice: List[str] = []
        if metrics["wrinkle"] > 50:
            advice.append(SKIN_ADVICE.get("wrinkles", "\uC8FC\uB984 \uAC1C\uC120\uC744 \uC704\uD574 \uD0C4\uB825 \uCF00\uC5B4\uC640 \uC790\uC678\uC120 \uCC28\uB2E8\uC744 \uD568\uAED8 \uAD00\uB9AC\uD574\uBCF4\uC138\uC694."))
        if metrics["pores"] > 50:
            advice.append(SKIN_ADVICE.get("pores", "\uBAA8\uACF5 \uBD80\uB2F4\uC774 \uB192\uC544 \uBCF4\uC5EC \uD53C\uC9C0 \uC870\uC808\uACFC \uC800\uC790\uADF9 \uAC01\uC9C8 \uCF00\uC5B4\uB97C \uBCD1\uD589\uD558\uB294 \uD3B8\uC774 \uC88B\uC2B5\uB2C8\uB2E4."))
        if metrics["redness"] > 40:
            advice.append(SKIN_ADVICE.get("redness", "\uBD89\uC740\uAE30\uAC00 \uBCF4\uC774\uBA74 \uC9C4\uC815 \uC131\uBD84 \uC911\uC2EC\uC73C\uB85C \uB8E8\uD2F4\uC744 \uB2E8\uC21C\uD654\uD574\uBCF4\uC138\uC694."))
        if metrics["acne_inflamed"] > 45:
            advice.append(SKIN_ADVICE.get("acne_inflamed", "\uC5FC\uC99D\uC131 \uC5EC\uB4DC\uB984\uC774 \uBCF4\uC77C \uB54C\uB294 \uC790\uADF9\uC801\uC778 \uC2A4\uD06C\uB7FD\uBCF4\uB2E4 \uC9C4\uC815\uACFC \uAD6D\uC18C \uCF00\uC5B4\uAC00 \uC6B0\uC120\uC785\uB2C8\uB2E4."))
        if metrics["acne_noninflamed"] > 45:
            advice.append(SKIN_ADVICE.get("acne_noninflamed", "\uD654\uC774\uD2B8\uD5E4\uB4DC\uC640 \uBE14\uB799\uD5E4\uB4DC \uACBD\uD5A5\uC774 \uBCF4\uC774\uBA74 BHA \uB610\uB294 PHA \uC911\uC2EC\uC758 \uCF00\uC5B4\uAC00 \uB3C4\uC6C0\uC774 \uB429\uB2C8\uB2E4."))
        if metrics["pigmentation"] > 40:
            advice.append(SKIN_ADVICE.get("pigmentation", "\uC0C9\uC18C\uCE68\uCC29\uC740 \uBE0C\uB77C\uC774\uD2B8\uB2DD \uC138\uB7FC\uACFC \uAFB8\uC900\uD55C \uC120\uCF00\uC5B4\uB97C \uAC19\uC774 \uC7A1\uC544\uC8FC\uB294 \uAC83\uC774 \uC88B\uC2B5\uB2C8\uB2E4."))
        if metrics["skin_scores"]["health"] < 50:
            advice.append("\uC218\uBD84 \uACF5\uAE09\uACFC \uCDA9\uBD84\uD55C \uD734\uC2DD\uC774 \uD53C\uBD80 \uCEE8\uB514\uC158 \uD68C\uBCF5\uC5D0 \uC911\uC694\uD569\uB2C8\uB2E4.")
        if not advice:
            advice.append("\uD604\uC7AC \uD53C\uBD80 \uCEE8\uB514\uC158\uC740 \uBE44\uAD50\uC801 \uC548\uC815\uC801\uC785\uB2C8\uB2E4. \uAE30\uBCF8 \uB8E8\uD2F4\uC744 \uAFB8\uC900\uD788 \uC720\uC9C0\uD574\uBCF4\uC138\uC694.")
        return advice

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Analyze the provided image and return skin metrics."""
        if not self.detect_face(image_path):
            raise ValueError("\uC5BC\uAD74\uC774 \uAC10\uC9C0\uB418\uC9C0 \uC54A\uC558\uC2B5\uB2C8\uB2E4. \uC815\uBA74 \uC5BC\uAD74 \uC0AC\uC9C4\uC744 \uC5C5\uB85C\uB4DC\uD574\uC8FC\uC138\uC694.")

        with Image.open(image_path) as image:
            image = image.convert("RGB")
            image = image.resize(TARGET_IMAGE_SIZE)
            arr = np.array(image)

        gray = np.dot(arr[..., :3], [0.2989, 0.5870, 0.1140])
        hsv = self._rgb_to_hsv(arr)
        dark_spots = float(np.mean(gray < (np.mean(gray) * 0.75)))
        red_score = float(np.mean(np.maximum(0, arr[..., 0] - np.maximum(arr[..., 1], arr[..., 2]))))

        brightness = int(round(float(np.mean(gray))))
        saturation = int(round(float(np.mean(hsv[..., 1]) * 100)))
        contrast = int(round(float(np.std(gray))))

        skin_scores = {
            "acne": clamp_score(red_score * 20),
            "stain": clamp_score(dark_spots * 100),
            "health": clamp_score(
                100
                - (red_score * 0.9)
                - (dark_spots * 35)
                - max(0, 125 - brightness) * 0.25
                + (saturation * 0.18)
            ),
        }

        metrics = {
            "brightness": brightness,
            "saturation": saturation,
            "contrast": contrast,
            "wrinkle": clamp_score(np.mean(np.abs(np.gradient(gray)[0]) + np.abs(np.gradient(gray)[1])) * 0.5 + np.std(gray) * 0.3 + dark_spots * 20),
            "pores": clamp_score(dark_spots * 100 * 0.7 + np.std(gray) * 0.2),
            "redness": clamp_score(red_score * 2.0),
            "acne_inflamed": clamp_score(clamp_score(red_score * 2.0) * 0.45 + dark_spots * 100 * 0.3 + np.std(gray) * 0.1),
            "acne_noninflamed": clamp_score((100 - saturation) * 0.2 + dark_spots * 100 * 0.2 + (120 - brightness) * 0.1),
            "skin_tone": clamp_score((130 - brightness) * 0.8 + (100 - saturation) * 0.1),
            "sagging": clamp_score((100 - contrast) * 0.45 + (110 - brightness) * 0.2 + (100 - skin_scores["health"]) * 0.1),
            "pigmentation": clamp_score(np.mean((hsv[..., 0] > 0.04) & (hsv[..., 0] < 0.15) & (hsv[..., 1] > 0.25) & (arr[..., 0] > arr[..., 1])) * 120 + dark_spots * 50),
            "oil_balance": clamp_score(saturation * 0.5 + brightness * 0.1),
            "skin_scores": skin_scores,
        }

        metrics.update(self._estimate_age_and_gender(arr, float(np.std(gray))))
        return {"analysis": metrics, "advice": self._build_advice(metrics)}


def _classify_answer_group(form: dict, key: str, a_label: str, a_name: str, b_label: str, b_name: str) -> dict:
    """Pick the dominant trait for a MBTI-like answer group."""
    answers = [form.get(f"{key}_{i}", "").strip().upper() for i in range(1, 4)]
    count_a = sum(1 for value in answers if value == "A")
    count_b = sum(1 for value in answers if value == "B")
    if count_a == 0 and count_b == 0:
        return {"code": "?", "label": "Unknown"}
    if count_a >= count_b:
        return {"code": a_label, "label": a_name}
    return {"code": b_label, "label": b_name}


def parse_skin_mbti(form: dict) -> dict:
    """Parse skin questionnaire answers into a skin MBTI style code."""
    dry_oily = _classify_answer_group(form, "dry_oily", "D", "Dry", "O", "Oily")
    sensitive_resistant = _classify_answer_group(form, "sensitive_resistant", "S", "Sensitive", "R", "Resistant")
    pigmented_nonpigmented = _classify_answer_group(form, "pigmented_nonpigmented", "P", "Pigmented", "N", "Non-pigmented")
    wrinkled_tight = _classify_answer_group(form, "wrinkled_tight", "W", "Wrinkled", "T", "Tight")
    return {
        "code": f"{dry_oily['code']}{sensitive_resistant['code']}{pigmented_nonpigmented['code']}{wrinkled_tight['code']}",
        "dry_oily": dry_oily,
        "sensitive_resistant": sensitive_resistant,
        "pigmented_nonpigmented": pigmented_nonpigmented,
        "wrinkled_tight": wrinkled_tight,
    }


def build_condition_cards(metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create structured condition summaries for the result page."""
    return [
        {
            "key": "wrinkle",
            "label": "\uC8FC\uB984",
            "score": metrics["wrinkle"],
            "level": score_to_level(metrics["wrinkle"]),
            "focus_area": "\uC774\uB9C8, \uBBF8\uAC04, \uB208\uAC00, \uD314\uC790 \uBD80\uC704",
            "description": "\uD45C\uC815 \uC8FC\uB984\uACFC \uBBF8\uC138 \uC8FC\uB984 \uD328\uD134\uC744 \uBC14\uD0D5\uC73C\uB85C \uD0C4\uB825 \uC800\uD558 \uC2E0\uD638\uB97C \uCD94\uC815\uD588\uC2B5\uB2C8\uB2E4.",
        },
        {
            "key": "pores",
            "label": "\uBAA8\uACF5",
            "score": metrics["pores"],
            "level": score_to_level(metrics["pores"]),
            "focus_area": "\uB098\uBE44\uC874 \uC911\uC2EC",
            "description": "\uCF54 \uC8FC\uBCC0\uACFC \uC591 \uBCFC\uC758 \uAC70\uCE60\uAE30\uC640 \uC810\uC0C1 \uBD84\uD3EC\uB97C \uBC14\uD0D5\uC73C\uB85C \uBAA8\uACF5 \uBD80\uB2F4\uC744 \uACC4\uC0B0\uD588\uC2B5\uB2C8\uB2E4.",
        },
        {
            "key": "redness",
            "label": "\uBD89\uC740\uAE30",
            "score": metrics["redness"],
            "level": score_to_level(metrics["redness"]),
            "focus_area": "\uB098\uBE44\uC874\uACFC \uBCFC \uC911\uC559",
            "description": "\uBBF8\uB9CC\uC131 \uD64D\uC870\uC640 \uC790\uADF9\uC73C\uB85C \uBCF4\uC774\uB294 \uBD89\uC740 \uC601\uC5ED\uC744 \uAE30\uC900\uC73C\uB85C \uBBFC\uAC10\uB3C4\uB97C \uCD94\uC815\uD588\uC2B5\uB2C8\uB2E4.",
        },
        {
            "key": "acne_inflamed",
            "label": "\uC5FC\uC99D\uC131 \uC5EC\uB4DC\uB984",
            "score": metrics["acne_inflamed"],
            "level": score_to_level(metrics["acne_inflamed"]),
            "focus_area": "\uB18D\uD3EC, \uAD6C\uC9C4, \uACB0\uC808 \uAC00\uB2A5 \uC601\uC5ED",
            "description": "\uBD89\uC740 \uB3CC\uAE30\uC640 \uC5FC\uC99D \uC9D5\uD6C4\uB97C \uAE30\uC900\uC73C\uB85C \uD2B8\uB7EC\uBE14 \uAC15\uB3C4\uB97C \uBD84\uC11D\uD588\uC2B5\uB2C8\uB2E4.",
        },
        {
            "key": "acne_noninflamed",
            "label": "\uBE44\uC5FC\uC99D\uC131 \uC5EC\uB4DC\uB984",
            "score": metrics["acne_noninflamed"],
            "level": score_to_level(metrics["acne_noninflamed"]),
            "focus_area": "\uD654\uC774\uD2B8\uD5E4\uB4DC, \uBE14\uB799\uD5E4\uB4DC \uBD84\uD3EC",
            "description": "\uD53C\uC9C0 \uC815\uCCB4\uC640 \uBA74\uD3EC\uC131 \uC694\uCCA0 \uD328\uD134\uC744 \uC911\uC2EC\uC73C\uB85C \uBD84\uC11D\uD588\uC2B5\uB2C8\uB2E4.",
        },
        {
            "key": "skin_tone",
            "label": "\uD53C\uBD80\uD1A4",
            "score": metrics["skin_tone"],
            "level": score_to_level(metrics["skin_tone"]),
            "focus_area": "\uC804\uBC18\uC801\uC778 \uBA85\uB3C4\uC640 \uADE0\uC77C\uB3C4",
            "description": "\uD53C\uBD80\uC758 \uC5B4\uB450\uC6C0 \uC815\uB3C4\uC640 \uD1A4 \uD3B8\uCC28\uB97C \uBC14\uD0D5\uC73C\uB85C \uCE59\uCE59\uD568 \uC815\uB3C4\uB97C \uCD94\uC815\uD588\uC2B5\uB2C8\uB2E4.",
        },
        {
            "key": "sagging",
            "label": "\uD53C\uBD80 \uCC98\uC9D0",
            "score": metrics["sagging"],
            "level": score_to_level(metrics["sagging"]),
            "focus_area": "\uD314\uC790, \uB9C8\uB9AC\uC624\uB137, \uD558\uAD00 \uB77C\uC778",
            "description": "\uD0C4\uB825 \uC800\uD558\uC640 \uADF8\uB9BC\uC790 \uAE4A\uC774\uB97C \uC774\uC6A9\uD574 \uC724\uACFD \uCC98\uC9D0 \uC815\uB3C4\uB97C \uACC4\uC0B0\uD588\uC2B5\uB2C8\uB2E4.",
        },
        {
            "key": "pigmentation",
            "label": "\uC0C9\uC18C\uCE68\uCC29",
            "score": metrics["pigmentation"],
            "level": score_to_level(metrics["pigmentation"]),
            "focus_area": "\uAE30\uBBF8, \uC7A1\uD2F0, \uC5FC\uC99D \uD6C4 \uD754\uC801",
            "description": "\uAC08\uC0C9\u00B7\uBD89\uC740\uC0C9 \uACC4\uC5F4\uC758 \uC0C9\uC18C\uD654\uB41C \uBA74\uC801\uC744 \uBC14\uD0D5\uC73C\uB85C \uD754\uC801\uACFC \uC7A1\uD2F0\uB97C \uCD94\uC815\uD588\uC2B5\uB2C8\uB2E4.",
        },
        {
            "key": "oil_balance",
            "label": "\uC720\uC218\uBD84 \uBC38\uB7F0\uC2A4",
            "score": metrics["oil_balance"],
            "level": score_to_level(abs(metrics["oil_balance"] - 50) * 2),
            "focus_area": "\uD53C\uC9C0 \uAD11\uD0DD\uACFC \uC218\uBD84 \uC720\uC9C0\uB825",
            "description": "\uAD11\uD0DD\uACFC \uCC44\uB3C4\uB97C \uAE30\uBC18\uC73C\uB85C \uC720\uBD84 \uC6B0\uC138 \uB610\uB294 \uAC74\uC870 \uC6B0\uC138 \uAC00\uB2A5\uC131\uC744 \uCD94\uC815\uD588\uC2B5\uB2C8\uB2E4.",
        },
    ]


def _copy_product(key: str) -> Dict[str, str]:
    """Return a copy of an official product definition."""
    return dict(PRODUCTS[key])


def build_product_recommendations(metrics: Dict[str, Any], skin_mbti: Dict[str, Any]) -> List[Dict[str, str]]:
    """Select official Hyafilia USA products only."""
    code = skin_mbti.get("code", "????")
    recommendations: List[Dict[str, str]] = [
        _copy_product("cleanser"),
        _copy_product("soothing_toner"),
    ]

    needs_acne = metrics["acne_inflamed"] >= 45 or metrics["acne_noninflamed"] >= 45 or code.startswith("O")
    needs_wrinkle = metrics["wrinkle"] >= 45 or metrics["sagging"] >= 45 or code.endswith("W")
    needs_dryness = code.startswith("D") or skin_mbti.get("sensitive_resistant", {}).get("code") == "S" or metrics["skin_scores"]["health"] < 55
    needs_pigment = metrics["pigmentation"] >= 40 or "P" in code

    if needs_acne:
        recommendations.append(_copy_product("blemish_cream"))
    elif needs_wrinkle or needs_pigment:
        recommendations.append(_copy_product("retinol"))
    else:
        recommendations.append(_copy_product("moisture_ampoule"))

    if needs_dryness:
        recommendations.append(_copy_product("soothing_cream"))
    elif not needs_acne:
        recommendations.append(_copy_product("moisture_ampoule"))

    recommendations.append(_copy_product("sunscreen"))

    unique_products: List[Dict[str, str]] = []
    seen: set[str] = set()
    for product in recommendations:
        if product["key"] in seen:
            continue
        seen.add(product["key"])
        unique_products.append(product)

    return unique_products


def build_routine(metrics: Dict[str, Any], skin_mbti: Dict[str, Any], products: List[Dict[str, str]]) -> Dict[str, List[str]]:
    """Build a routine that references only official Hyafilia USA products."""
    product_map = {product["key"]: product for product in products}

    morning = [
        f"세안은 {product_map['cleanser']['name']}로 가볍게 시작합니다.",
        f"피부 결 정돈은 {product_map['soothing_toner']['name']}로 진행합니다.",
    ]

    evening = [
        f"저녁 세안은 {product_map['cleanser']['name']}로 부드럽게 마무리합니다.",
        f"세안 후 {product_map['soothing_toner']['name']}로 피부를 진정시키고 다음 단계를 준비합니다.",
    ]

    if "moisture_ampoule" in product_map:
        morning.append(f"수분 보충이 필요하면 {product_map['moisture_ampoule']['name']}를 얇게 레이어링합니다.")
        evening.append(f"건조함이 느껴지는 날에는 {product_map['moisture_ampoule']['name']}를 충분히 사용합니다.")

    if "blemish_cream" in product_map:
        morning.append(f"트러블 관리가 필요한 부위에는 {product_map['blemish_cream']['name']}를 소량 사용합니다.")
        evening.append(f"트러블 진정 단계로 {product_map['blemish_cream']['name']}를 집중 사용합니다.")

    if "retinol" in product_map:
        evening.append(f"탄력과 결 케어를 위해 밤에는 {product_map['retinol']['name']}를 소량 사용합니다.")

    if "soothing_cream" in product_map:
        evening.append(f"마지막 보습막은 {product_map['soothing_cream']['name']}로 정리합니다.")
        morning.append(f"건조하거나 예민한 날 아침에는 {product_map['soothing_cream']['name']}를 얇게 덧발라 줍니다.")

    morning.append(f"외출 전에는 {product_map['sunscreen']['name']}로 자외선 차단을 마무리합니다.")

    return {"morning": morning[:5], "evening": evening[:5]}


def build_personalized_report(metrics: Dict[str, Any], skin_mbti: Dict[str, Any]) -> Dict[str, Any]:
    """Create an explainable report payload for the frontend."""
    cards = build_condition_cards(metrics)
    top_concerns = sorted(
        [card for card in cards if card["key"] != "oil_balance"],
        key=lambda item: item["score"],
        reverse=True,
    )[:3]

    overall_score = clamp_score(
        metrics["skin_scores"]["health"] * 0.5
        + (100 - metrics["wrinkle"]) * 0.1
        + (100 - metrics["pigmentation"]) * 0.1
        + (100 - metrics["redness"]) * 0.1
        + (100 - metrics["acne_inflamed"]) * 0.1
        + (100 - metrics["pores"]) * 0.1
    )

    overall_level = (
        "\uC548\uC815"
        if overall_score >= 75
        else "\uC9D1\uC911 \uAD00\uB9AC"
        if overall_score < 45
        else "\uAD00\uB9AC \uD544\uC694"
    )

    summary = (
        f"{skin_mbti.get('code', '????')} \uD0C0\uC785 \uACBD\uD5A5\uC774 \uBCF4\uC774\uBA70, "
        f"\uD604\uC7AC \uC6B0\uC120 \uAD00\uB9AC \uD3EC\uC778\uD2B8\uB294 "
        f"{top_concerns[0]['label']}, {top_concerns[1]['label']}, {top_concerns[2]['label']}\uC785\uB2C8\uB2E4."
    )

    products = build_product_recommendations(metrics, skin_mbti)

    return {
        "overall_score": overall_score,
        "overall_level": overall_level,
        "summary": summary,
        "top_concerns": top_concerns,
        "condition_cards": cards,
        "product_recommendations": products,
        "routine": build_routine(metrics, skin_mbti, products),
        "disclaimer": "\uC774 \uACB0\uACFC\uB294 \uC0AC\uC9C4 \uAE30\uBC18 \uCC38\uACE0\uC6A9 \uBD84\uC11D\uC774\uBA70, \uD53C\uBD80 \uC9C8\uD658\uC774 \uC758\uC2EC\uB418\uBA74 \uC804\uBB38 \uC9C4\uB8CC\uAC00 \uC6B0\uC120\uC785\uB2C8\uB2E4.",
    }


def analyze_image(image_path: str) -> dict:
    """Analyze image using the shared SkinAnalyzer instance."""
    analyzer = SkinAnalyzer()
    result = analyzer.analyze_image(image_path)
    logger.debug("Returned analysis result for %s", image_path)
    return result


def ensure_face_image(image_path: str) -> None:
    """Validate that the uploaded image contains a face before AI inference."""
    analyzer = SkinAnalyzer()
    if not analyzer.detect_face(image_path):
        raise ValueError("정면 얼굴 사진을 다시 업로드해 주세요.")


def _copy_products_by_keys(product_keys: List[str]) -> List[Dict[str, str]]:
    """Return official product definitions while preserving order and uniqueness."""
    seen: set[str] = set()
    selected: List[Dict[str, str]] = []
    for key in product_keys:
        if key in seen:
            continue
        seen.add(key)
        selected.append(_copy_product(key))
    return selected


def build_pytorch_product_recommendations(
    skin_mbti: Dict[str, Any], analysis: Dict[str, Any] | None = None
) -> List[Dict[str, str]]:
    """Build product recommendations from the questionnaire and AI skin analysis."""
    code = skin_mbti.get("code", "????")
    analysis = analysis or {}
    prediction_route = analysis.get("prediction_route", "unknown")
    skin_score = float(analysis.get("skin_score", analysis.get("pytorch_confidence", 0)) or 0)
    acne_count = int(analysis.get("acne_count", 0) or 0)
    severity_ratio = float(analysis.get("severity_ratio", 0) or 0)
    keys = ["cleanser", "soothing_toner"]

    if code.startswith("D"):
        keys.extend(["moisture_ampoule", "soothing_cream"])
    else:
        keys.extend(["blemish_cream", "moisture_ampoule"])

    if prediction_route == "acne" or acne_count > 0 or severity_ratio >= 0.2:
        keys.append("blemish_cream")

    if skin_score and skin_score < 65:
        keys.extend(["moisture_ampoule", "soothing_cream"])

    if "W" in code or "P" in code:
        keys.append("retinol")

    keys.append("sunscreen")
    return _copy_products_by_keys(keys)


def build_pytorch_condition_cards(analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Turn PyTorch class scores into explainable result cards."""
    class_scores = analysis.get("pytorch_class_scores", {})
    if not class_scores:
        return []

    cards: List[Dict[str, Any]] = []
    for label, score in sorted(class_scores.items(), key=lambda item: item[1], reverse=True):
        score_value = clamp_score(score)
        cards.append(
            {
                "key": label,
                "label": label,
                "score": score_value,
                "level": score_to_level(score_value),
                "focus_area": "AI 분석 결과",
                "description": f"AI가 이 클래스로 판단한 확률입니다. 현재 점수는 {score_value}점입니다.",
            }
        )
    return cards


def build_pytorch_routine(
    products: List[Dict[str, str]], analysis: Dict[str, Any] | None = None
) -> Dict[str, List[str]]:
    """Build a routine around selected products and AI analysis signals."""
    product_map = {product["key"]: product for product in products}
    analysis = analysis or {}
    prediction_route = analysis.get("prediction_route", "unknown")
    predicted_class = analysis.get("pytorch_predicted_class", "unknown")
    confidence = float(analysis.get("pytorch_confidence", 0) or 0)
    skin_score = float(analysis.get("skin_score", confidence) or 0)
    acne_count = int(analysis.get("acne_count", 0) or 0)
    severity_ratio = float(analysis.get("severity_ratio", 0) or 0)
    acne_signal = prediction_route == "acne" or acne_count > 0 or severity_ratio >= 0.2

    morning = [
        f"{product_map['cleanser']['name']}로 세안을 시작합니다.",
        f"{product_map['soothing_toner']['name']}로 피부 결을 정돈합니다.",
    ]
    evening = [
        f"{product_map['cleanser']['name']}로 메이크업과 노폐물을 정리합니다.",
        f"{product_map['soothing_toner']['name']}로 피부를 편안하게 진정시킵니다.",
    ]

    if "moisture_ampoule" in product_map:
        morning.append(f"{product_map['moisture_ampoule']['name']}로 수분을 채워줍니다.")
        evening.append(f"{product_map['moisture_ampoule']['name']}를 충분히 레이어링합니다.")

    if acne_signal and "blemish_cream" in product_map:
        morning.append(f"AI가 {predicted_class} 경향을 감지해 트러블 부위에는 {product_map['blemish_cream']['name']}를 소량만 사용합니다.")

    if "blemish_cream" in product_map:
        evening.append(f"트러블 부위에는 {product_map['blemish_cream']['name']}를 가볍게 사용합니다.")

    if "retinol" in product_map:
        evening.append(f"탄력 관리가 필요할 때 {product_map['retinol']['name']}를 밤 루틴에 추가합니다.")

    if "soothing_cream" in product_map:
        morning.append(f"건조함이 느껴지면 {product_map['soothing_cream']['name']}로 마무리합니다.")
        evening.append(f"{product_map['soothing_cream']['name']}로 보습막을 마무리합니다.")

    if confidence < 60:
        morning.append("AI 신뢰도가 낮은 편이므로 오늘은 자극적인 기능성 제품보다 진정과 보습 위주로 단순하게 유지합니다.")
        evening.append("분석 신뢰도가 낮아 밤에는 새 제품을 늘리기보다 기존 진정 루틴을 유지합니다.")
    elif skin_score and skin_score < 60:
        morning.append("AI 피부 점수가 낮게 나와 낮 동안 보습막을 얇게 유지하고 손으로 만지는 자극을 줄입니다.")
        evening.append("AI 피부 점수가 낮게 나와 밤에는 트러블 부위 케어 후 보습 단계를 충분히 가져갑니다.")
    elif prediction_route == "healthy" and skin_score >= 85:
        morning.append("AI가 안정적인 피부 상태로 판단했으므로 아침 루틴은 가볍게 유지합니다.")
        evening.append("안정적인 상태를 유지할 수 있게 밤에는 세안과 보습을 과하게 늘리지 않습니다.")

    morning.append(f"외출 전에는 {product_map['sunscreen']['name']}로 자외선 차단을 마무리합니다.")

    routine_steps: List[Dict[str, str]] = [
        {
            "period": "아침",
            "title": "1. 세안",
            "description": "가볍게 노폐물을 정리합니다.",
            "product_name": product_map["cleanser"]["name"],
            "product_url": product_map["cleanser"]["url"],
            "product_image_url": product_map["cleanser"]["image_url"],
        },
        {
            "period": "아침",
            "title": "2. 토너",
            "description": "피부결을 편안하게 정돈합니다.",
            "product_name": product_map["soothing_toner"]["name"],
            "product_url": product_map["soothing_toner"]["url"],
            "product_image_url": product_map["soothing_toner"]["image_url"],
        },
    ]

    if "moisture_ampoule" in product_map:
        routine_steps.append(
            {
                "period": "아침",
                "title": "3. 수분 앰플",
                "description": "산뜻하게 수분을 채워줍니다.",
                "product_name": product_map["moisture_ampoule"]["name"],
                "product_url": product_map["moisture_ampoule"]["url"],
                "product_image_url": product_map["moisture_ampoule"]["image_url"],
            }
        )

    if "soothing_cream" in product_map:
        routine_steps.append(
            {
                "period": "아침",
                "title": "4. 보습 크림",
                "description": "건조함이 남지 않도록 마무리합니다.",
                "product_name": product_map["soothing_cream"]["name"],
                "product_url": product_map["soothing_cream"]["url"],
                "product_image_url": product_map["soothing_cream"]["image_url"],
            }
        )

    routine_steps.append(
        {
            "period": "아침",
            "title": "5. 자외선 차단",
            "description": "외출 전 피부를 보호합니다.",
            "product_name": product_map["sunscreen"]["name"],
            "product_url": product_map["sunscreen"]["url"],
            "product_image_url": product_map["sunscreen"]["image_url"],
        }
    )

    routine_steps.append(
        {
            "period": "저녁",
            "title": "1. 클렌징",
            "description": "메이크업과 노폐물을 정리합니다.",
            "product_name": product_map["cleanser"]["name"],
            "product_url": product_map["cleanser"]["url"],
            "product_image_url": product_map["cleanser"]["image_url"],
        }
    )
    routine_steps.append(
        {
            "period": "저녁",
            "title": "2. 진정 토너",
            "description": "피부를 차분하게 정돈합니다.",
            "product_name": product_map["soothing_toner"]["name"],
            "product_url": product_map["soothing_toner"]["url"],
            "product_image_url": product_map["soothing_toner"]["image_url"],
        }
    )

    if "blemish_cream" in product_map:
        routine_steps.append(
            {
                "period": "저녁",
                "title": "3. 트러블 케어",
                "description": "고민 부위에 가볍게 사용합니다.",
                "product_name": product_map["blemish_cream"]["name"],
                "product_url": product_map["blemish_cream"]["url"],
                "product_image_url": product_map["blemish_cream"]["image_url"],
            }
        )

    if "retinol" in product_map:
        routine_steps.append(
            {
                "period": "저녁",
                "title": "4. 탄력 케어",
                "description": "밤 시간에 집중적으로 관리합니다.",
                "product_name": product_map["retinol"]["name"],
                "product_url": product_map["retinol"]["url"],
                "product_image_url": product_map["retinol"]["image_url"],
            }
        )

    if "moisture_ampoule" in product_map:
        routine_steps.append(
            {
                "period": "저녁",
                "title": "5. 수분 보충",
                "description": "충분히 레이어링해 마무리합니다.",
                "product_name": product_map["moisture_ampoule"]["name"],
                "product_url": product_map["moisture_ampoule"]["url"],
                "product_image_url": product_map["moisture_ampoule"]["image_url"],
            }
        )

    if "soothing_cream" in product_map:
        routine_steps.append(
            {
                "period": "저녁",
                "title": "6. 보습 마감",
                "description": "잠들기 전 보습막을 더합니다.",
                "product_name": product_map["soothing_cream"]["name"],
                "product_url": product_map["soothing_cream"]["url"],
                "product_image_url": product_map["soothing_cream"]["image_url"],
            }
        )

    period_counters = {"아침": 0, "저녁": 0}
    for step in routine_steps:
        period = step["period"]
        period_counters[period] += 1
        title_body = step["title"].split(". ", 1)[1] if ". " in step["title"] else step["title"]
        step["title"] = f"{period_counters[period]}. {title_body}"

    return {"morning": morning[:6], "evening": evening[:6], "steps": routine_steps}


def build_pytorch_advice(analysis: Dict[str, Any], skin_mbti: Dict[str, Any]) -> List[str]:
    """Build short guidance lines from the .pth result and questionnaire."""
    predicted_class = analysis.get("pytorch_predicted_class", "unknown")
    confidence = round(float(analysis.get("pytorch_confidence", 0)), 2)
    code = skin_mbti.get("code", "????")

    advice = [
        f"AI 분석 결과 이번 사진은 {predicted_class} 패턴으로 {confidence}% 신뢰도로 분류되었습니다.",
        "결과는 사진 분석과 설문 응답을 바탕으로 정리되었습니다.",
    ]

    if confidence < 60:
        advice.append("정면 사진과 밝은 조명으로 다시 촬영하면 더 안정적인 결과를 볼 수 있습니다.")

    if code.startswith("D"):
        advice.append("설문상 건조 성향이 보여 수분 앰플과 보습 크림 중심 루틴을 권장합니다.")
    elif code.startswith("O"):
        advice.append("설문상 유분 성향이 보여 가벼운 진정 케어와 트러블 관리 제품을 우선 추천합니다.")

    if "W" in code or "P" in code:
        advice.append("탄력 또는 색소 고민 응답이 있어 야간 기능성 케어를 함께 제안합니다.")

    return advice


def build_pytorch_personalized_report(analysis: Dict[str, Any], skin_mbti: Dict[str, Any]) -> Dict[str, Any]:
    """Create a report payload driven by the .pth model output."""
    predicted_class = analysis.get("pytorch_predicted_class", "unknown")
    confidence = clamp_score(float(analysis.get("pytorch_confidence", 0)))
    cards = build_pytorch_condition_cards(analysis)
    top_concerns = cards[:3]
    products = build_pytorch_product_recommendations(skin_mbti, analysis)

    if confidence >= 80:
        overall_level = "판독 신뢰 높음"
    elif confidence >= 60:
        overall_level = "판독 완료"
    else:
        overall_level = "재촬영 권장"

    summary = (
        f"AI가 이번 사진을 {predicted_class} 클래스로 분류했습니다. "
        f"현재 신뢰도는 {confidence}점이며, 설문 코드 {skin_mbti.get('code', '????')}를 함께 반영해 루틴을 구성했습니다."
    )

    return {
        "overall_score": confidence,
        "overall_level": overall_level,
        "summary": summary,
        "top_concerns": top_concerns,
        "condition_cards": cards,
        "product_recommendations": products,
        "routine": build_pytorch_routine(products, analysis),
        "disclaimer": "이 결과는 사진 분석과 설문 응답을 바탕으로 한 참고용 안내입니다.",
    }
