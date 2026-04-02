import dlib
import cv2
import numpy as np
import os

# โหลด dlib face detector + shape predictor
_PREDICTOR_PATH = os.path.join(
    os.path.dirname(__file__), "..", "models_ai", "shape_predictor_68_face_landmarks.dat"
)

_detector = dlib.get_frontal_face_detector()
_predictor = None


def _load_predictor():
    global _predictor
    if _predictor is None:
        path = os.path.abspath(_PREDICTOR_PATH)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"shape_predictor_68_face_landmarks.dat not found at {path}. "
                "Download from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
            )
        _predictor = dlib.shape_predictor(path)
    return _predictor


def detect_landmarks(image_path: str) -> dict:
    """ตรวจจับ 68 จุด landmark บนใบหน้าด้วย dlib"""
    img = cv2.imread(image_path)
    if img is None:
        return {"error": "Cannot read image"}

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = img.shape[:2]

    predictor = _load_predictor()
    faces = _detector(gray, 1)

    if len(faces) == 0:
        return {"error": "No face detected"}

    face = faces[0]
    shape = predictor(gray, face)

    # แปลง landmark เป็น list ของ {x, y} (normalized 0-1)
    landmarks = []
    for i in range(68):
        pt = shape.part(i)
        landmarks.append({
            "x": round(pt.x / w, 4),
            "y": round(pt.y / h, 4)
        })

    return {
        "landmarks": landmarks,
        "image_width": w,
        "image_height": h,
        "face_rect": {
            "left": face.left(),
            "top": face.top(),
            "right": face.right(),
            "bottom": face.bottom()
        }
    }
