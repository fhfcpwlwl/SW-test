"""Machine Learning Model for Skin Analysis

Provides model building, training, and prediction capabilities
using TensorFlow/Keras with transfer learning on MobileNetV2.
"""
import os
from typing import Optional, Dict
import numpy as np
from PIL import Image

try:
    import tensorflow as tf
    from tensorflow.keras import layers, models
    TENSORFLOW_AVAILABLE = True
except ImportError:
    tf = None
    layers = None
    models = None
    TENSORFLOW_AVAILABLE = False

try:
    from config import MODEL_PATH, MODEL_INPUT_SHAPE
    from logger import setup_logger
except ImportError:
    MODEL_PATH = os.path.join("model", "skin_model.h5")
    MODEL_INPUT_SHAPE = (224, 224, 3)
    import logging
    setup_logger = lambda x: logging.getLogger(x)

logger = setup_logger(__name__)

MODEL_DIR = "model"



def build_model(input_shape: tuple = MODEL_INPUT_SHAPE) -> 'tf.keras.Model':
    """Build transfer learning model with MobileNetV2.
    
    Args:
        input_shape: Input image shape (height, width, channels)
        
    Returns:
        Compiled Keras model
    """
    if not TENSORFLOW_AVAILABLE:
        raise RuntimeError("TensorFlow is not installed. Install tensorflow to build the model.")

    try:
        # Load pre-trained MobileNetV2 without top layers
        base_model = tf.keras.applications.MobileNetV2(
            input_shape=input_shape,
            include_top=False,
            weights="imagenet",
        )
        base_model.trainable = False
        
        # Add custom layers
        inputs = layers.Input(shape=input_shape)
        x = tf.keras.applications.mobilenet_v2.preprocess_input(inputs)
        x = base_model(x, training=False)
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(128, activation="relu")(x)
        outputs = layers.Dense(3, activation="sigmoid")(x)
        
        model = models.Model(inputs, outputs, name="SkinAnalysisModel")
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
            loss="mse",
            metrics=[tf.keras.metrics.MeanAbsoluteError()],
        )
        
        logger.info(f"Model built: input_shape={input_shape}")
        return model
    except Exception as e:
        logger.error(f"Error building model: {e}")
        raise


def ensure_model_dir():
    os.makedirs(MODEL_DIR, exist_ok=True)


def load_model(path: str = str(MODEL_PATH)) -> 'tf.keras.Model':
    """Load trained model from disk.
    
    Args:
        path: Path to model file
        
    Returns:
        Loaded Keras model
        
    Raises:
        FileNotFoundError: If model file doesn't exist
        RuntimeError: If TensorFlow is not installed
    """
    if not TENSORFLOW_AVAILABLE:
        raise RuntimeError("TensorFlow is not installed. Install tensorflow to load the model.")

    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found: {path}")
    
    try:
        # Inference does not require training-time optimizer/metric state.
        model = tf.keras.models.load_model(path, compile=False)
        logger.info(f"Model loaded: {path}")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise


def preprocess_image(image_path: str, target_size: tuple = MODEL_INPUT_SHAPE[:2]) -> np.ndarray:
    """Preprocess image for model input
    
    Args:
        image_path: Path to image file
        target_size: Target image dimensions
        
    Returns:
        Preprocessed image array
    """
    try:
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            image = image.resize(target_size)
            arr = np.array(image, dtype="float32")
            arr = arr / 255.0  # Normalize
            return np.expand_dims(arr, axis=0)  # Add batch dimension
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        raise


def predict_skin_analysis(image_path: str, model: Optional['tf.keras.Model'] = None) -> Optional[Dict]:
    """Make skin analysis prediction.
    
    Args:
        image_path: Path to image file
        model: Keras model (loads if None)
        
    Returns:
        Dictionary with predictions or None
    """
    if not TENSORFLOW_AVAILABLE:
        logger.warning("TensorFlow is not installed. Skipping model prediction.")
        return None

    if model is None:
        try:
            model = load_model()
        except (FileNotFoundError, RuntimeError):
            logger.warning("Model not available")
            return None
    
    try:
        image_array = preprocess_image(image_path)
        preds = model.predict(image_array, verbose=0)[0] * 100
        
        acne_score = int(np.clip(preds[0], 0, 100))
        stain_score = int(np.clip(preds[1], 0, 100))
        health_score = int(np.clip(preds[2], 0, 100))
        
        advice = []
        if acne_score > 50:
            advice.append("모공 관리와 저자극 클렌징을 추천합니다.")
        if stain_score > 40:
            advice.append("미백 제품과 자외선 차단제를 꾸준히 사용하세요.")
        if health_score < 50:
            advice.append("수분 공급과 휴식이 필요합니다.")
        
        return {
            "analysis": {
                "model_acne": acne_score,
                "model_stain": stain_score,
                "model_health": health_score,
            },
            "advice": advice,
        }
    except Exception as e:
        logger.error(f"Error in prediction: {e}")
        return None
