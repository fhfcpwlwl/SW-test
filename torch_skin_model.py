"""PyTorch model loading and inference helpers."""
from pathlib import Path
from typing import Optional

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


def predict_pytorch_skin_model(image_path: str, bundle: Optional[dict] = None) -> Optional[dict]:
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
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            tensor = preprocess(image).unsqueeze(0)

        with torch.inference_mode():
            logits = model(tensor)
            probabilities = F.softmax(logits, dim=1)[0].cpu().numpy()

        predicted_index = int(np.argmax(probabilities))
        predicted_label = labels[predicted_index] if predicted_index < len(labels) else f"class_{predicted_index}"
        confidence = float(probabilities[predicted_index] * 100)

        class_scores = {
            label: round(float(probabilities[index] * 100), 2)
            for index, label in enumerate(labels)
        }

        return {
            "analysis": {
                "pytorch_predicted_class": predicted_label,
                "pytorch_confidence": round(confidence, 2),
                "pytorch_class_scores": class_scores,
            },
            "advice": [],
        }
    except Exception as exc:
        logger.error("PyTorch inference failed: %s", exc)
        return None
