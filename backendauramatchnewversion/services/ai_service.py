import cv2
import numpy as np
import mediapipe as mp
import os

mp_face_mesh = mp.solutions.face_mesh

# ── Load CNN model (optional — falls back to MediaPipe if not found) ──────────
_CNN_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models_ai", "face_shape_cnn.h5")
_CNN_CLASSES = ['diamond', 'heart', 'oblong', 'oval', 'round', 'square', 'triangle']
_cnn_model = None

def _load_cnn_model():
    global _cnn_model
    if _cnn_model is not None:
        return _cnn_model
    model_path = os.path.abspath(_CNN_MODEL_PATH)
    if os.path.exists(model_path):
        try:
            import tensorflow as tf
            _cnn_model = tf.keras.models.load_model(model_path)
        except Exception:
            _cnn_model = None
    return _cnn_model


def analyze_face(image_path: str, gender: str = "female", db_session=None) -> dict:
    image = cv2.imread(image_path)
    if image is None:
        return {}

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    face_shape = detect_face_shape(rgb)

    from services.color_analysis_service import (
        extract_skin_lab, classify_tone_from_lab, classify_undertone_from_lab,
    )
    skin_lab = extract_skin_lab(rgb)
    skin_tone = classify_tone_from_lab(skin_lab[0])
    skin_undertone = classify_undertone_from_lab(skin_lab[1], skin_lab[2])

    personal_color, palette_id, confidence = get_personal_color(
        skin_tone, skin_undertone, skin_lab=skin_lab, db_session=db_session
    )

    return {
        "face_shape": face_shape,
        "skin_tone": skin_tone,
        "skin_undertone": skin_undertone,
        "personal_color": personal_color,
        "palette_id": palette_id,
        "ethnicity": "other",
        "confidence_score": confidence,
    }


def _crop_face_mediapipe(rgb_image):
    """Crop face region using MediaPipe bounding box. Returns cropped BGR or None."""
    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1) as face_mesh:
        results = face_mesh.process(rgb_image)
        if not results.multi_face_landmarks:
            return None
        h, w = rgb_image.shape[:2]
        lm = results.multi_face_landmarks[0].landmark
        xs = [p.x * w for p in lm]
        ys = [p.y * h for p in lm]
        x1, x2 = max(0, int(min(xs)) - 20), min(w, int(max(xs)) + 20)
        y1, y2 = max(0, int(min(ys)) - 20), min(h, int(max(ys)) + 20)
        face = rgb_image[y1:y2, x1:x2]
        return face if face.size > 0 else None


def detect_face_shape(rgb_image) -> str:
    model = _load_cnn_model()
    if model is not None:
        face_crop = _crop_face_mediapipe(rgb_image)
        if face_crop is not None:
            img = cv2.resize(face_crop, (200, 200)).astype("float32") / 255.0
            pred = model.predict(np.expand_dims(img, axis=0), verbose=0)
            return _CNN_CLASSES[int(np.argmax(pred))]

    # ── Fallback: MediaPipe geometry ──────────────────────────────────────────
    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1) as face_mesh:
        results = face_mesh.process(rgb_image)
        if not results.multi_face_landmarks:
            return "oval"

        landmarks = results.multi_face_landmarks[0].landmark
        h, w = rgb_image.shape[:2]

        chin = landmarks[152]
        forehead = landmarks[10]
        left_cheek = landmarks[234]
        right_cheek = landmarks[454]
        left_jaw = landmarks[172]
        right_jaw = landmarks[397]

        face_width = abs(right_cheek.x - left_cheek.x) * w
        face_height = abs(chin.y - forehead.y) * h
        jaw_width = abs(right_jaw.x - left_jaw.x) * w

        ratio = face_height / face_width if face_width > 0 else 1.3

        if ratio > 1.5:
            return "oblong"
        elif ratio > 1.3:
            return "oval"
        elif ratio > 1.1:
            if jaw_width / face_width > 0.85:
                return "square"
            return "heart"
        elif ratio > 0.9:
            return "round"
        else:
            return "square"


def detect_skin_tone(rgb_image) -> tuple:
    """Detect skin tone and undertone using CIELAB color space.

    Returns (tone: str, undertone: str) — same contract as before.
    """
    from services.color_analysis_service import (
        extract_skin_lab, classify_tone_from_lab, classify_undertone_from_lab,
    )
    L, a, b = extract_skin_lab(rgb_image)
    tone = classify_tone_from_lab(L)
    undertone = classify_undertone_from_lab(a, b)
    return tone, undertone


def get_personal_color(skin_tone: str, undertone: str,
                       skin_lab: tuple = None, db_session=None) -> tuple:
    """Determine personal color season.

    If skin_lab and db_session are provided, uses CIEDE2000 matching against
    the color_palettes table. Otherwise falls back to the legacy lookup dict.

    Returns (season: str, palette_id: int|None, confidence: float).
    """
    if skin_lab is not None and db_session is not None:
        from services.color_analysis_service import (
            match_season_by_delta_e, load_palette_references,
        )
        refs = load_palette_references(db_session)
        if refs:
            return match_season_by_delta_e(skin_lab, refs)

    # Legacy fallback
    mapping = {
        ("fair", "cool"): "summer",
        ("fair", "warm"): "spring",
        ("fair", "neutral"): "summer",
        ("light", "cool"): "summer",
        ("light", "warm"): "spring",
        ("light", "neutral"): "spring",
        ("medium", "warm"): "autumn",
        ("medium", "cool"): "summer",
        ("medium", "neutral"): "autumn",
        ("tan", "warm"): "autumn",
        ("tan", "cool"): "winter",
        ("tan", "neutral"): "autumn",
        ("dark", "warm"): "autumn",
        ("dark", "cool"): "winter",
        ("dark", "neutral"): "winter",
        ("deep", "warm"): "autumn",
        ("deep", "cool"): "winter",
        ("deep", "neutral"): "winter",
    }
    return mapping.get((skin_tone, undertone), "spring"), None, 85.0
