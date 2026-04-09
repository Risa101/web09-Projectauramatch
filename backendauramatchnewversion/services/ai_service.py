import cv2
import numpy as np
import mediapipe as mp
import os

mp_face_mesh = mp.solutions.face_mesh

# ── Load CNN model (optional — falls back to MediaPipe if not found) ──────────
_CNN_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models_ai", "face_shape_cnn.h5")
_CNN_CLASSES = ['diamond', 'heart', 'oblong', 'oval', 'round', 'square', 'triangle']
_cnn_model = None

FACE_SHAPE_TIPS = {
    "oval": {"description": "Balanced proportions", "contouring": "Light contour on cheekbones", "styles": ["Most styles work well"]},
    "round": {"description": "Equal width and height", "contouring": "Contour along jawline and temples", "styles": ["Angular frames", "Side-swept bangs"]},
    "square": {"description": "Strong jawline, equal proportions", "contouring": "Soften jaw corners", "styles": ["Textured layers", "Side parts"]},
    "heart": {"description": "Wider forehead, narrow chin", "contouring": "Contour forehead sides", "styles": ["Side-swept bangs", "Chin-length layers"]},
    "oblong": {"description": "Longer than wide", "contouring": "Add width at cheekbones", "styles": ["Side-swept bangs", "Layered cuts"]},
    "diamond": {"description": "Narrow forehead and jaw, wide cheekbones", "contouring": "Soften cheekbone prominence", "styles": ["Side-swept bangs", "Chin-length styles"]},
    "triangle": {"description": "Wider jaw, narrow forehead", "contouring": "Add width at temples", "styles": ["Volume at crown", "Side-swept bangs"]},
}


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


# ── Single MediaPipe pass ────────────────────────────────────────────────────

def _run_facemesh(rgb_image):
    """Run MediaPipe FaceMesh once. Returns dict with landmarks/bbox/crop or None."""
    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1) as fm:
        results = fm.process(rgb_image)
        if not results.multi_face_landmarks:
            return None
        h, w = rgb_image.shape[:2]
        lm = results.multi_face_landmarks[0].landmark
        landmarks = [(p.x, p.y, p.z) for p in lm]
        xs = [p[0] * w for p in landmarks]
        ys = [p[1] * h for p in landmarks]
        x1, x2 = max(0, int(min(xs)) - 20), min(w, int(max(xs)) + 20)
        y1, y2 = max(0, int(min(ys)) - 20), min(h, int(max(ys)) + 20)
        face_crop = rgb_image[y1:y2, x1:x2]
        return {
            "landmarks": landmarks,
            "bbox": (x1, y1, x2, y2),
            "face_crop": face_crop if face_crop.size > 0 else None,
            "h": h, "w": w,
        }


# ── Orchestrator ─────────────────────────────────────────────────────────────

def analyze_face(image_path: str, gender: str = "female", db_session=None) -> dict:
    image = cv2.imread(image_path)
    if image is None:
        return {}

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Single MediaPipe pass — reused for face shape + skin extraction
    facemesh_data = _run_facemesh(rgb)

    face_shape = detect_face_shape(rgb, facemesh_data=facemesh_data)

    from services.color_analysis_service import (
        extract_skin_lab, extract_skin_lab_from_bbox,
        classify_tone_from_lab, classify_undertone_from_lab,
    )

    if facemesh_data and facemesh_data["face_crop"] is not None:
        skin_lab = extract_skin_lab_from_bbox(rgb, facemesh_data["bbox"])
    else:
        skin_lab = extract_skin_lab(rgb)

    skin_tone = classify_tone_from_lab(skin_lab[0], skin_lab[2])
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


# ── Face shape detection ─────────────────────────────────────────────────────

def detect_face_shape(rgb_image, facemesh_data=None) -> str:
    if facemesh_data is None:
        facemesh_data = _run_facemesh(rgb_image)

    model = _load_cnn_model()
    if model is not None and facemesh_data and facemesh_data["face_crop"] is not None:
        face_crop = facemesh_data["face_crop"]
        img = cv2.resize(face_crop, (200, 200)).astype("float32") / 255.0
        pred = model.predict(np.expand_dims(img, axis=0), verbose=0)
        return _CNN_CLASSES[int(np.argmax(pred))]

    # ── Fallback: MediaPipe geometry ──────────────────────────────────────────
    if not facemesh_data:
        return "oval"

    landmarks = facemesh_data["landmarks"]
    h, w = facemesh_data["h"], facemesh_data["w"]

    def _px(idx):
        return landmarks[idx][0] * w, landmarks[idx][1] * h

    chin = _px(152)
    forehead = _px(10)
    left_cheek = _px(234)
    right_cheek = _px(454)
    left_jaw = _px(172)
    right_jaw = _px(397)
    left_temple = _px(127)
    right_temple = _px(356)

    cheekbone_width = abs(right_cheek[0] - left_cheek[0])
    face_height = abs(chin[1] - forehead[1])
    jaw_width = abs(right_jaw[0] - left_jaw[0])
    temple_width = abs(right_temple[0] - left_temple[0])

    ratio = face_height / cheekbone_width if cheekbone_width > 0 else 1.3
    jaw_ratio = jaw_width / cheekbone_width if cheekbone_width > 0 else 0.8
    temple_ratio = temple_width / cheekbone_width if cheekbone_width > 0 else 0.9

    # Thresholds derived from Farkas (1994) facial anthropometry:
    #   Farkas, L. G. (1994). Anthropometry of the Head and Face (2nd ed.).
    #   Raven Press, New York.
    #
    #   Farkas, L. G., Hreczko, T. A., Kolar, J. C., & Munro, I. R. (1985).
    #   Vertical and horizontal proportions of the face in young adult
    #   North American Caucasians. Plast Reconstr Surg, 75(3), 328-338.
    #
    # Normative data (Farkas 1994, Table 6.5):
    #   Total facial index (tr-gn/zy-zy): mean 1.28, SD ~0.06
    #   Mandibular-bizygomatic (go-go/zy-zy): mean 0.71, SD ~0.04
    #   Frontal-bizygomatic (ft-ft/zy-zy): mean 0.87, SD ~0.03
    #
    # MediaPipe landmarks 10/152 approximate trichion-gnathion; 234/454
    # approximate bizygomatic; 172/397 approximate bigonial; 127/356
    # approximate frontal width.

    if ratio > 1.45:
        return "oblong"
    elif ratio > 1.30:
        if jaw_ratio < 0.70:
            return "heart"
        if temple_ratio < 0.82:
            return "diamond"
        return "oval"
    elif ratio > 1.15:
        if jaw_ratio > 0.85:
            return "square"
        if jaw_ratio < 0.70:
            return "heart"
        if temple_ratio < 0.82:
            return "diamond"
        return "oval"
    else:
        if jaw_ratio > 0.85:
            return "square"
        return "round"


def detect_skin_tone(rgb_image) -> tuple:
    """Detect skin tone and undertone using CIELAB color space.

    Returns (tone: str, undertone: str) — same contract as before.
    """
    from services.color_analysis_service import (
        extract_skin_lab, classify_tone_from_lab, classify_undertone_from_lab,
    )
    L, a, b = extract_skin_lab(rgb_image)
    tone = classify_tone_from_lab(L, b)
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
