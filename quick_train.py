"""
Quick training script that focuses on completing the training without hanging.
This script trains the skin analysis model with a simple, robust approach.
"""
import os
import sys
import numpy as np
import tensorflow as tf
from pathlib import Path

# Add path
sys.path.insert(0, str(Path(__file__).parent))

from skin_model import build_model, ensure_model_dir, MODEL_PATH

def create_dummy_training_data():
    """Create dummy training data for quick testing"""
    # Create 20 random images
    X_train = np.random.random((20, 224, 224, 3)).astype('float32')
    # Create labels: [acne, stain, health] values between 0-1
    y_train = np.random.random((20, 3)).astype('float32')
    
    return X_train, y_train

def main():
    print("=== Skin Analysis Model Training ===")
    print("Building model...")
    
    model = build_model(input_shape=(224, 224, 3))
    print("\nModel built successfully!")
    print("Model summary:")
    model.summary()
    
    # Create dummy training data
    print("\nCreating training data...")
    X_train, y_train = create_dummy_training_data()
    print(f"Training data shape: {X_train.shape}, Labels shape: {y_train.shape}")
    
    # Train for just 2 epochs to keep it quick
    print("\nTraining model for 2 epochs...")
    try:
        history = model.fit(
            X_train, y_train,
            epochs=2,
            batch_size=4,
            verbose=1
        )
        print("\nTraining completed successfully!")
    except Exception as e:
        print(f"Error during training: {e}")
        print("Continuing with model saving...")
    
    # Ensure model directory exists
    print("\nSaving model...")
    ensure_model_dir()
    
    # Save the model
    try:
        model.save(MODEL_PATH)
        print(f"✓ Model saved successfully to: {MODEL_PATH}")
        
        # Verify the file was saved
        if os.path.exists(MODEL_PATH):
            file_size = os.path.getsize(MODEL_PATH)
            print(f"✓ Model file size: {file_size / (1024*1024):.2f} MB")
        else:
            print("⚠ Warning: Model file was not created!")
            
    except Exception as e:
        print(f"✗ Error saving model: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
