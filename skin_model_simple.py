"""
Simplified skin analysis model that avoids TensorFlow issues.
Uses a simple CNN architecture instead of MobileNetV2.
"""
import tensorflow as tf
from tensorflow.keras import layers, Model
import numpy as np
from pathlib import Path

MODEL_DIR = Path("model")
MODEL_PATH = MODEL_DIR / "skin_model.h5"

def ensure_model_dir():
    """Create model directory if it doesn't exist"""
    MODEL_DIR.mkdir(exist_ok=True)

def build_simple_model(input_shape=(224, 224, 3)):
    """Build a simple CNN model for skin analysis"""
    model = tf.keras.Sequential([
        layers.Input(shape=input_shape),
        layers.Conv2D(32, 3, activation='relu', padding='same'),
        layers.MaxPooling2D(2),
        layers.Conv2D(64, 3, activation='relu', padding='same'),
        layers.MaxPooling2D(2),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(3, activation='sigmoid')  # 3 outputs: acne, stain, health
    ])
    
    model.compile(
        optimizer='adam',
        loss='mse',
        metrics=['mae']
    )
    
    return model

def build_model(input_shape=(224, 224, 3)):
    """Build model - wrapper for compatibility"""
    return build_simple_model(input_shape)

def predict_skin_analysis(image_path, model=None):
    """Make predictions using the model"""
    if model is None:
        return None
    
    try:
        image = tf.keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
        image_array = tf.keras.preprocessing.image.img_to_array(image)
        image_array = np.expand_dims(image_array, axis=0)
        image_array = image_array / 255.0
        
        prediction = model.predict(image_array, verbose=0)
        return {
            "acne": float(prediction[0][0]),
            "stain": float(prediction[0][1]),
            "health": float(prediction[0][2])
        }
    except Exception as e:
        print(f"Error making prediction: {e}")
        return None

def load_model():
    """Load trained model"""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
    return tf.keras.models.load_model(str(MODEL_PATH))
