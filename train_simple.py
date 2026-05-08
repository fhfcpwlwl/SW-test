"""
Fast training script using simplified model
"""
import os
import sys
from pathlib import Path
import numpy as np
import tensorflow as tf

# Import the simple model
from skin_model_simple import build_model, ensure_model_dir, MODEL_PATH

def main():
    print("=== Skin Analysis Model Training (Simple) ===")
    print("Building simplified model...")
    
    model = build_model(input_shape=(224, 224, 3))
    print("Model architecture:")
    model.summary()
    
    # Create small dummy training data
    print("\nCreating training data...")
    X_train = np.random.random((10, 224, 224, 3)).astype('float32')
    y_train = np.random.random((10, 3)).astype('float32')
    print(f"Training data: {X_train.shape}, Labels: {y_train.shape}")
    
    # Train for 2 epochs quickly
    print("\nTraining model...")
    try:
        history = model.fit(
            X_train, y_train,
            epochs=2,
            batch_size=2,
            verbose=1
        )
        print("✓ Training completed!")
    except Exception as e:
        print(f"⚠ Training error: {e}")
    
    # Save model
    print("Saving model...")
    ensure_model_dir()
    model.save(str(MODEL_PATH))
    
    if os.path.exists(MODEL_PATH):
        size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
        print(f"✓ Model saved: {MODEL_PATH} ({size_mb:.2f} MB)")
    else:
        print("✗ Model file not created!")
        sys.exit(1)

if __name__ == "__main__":
    main()
