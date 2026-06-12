"""PyTorch model loading and inference helpers."""
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from config import PYTORCH_MODEL_LABELS, PYTORCH_MODEL_PATH
from logger import setup_logger

logger = setup_logger(__name__)

try:
    import torch
    import torch.nn.functional as F
    from PIL import Image
    from torchvision import models, transforms

    TORCH_AVAILABLE = True
    torch.set_num_threads(1)
except ImportError:
    torch = None
    F = None
    Image = None
    models = None
    transforms = None
    TORCH_AVAILABLE = False


def build_resnet18_classifier(num_classes: int):
    """Build a ResNet18 classifier matching the discovered checkpoint layout."""
    model = models.resnet18(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
    return model


def calculate_skin_pixel_ratio(image) -> float:
    """Estimate how much of the image is likely human skin using HSV ranges."""
    hsv_image = image.convert("HSV")
    hue, saturation, _ = hsv_image.split()
    hue_array = np.array(hue)
    saturation_array = np.array(saturation)

    skin_mask = ((hue_array <= 20) | (hue_array >= 160)) & (saturation_array >= 40)
    return float(np.sum(skin_mask) / (image.size[0] * image.size[1]))


def calculate_advanced_skin_score(image_bytes: bytes) -> dict:
    """Calculate a care score from redness-like regions on skin-colored pixels."""
    file_bytes = np.frombuffer(image_bytes, dtype=np.uint8)
    image_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise ValueError("Could not decode image bytes.")

    height, width = image_bgr.shape[:2]
    max_size = 640
    if max(height, width) > max_size:
        scale = max_size / max(height, width)
        image_bgr = cv2.resize(
            image_bgr,
            (int(width * scale), int(height * scale)),
            interpolation=cv2.INTER_AREA,
        )

    image_hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    total_pixels = image_bgr.shape[0] * image_bgr.shape[1]

    lower_skin = np.array([0, 30, 40], dtype=np.uint8)
    upper_skin = np.array([20, 150, 255], dtype=np.uint8)
    skin_mask = cv2.inRange(image_hsv, lower_skin, upper_skin)
    skin_pixel_count = int(np.sum(skin_mask > 0))
    if skin_pixel_count < total_pixels * 0.1:
        skin_pixel_count = total_pixels

    lower_acne = np.array([0, 80, 50], dtype=np.uint8)
    upper_acne = np.array([10, 255, 255], dtype=np.uint8)
    acne_mask = cv2.inRange(image_hsv, lower_acne, upper_acne)
    acne_in_skin = cv2.bitwise_and(acne_mask, acne_mask, mask=skin_mask)

    contours, _ = cv2.findContours(acne_in_skin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    valid_contours = [contour for contour in contours if cv2.contourArea(contour) > 15]

    acne_count = len(valid_contours)
    total_acne_area = float(sum(cv2.contourArea(contour) for contour in valid_contours))
    severity_ratio = (total_acne_area / skin_pixel_count) * 100

    count_penalty = min(30, acne_count * 1.5)
    size_penalty = min(40, (severity_ratio / 3.0) * 40)
    skin_score = int(85 - (count_penalty + size_penalty))

    return {
        "skin_score": max(10, skin_score),
        "acne_count": acne_count,
        "severity_ratio": round(float(severity_ratio), 2),
    }


def infer_prediction_route(label: str, index: int) -> str:
    """Normalize model labels into project-level care routes."""
    normalized = label.lower()
    if "acne" in normalized or "disease" in normalized or "trouble" in normalized or "여드름" in label:
        return "acne"
    if "healthy" in normalized or "normal" in normalized or "정상" in label or "건강" in label:
        return "healthy"
    if index == 0:
        return "acne"
    if index == 1:
        return "healthy"
    return "unknown"


def load_pytorch_model(
    path: Path = PYTORCH_MODEL_PATH,
    labels: Optional[list[str]] = None,
):
    """Load a local PyTorch state_dict checkpoint."""
    if not TORCH_AVAILABLE:
        raise RuntimeError("PyTorch is not installed.")

    if not path.exists():
        raise FileNotFoundError(f"PyTorch model not found: {path}")

    state_dict = torch.load(path, map_location="cpu")
    if not isinstance(state_dict, dict):
        raise ValueError("Expected a state_dict dictionary in the .pth file.")

    inferred_labels = labels or PYTORCH_MODEL_LABELS
    num_classes = state_dict["fc.weight"].shape[0]
    if len(inferred_labels) != num_classes:
        inferred_labels = [f"class_{index}" for index in range(num_classes)]

    model = build_resnet18_classifier(num_classes=num_classes)
    model.load_state_dict(state_dict, strict=True)
    model.eval()

    logger.info("Loaded PyTorch model from %s with %s classes", path, num_classes)
    return {"model": model, "labels": inferred_labels, "path": str(path)}


def predict_pytorch_skin_model(
    image_path: str,
    bundle: Optional[dict] = None,
    use_tta: bool = True,
    use_advanced_score: bool = True,
) -> Optional[dict]:
    """Run inference with the external .pth model and return class/confidence data."""
    if not TORCH_AVAILABLE:
        logger.warning("PyTorch is not installed. Skipping .pth model inference.")
        return None

    if bundle is None:
        try:
            bundle = load_pytorch_model()
        except Exception as exc:
            logger.warning("PyTorch model not available: %s", exc)
            return None

    model = bundle["model"]
    labels = bundle["labels"]

    preprocess = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    try:
        image_bytes = Path(image_path).read_bytes()
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            skin_pixel_ratio = calculate_skin_pixel_ratio(image)
            if skin_pixel_ratio < 0.03:
                return {
                    "analysis": {
                        "pytorch_predicted_class": "not_skin",
                        "pytorch_confidence": round(skin_pixel_ratio * 100, 2),
                        "pytorch_class_scores": {},
                        "prediction_route": "not_skin",
                        "skin_score": 0,
                        "acne_count": 0,
                        "severity_ratio": 0.0,
                        "skin_pixel_ratio": round(skin_pixel_ratio * 100, 2),
                    },
                    "advice": [],
                }

            tensor = preprocess(image).unsqueeze(0)
            flipped_tensor = preprocess(image.transpose(Image.FLIP_LEFT_RIGHT)).unsqueeze(0) if use_tta else None

        with torch.inference_mode():
            logits = model(tensor)
            probabilities_tensor = F.softmax(logits, dim=1)[0]
            if flipped_tensor is not None:
                flipped_logits = model(flipped_tensor)
                probabilities_tensor = (probabilities_tensor + F.softmax(flipped_logits, dim=1)[0]) / 2
            probabilities = probabilities_tensor.cpu().numpy()

        predicted_index = int(np.argmax(probabilities))
        predicted_label = labels[predicted_index] if predicted_index < len(labels) else f"class_{predicted_index}"
        confidence = float(probabilities[predicted_index] * 100)
        prediction_route = infer_prediction_route(predicted_label, predicted_index)

        if prediction_route == "healthy":
            normalized_confidence = max(0.0, min(1.0, (confidence / 100 - 0.5) / 0.5))
            score_payload = {
                "skin_score": int(70 + (normalized_confidence * 30)),
                "acne_count": 0,
                "severity_ratio": 0.0,
            }
        elif prediction_route == "acne" and use_advanced_score:
            score_payload = calculate_advanced_skin_score(image_bytes)
        elif prediction_route == "acne":
            normalized_confidence = max(0.0, min(1.0, confidence / 100))
            score_payload = {
                "skin_score": int(80 - (normalized_confidence * 35)),
                "acne_count": 0,
                "severity_ratio": round(normalized_confidence * 10, 2),
            }
        else:
            score_payload = {
                "skin_score": round(confidence),
                "acne_count": 0,
                "severity_ratio": 0.0,
            }

        class_scores = {
            label: round(float(probabilities[index] * 100), 2)
            for index, label in enumerate(labels)
        }

        return {
            "analysis": {
                "pytorch_predicted_class": predicted_label,
                "pytorch_confidence": round(confidence, 2),
                "pytorch_class_scores": class_scores,
                "prediction_route": prediction_route,
                "skin_score": score_payload["skin_score"],
                "acne_count": score_payload["acne_count"],
                "severity_ratio": score_payload["severity_ratio"],
                "skin_pixel_ratio": round(skin_pixel_ratio * 100, 2),
            },
            "advice": [],
        }
    except Exception as exc:
        logger.error("PyTorch inference failed: %s", exc)
        return None
