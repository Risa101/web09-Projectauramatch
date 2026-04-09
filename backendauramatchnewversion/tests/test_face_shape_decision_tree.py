"""Characterization tests for the face shape geometry decision tree.

These tests lock in the Farkas (1994) anthropometry-based thresholds used by
detect_face_shape() when the CNN model is unavailable and MediaPipe geometry
fallback is used.

References:
    Farkas, L. G. (1994). Anthropometry of the Head and Face (2nd ed.).
    Raven Press, New York.

    Farkas, L. G., Hreczko, T. A., Kolar, J. C., & Munro, I. R. (1985).
    Vertical and horizontal proportions of the face in young adult
    North American Caucasians. Plast Reconstr Surg, 75(3), 328-338.

Decision tree (ai_service.py):
  ratio = face_height / cheekbone_width  (landmarks: 152<->10 / 234<->454)
  jaw_ratio = jaw_width / cheekbone_width  (landmarks: 172<->397 / 234<->454)
  temple_ratio = temple_width / cheekbone  (landmarks: 127<->356 / 234<->454)

  Farkas normative data:
    Total facial index mean: 1.28, SD ~0.06
    Mandibular-bizygomatic mean: 0.71, SD ~0.04
    Frontal-bizygomatic mean: 0.87, SD ~0.03

  ratio > 1.45                              -> oblong  (hyperleptoprosopic)
  ratio > 1.30, jaw_ratio < 0.70            -> heart
  ratio > 1.30, temple_ratio < 0.82         -> diamond
  ratio > 1.30, else                        -> oval    (leptoprosopic)
  ratio > 1.15, jaw_ratio > 0.85            -> square
  ratio > 1.15, jaw_ratio < 0.70            -> heart
  ratio > 1.15, temple_ratio < 0.82         -> diamond
  ratio > 1.15, else                        -> oval    (mesoprosopic)
  ratio <= 1.15, jaw_ratio > 0.85           -> square
  ratio <= 1.15, else                       -> round   (euryprosopic)
  no facemesh_data                          -> oval (default)
"""

import pytest
from unittest.mock import patch

# Patch CNN model loader to always return None so geometry fallback is used
with patch("services.ai_service._load_cnn_model", return_value=None):
    from services.ai_service import detect_face_shape


def _make_facemesh_data(ratio, jaw_ratio, temple_ratio, cheekbone_width=200):
    """Build synthetic facemesh_data dict that produces the desired ratios.

    Places landmarks on a 1000x1000 pixel canvas so that:
      face_height = ratio * cheekbone_width
      jaw_width   = jaw_ratio * cheekbone_width
      temple_width = temple_ratio * cheekbone_width

    Landmark indices used by detect_face_shape():
      152 (chin), 10 (forehead), 234 (left_cheek), 454 (right_cheek),
      172 (left_jaw), 397 (right_jaw), 127 (left_temple), 356 (right_temple)
    """
    w, h = 1000, 1000
    face_height = ratio * cheekbone_width
    jaw_width = jaw_ratio * cheekbone_width
    temple_width = temple_ratio * cheekbone_width

    cx, cy = 500, 500  # center of face

    # Build 468 landmarks, all at center by default
    landmarks = [(cx / w, cy / h, 0.0)] * 468

    # Forehead (10): top of face
    landmarks[10] = (cx / w, (cy - face_height / 2) / h, 0.0)
    # Chin (152): bottom of face
    landmarks[152] = (cx / w, (cy + face_height / 2) / h, 0.0)
    # Left cheek (234) / right cheek (454): cheekbone width
    landmarks[234] = ((cx - cheekbone_width / 2) / w, cy / h, 0.0)
    landmarks[454] = ((cx + cheekbone_width / 2) / w, cy / h, 0.0)
    # Left jaw (172) / right jaw (397): jaw width
    landmarks[172] = ((cx - jaw_width / 2) / w, cy / h, 0.0)
    landmarks[397] = ((cx + jaw_width / 2) / w, cy / h, 0.0)
    # Left temple (127) / right temple (356): temple width
    landmarks[127] = ((cx - temple_width / 2) / w, cy / h, 0.0)
    landmarks[356] = ((cx + temple_width / 2) / w, cy / h, 0.0)

    return {
        "landmarks": landmarks,
        "bbox": (300, 200, 700, 800),
        "face_crop": None,  # None forces geometry path (CNN skipped)
        "h": h,
        "w": w,
    }


# Dummy image (not actually used when facemesh_data is provided)
import numpy as np
_DUMMY_IMG = np.zeros((100, 100, 3), dtype=np.uint8)


# ===============================================================================
# Branch 1: ratio > 1.45 -> oblong (hyperleptoprosopic)
# ===============================================================================

class TestOblong:
    """ratio > 1.45 -> oblong regardless of jaw/temple ratios."""

    def test_oblong_typical(self):
        fd = _make_facemesh_data(ratio=1.55, jaw_ratio=0.75, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oblong"

    def test_oblong_wide_jaw(self):
        fd = _make_facemesh_data(ratio=1.8, jaw_ratio=0.90, temple_ratio=0.95)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oblong"

    def test_oblong_narrow_jaw(self):
        fd = _make_facemesh_data(ratio=1.50, jaw_ratio=0.5, temple_ratio=0.7)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oblong"

    def test_oblong_at_boundary(self):
        """ratio = 1.46, just above the 1.45 threshold."""
        fd = _make_facemesh_data(ratio=1.46, jaw_ratio=0.75, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oblong"


# ===============================================================================
# Branch 2: 1.30 < ratio <= 1.45 (leptoprosopic)
# ===============================================================================

class TestHighRatio:
    """1.30 < ratio <= 1.45: heart / diamond / oval."""

    def test_heart_narrow_jaw(self):
        """jaw_ratio < 0.70 -> heart."""
        fd = _make_facemesh_data(ratio=1.4, jaw_ratio=0.65, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "heart"

    def test_heart_very_narrow_jaw(self):
        fd = _make_facemesh_data(ratio=1.35, jaw_ratio=0.5, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "heart"

    def test_heart_boundary_jaw(self):
        """jaw_ratio = 0.69, just below 0.70 threshold."""
        fd = _make_facemesh_data(ratio=1.4, jaw_ratio=0.69, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "heart"

    def test_diamond_narrow_temple(self):
        """jaw_ratio >= 0.70, temple_ratio < 0.82 -> diamond."""
        fd = _make_facemesh_data(ratio=1.4, jaw_ratio=0.75, temple_ratio=0.78)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "diamond"

    def test_diamond_boundary_temple(self):
        """temple_ratio = 0.81, just below 0.82."""
        fd = _make_facemesh_data(ratio=1.35, jaw_ratio=0.72, temple_ratio=0.81)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "diamond"

    def test_oval_balanced(self):
        """jaw_ratio >= 0.70, temple_ratio >= 0.82 -> oval."""
        fd = _make_facemesh_data(ratio=1.4, jaw_ratio=0.75, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oval"

    def test_oval_at_boundary(self):
        """ratio = 1.31, jaw_ratio = 0.70, temple_ratio = 0.82 -> oval."""
        fd = _make_facemesh_data(ratio=1.31, jaw_ratio=0.70, temple_ratio=0.82)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oval"

    def test_heart_takes_priority_over_diamond(self):
        """When both jaw_ratio < 0.70 AND temple_ratio < 0.82, heart wins (checked first)."""
        fd = _make_facemesh_data(ratio=1.4, jaw_ratio=0.55, temple_ratio=0.7)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "heart"


# ===============================================================================
# Branch 3: 1.15 < ratio <= 1.30 (mesoprosopic)
# ===============================================================================

class TestMidRatio:
    """1.15 < ratio <= 1.30: square / heart / diamond / oval."""

    def test_square_wide_jaw(self):
        """jaw_ratio > 0.85 -> square."""
        fd = _make_facemesh_data(ratio=1.25, jaw_ratio=0.90, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "square"

    def test_square_boundary_jaw(self):
        """jaw_ratio = 0.86, just above 0.85."""
        fd = _make_facemesh_data(ratio=1.20, jaw_ratio=0.86, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "square"

    def test_heart_narrow_jaw(self):
        """jaw_ratio < 0.70 -> heart."""
        fd = _make_facemesh_data(ratio=1.25, jaw_ratio=0.65, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "heart"

    def test_diamond_narrow_temple(self):
        """0.70 <= jaw_ratio <= 0.85, temple_ratio < 0.82 -> diamond."""
        fd = _make_facemesh_data(ratio=1.25, jaw_ratio=0.75, temple_ratio=0.78)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "diamond"

    def test_oval_balanced(self):
        """0.70 <= jaw_ratio <= 0.85, temple_ratio >= 0.82 -> oval."""
        fd = _make_facemesh_data(ratio=1.25, jaw_ratio=0.75, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oval"

    def test_square_takes_priority_over_heart(self):
        """jaw_ratio > 0.85 checked before jaw_ratio < 0.70."""
        fd = _make_facemesh_data(ratio=1.20, jaw_ratio=0.90, temple_ratio=0.7)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "square"

    def test_heart_takes_priority_over_diamond(self):
        """jaw_ratio < 0.70 checked before temple_ratio < 0.82."""
        fd = _make_facemesh_data(ratio=1.20, jaw_ratio=0.55, temple_ratio=0.7)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "heart"


# ===============================================================================
# Branch 4: ratio <= 1.15 (euryprosopic)
# ===============================================================================

class TestLowRatio:
    """ratio <= 1.15: square / round."""

    def test_square_wide_jaw(self):
        """jaw_ratio > 0.85 -> square."""
        fd = _make_facemesh_data(ratio=1.10, jaw_ratio=0.90, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "square"

    def test_round_typical(self):
        """jaw_ratio <= 0.85 -> round."""
        fd = _make_facemesh_data(ratio=1.05, jaw_ratio=0.75, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "round"

    def test_round_narrow_jaw(self):
        fd = _make_facemesh_data(ratio=0.95, jaw_ratio=0.6, temple_ratio=0.7)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "round"

    def test_square_at_boundary(self):
        """jaw_ratio = 0.86 at ratio=1.15 -> square."""
        fd = _make_facemesh_data(ratio=1.15, jaw_ratio=0.86, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "square"

    def test_round_at_boundary(self):
        """jaw_ratio = 0.85 (not > 0.85) at ratio=1.15 -> round."""
        fd = _make_facemesh_data(ratio=1.15, jaw_ratio=0.85, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "round"


# ===============================================================================
# Edge cases
# ===============================================================================

class TestEdgeCases:
    """Default fallback and boundary conditions."""

    def test_no_facemesh_data_returns_oval(self):
        """When facemesh_data is None (no face detected), default to oval."""
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=None) == "oval"

    def test_exact_ratio_boundary_1_45(self):
        """ratio = 1.45 is NOT > 1.45, so falls to the 1.30 < ratio branch."""
        fd = _make_facemesh_data(ratio=1.45, jaw_ratio=0.75, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oval"

    def test_exact_ratio_boundary_1_30(self):
        """ratio = 1.30 is NOT > 1.30, so falls to the 1.15 < ratio branch."""
        fd = _make_facemesh_data(ratio=1.30, jaw_ratio=0.75, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oval"

    def test_exact_ratio_boundary_1_15(self):
        """ratio = 1.15 is NOT > 1.15, so falls to the <= 1.15 branch."""
        fd = _make_facemesh_data(ratio=1.15, jaw_ratio=0.75, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "round"

    def test_exact_jaw_boundary_0_70(self):
        """jaw_ratio = 0.70 is NOT < 0.70, so heart is not triggered."""
        fd = _make_facemesh_data(ratio=1.4, jaw_ratio=0.70, temple_ratio=0.78)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "diamond"

    def test_exact_jaw_boundary_0_85(self):
        """jaw_ratio = 0.85 is NOT > 0.85, so square is not triggered in mid-ratio."""
        fd = _make_facemesh_data(ratio=1.25, jaw_ratio=0.85, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oval"

    def test_exact_temple_boundary_0_82(self):
        """temple_ratio = 0.82 is NOT < 0.82, so diamond is not triggered."""
        fd = _make_facemesh_data(ratio=1.4, jaw_ratio=0.75, temple_ratio=0.82)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oval"

    def test_zero_cheekbone_width_defaults(self):
        """When cheekbone_width = 0, ratios default to 1.3/0.8/0.9 -> oval."""
        fd = _make_facemesh_data(ratio=1.3, jaw_ratio=0.8, temple_ratio=0.9)
        # Override to make cheekbones overlap (zero width)
        fd["landmarks"][234] = (0.5, 0.5, 0.0)
        fd["landmarks"][454] = (0.5, 0.5, 0.0)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oval"


# ===============================================================================
# Every shape is reachable
# ===============================================================================

class TestAllShapesReachable:
    """Verify that each of the 7 shapes can be produced by the geometry path."""

    @pytest.mark.parametrize("ratio,jaw_ratio,temple_ratio,expected", [
        (1.55, 0.75, 0.90, "oblong"),
        (1.40, 0.65, 0.90, "heart"),
        (1.40, 0.75, 0.78, "diamond"),
        (1.40, 0.75, 0.90, "oval"),
        (1.25, 0.90, 0.90, "square"),
        (1.05, 0.75, 0.90, "round"),
        # triangle is NOT reachable via the geometry decision tree
        # (it requires the CNN model). This documents that limitation.
    ])
    def test_shape_reachable(self, ratio, jaw_ratio, temple_ratio, expected):
        fd = _make_facemesh_data(ratio=ratio, jaw_ratio=jaw_ratio, temple_ratio=temple_ratio)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == expected

    def test_triangle_not_reachable_via_geometry(self):
        """Triangle shape has no geometry path -- only the CNN can produce it.
        This test documents the gap so it's not silently forgotten."""
        all_shapes = set()
        # Sweep a range of ratio combinations
        for r in [0.8, 0.9, 1.0, 1.1, 1.15, 1.2, 1.3, 1.35, 1.45, 1.5, 1.6]:
            for jr in [0.4, 0.6, 0.69, 0.70, 0.75, 0.85, 0.86, 0.90]:
                for tr in [0.7, 0.81, 0.82, 0.9, 0.95]:
                    fd = _make_facemesh_data(ratio=r, jaw_ratio=jr, temple_ratio=tr)
                    shape = detect_face_shape(_DUMMY_IMG, facemesh_data=fd)
                    all_shapes.add(shape)
        assert "triangle" not in all_shapes, "triangle became reachable -- update tests!"
        assert all_shapes == {"oblong", "heart", "diamond", "oval", "square", "round"}
