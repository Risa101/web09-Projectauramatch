"""
Train CNN Model สำหรับจำแนกโครงหน้า 7 แบบ
diamond | heart | oblong | oval | round | square | triangle

วิธีรัน:
  cd backendauramatchnewversion
  pip install tensorflow opencv-python matplotlib
  python scripts/train_face_shape.py

Dataset:
  ดาวน์โหลดจาก Kaggle: face-shape-classification
  วางไว้ที่: scripts/dataset/face shape detector/
"""

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models
import os

DATASET_PATH = os.path.join(os.path.dirname(__file__), "dataset", "face shape detector")
MODEL_OUTPUT = os.path.join(os.path.dirname(__file__), "..", "models_ai", "face_shape_cnn.h5")
IMG_SIZE = (200, 200)
BATCH_SIZE = 32
EPOCHS = 15

CLASSES = ['diamond', 'heart', 'oblong', 'oval', 'round', 'square', 'triangle']

os.makedirs(os.path.dirname(MODEL_OUTPUT), exist_ok=True)

# ── Data Augmentation ──────────────────────────────
datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=10,
    zoom_range=0.1,
    horizontal_flip=True,
)

train_data = datagen.flow_from_directory(
    DATASET_PATH,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='sparse',
    subset='training'
)

val_data = datagen.flow_from_directory(
    DATASET_PATH,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='sparse',
    subset='validation'
)

print(f"Classes: {train_data.class_indices}")

# ── CNN Model ─────────────────────────────────────
cnn = tf.keras.Sequential([
    layers.Conv2D(64, (3,3), padding='same', strides=2, activation='relu', input_shape=(200,200,3)),
    layers.MaxPool2D(2, 2),

    layers.Conv2D(32, (3,3), padding='same', strides=2, activation='relu'),
    layers.MaxPool2D(2, 2),

    layers.Conv2D(32, (3,3), padding='same', strides=2, activation='relu'),
    layers.MaxPool2D(2, 2),

    layers.Flatten(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(7, activation='softmax')
])

cnn.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

cnn.summary()

# ── Train ─────────────────────────────────────────
history = cnn.fit(
    train_data,
    validation_data=val_data,
    epochs=EPOCHS,
)

# ── Save ──────────────────────────────────────────
cnn.save(MODEL_OUTPUT)
print(f"\n✅ Model saved to: {MODEL_OUTPUT}")
print(f"   Final accuracy    : {history.history['accuracy'][-1]:.2%}")
print(f"   Final val_accuracy: {history.history['val_accuracy'][-1]:.2%}")
