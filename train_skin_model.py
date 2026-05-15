import csv
import os
from pathlib import Path

import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split

from skin_model import build_model, ensure_model_dir, MODEL_PATH

DATA_DIR = Path("data")
IMAGE_DIR = DATA_DIR / "images"
LABELS_CSV = DATA_DIR / "labels.csv"
BATCH_SIZE = 16
TARGET_SIZE = (224, 224)
EPOCHS = 20


def load_labels(label_path: Path):
    images = []
    labels = []
    with open(label_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            filename = row.get("filename")
            if not filename:
                continue
            acne = float(row.get("acne", 0)) / 100.0
            stain = float(row.get("stain", 0)) / 100.0
            health = float(row.get("health", 0)) / 100.0
            path = IMAGE_DIR / filename
            if path.exists():
                images.append(str(path))
                labels.append([acne, stain, health])
            else:
                print(f"경고: 이미지가 존재하지 않음 {path}")
    return images, np.array(labels, dtype="float32")


def load_image(path: str):
    image = tf.keras.preprocessing.image.load_img(path, target_size=TARGET_SIZE)
    arr = tf.keras.preprocessing.image.img_to_array(image)
    arr = arr / 255.0
    return arr


def create_dataset(image_paths, labels):
    images = []
    for path in image_paths:
        images.append(load_image(path))
    return np.array(images), labels


def main():
    if not LABELS_CSV.exists():
        raise FileNotFoundError(f"레이블 CSV 파일이 필요합니다: {LABELS_CSV}")
    images, labels = load_labels(LABELS_CSV)
    if len(images) == 0:
        raise ValueError("학습할 이미지가 없습니다. data/images 폴더에 이미지를 넣고 labels.csv를 준비하세요.")

    print(f"학습 데이터: {len(images)}개 이미지")

    # 간단한 방식으로 데이터 로드
    X, y = create_dataset(images, labels)

    model = build_model(input_shape=(*TARGET_SIZE, 3))
    model.summary()

    history = model.fit(
        X, y,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=0.2 if len(images) >= 5 else 0.0
    )

    ensure_model_dir()
    model.save(MODEL_PATH)
    print(f"학습 완료: 모델이 저장되었습니다. {MODEL_PATH}")


if __name__ == "__main__":
    main()
