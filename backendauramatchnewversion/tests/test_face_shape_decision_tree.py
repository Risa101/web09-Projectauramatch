"""Characterization tests for the face shape geometry decision tree.

These tests lock in the current ratio thresholds used by detect_face_shape()
when the CNN model is unavailable and MediaPipe geometry fallback is used.

Decision tree (ai_service.py lines 145-164):
  ratio = face_height / cheekbone_width
  jaw_ratio = jaw_width / cheekbone_width
  temple_ratio = temple_width / cheekbone_width

  ratio > 1.5                              → oblong
  ratio > 1.3, jaw_ratio < 0.75            → heart
  ratio > 1.3, temple_ratio < 0.85         → diamond
  ratio > 1.3, else                         → oval
  ratio > 1.0, jaw_ratio > 0.9             → square
  ratio > 1.0, jaw_ratio < 0.75            → heart
  ratio > 1.0, temple_ratio < 0.85         → diamond
  ratio > 1.0, else                         → oval
  ratio <= 1.0, jaw_ratio > 0.9            → square
  ratio <= 1.0, else                        → round
  no facemesh_data                          → oval (default)
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


# ═══════════════════════════════════════════════════════════════════════════════
# Branch 1: ratio > 1.5 → oblong
# ═══════════════════════════════════════════════════════════════════════════════

class TestOblong:
    """ratio > 1.5 → oblong regardless of jaw/temple ratios."""

    def test_oblong_typical(self):
        fd = _make_facemesh_data(ratio=1.6, jaw_ratio=0.8, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oblong"

    def test_oblong_wide_jaw(self):
        fd = _make_facemesh_data(ratio=1.8, jaw_ratio=0.95, temple_ratio=0.95)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oblong"

    def test_oblong_narrow_jaw(self):
        fd = _make_facemesh_data(ratio=1.55, jaw_ratio=0.5, temple_ratio=0.7)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oblong"

    def test_oblong_at_boundary(self):
        """ratio = 1.51, just above the 1.5 threshold."""
        fd = _make_facemesh_data(ratio=1.51, jaw_ratio=0.85, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oblong"


# ═══════════════════════════════════════════════════════════════════════════════
# Branch 2: 1.3 < ratio <= 1.5
# ═══════════════════════════════════════════════════════════════════════════════

class TestHighRatio:
    """1.3 < ratio <= 1.5: heart / diamond / oval."""

    def test_heart_narrow_jaw(self):
        """jaw_ratio < 0.75 → heart."""
        fd = _make_facemesh_data(ratio=1.4, jaw_ratio=0.7, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "heart"

    def test_heart_very_narrow_jaw(self):
        fd = _make_facemesh_data(ratio=1.35, jaw_ratio=0.5, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "heart"

    def test_heart_boundary_jaw(self):
        """jaw_ratio = 0.74, just below 0.75 threshold."""
        fd = _make_facemesh_data(ratio=1.4, jaw_ratio=0.74, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "heart"

    def test_diamond_narrow_temple(self):
        """jaw_ratio >= 0.75, temple_ratio < 0.85 → diamond."""
        fd = _make_facemesh_data(ratio=1.4, jaw_ratio=0.8, temple_ratio=0.8)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "diamond"

    def test_diamond_boundary_temple(self):
        """temple_ratio = 0.84, just below 0.85."""
        fd = _make_facemesh_data(ratio=1.35, jaw_ratio=0.76, temple_ratio=0.84)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "diamond"

    def test_oval_balanced(self):
        """jaw_ratio >= 0.75, temple_ratio >= 0.85 → oval."""
        fd = _make_facemesh_data(ratio=1.4, jaw_ratio=0.85, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oval"

    def test_oval_at_boundary(self):
        """ratio = 1.31, jaw_ratio = 0.75, temple_ratio = 0.85 → oval."""
        fd = _make_facemesh_data(ratio=1.31, jaw_ratio=0.75, temple_ratio=0.85)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oval"

    def test_heart_takes_priority_over_diamond(self):
        """When both jaw_ratio < 0.75 AND temple_ratio < 0.85, heart wins (checked first)."""
        fd = _make_facemesh_data(ratio=1.4, jaw_ratio=0.6, temple_ratio=0.7)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "heart"


# ═══════════════════════════════════════════════════════════════════════════════
# Branch 3: 1.0 < ratio <= 1.3
# ═══════════════════════════════════════════════════════════════════════════════

class TestMidRatio:
    """1.0 < ratio <= 1.3: square / heart / diamond / oval."""

    def test_square_wide_jaw(self):
        """jaw_ratio > 0.9 → square."""
        fd = _make_facemesh_data(ratio=1.2, jaw_ratio=0.95, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "square"

    def test_square_boundary_jaw(self):
        """jaw_ratio = 0.91, just above 0.9."""
        fd = _make_facemesh_data(ratio=1.15, jaw_ratio=0.91, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "square"

    def test_heart_narrow_jaw(self):
        """jaw_ratio < 0.75 → heart."""
        fd = _make_facemesh_data(ratio=1.2, jaw_ratio=0.7, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "heart"

    def test_diamond_narrow_temple(self):
        """0.75 <= jaw_ratio <= 0.9, temple_ratio < 0.85 → diamond."""
        fd = _make_facemesh_data(ratio=1.2, jaw_ratio=0.8, temple_ratio=0.8)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "diamond"

    def test_oval_balanced(self):
        """0.75 <= jaw_ratio <= 0.9, temple_ratio >= 0.85 → oval."""
        fd = _make_facemesh_data(ratio=1.2, jaw_ratio=0.85, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oval"

    def test_square_takes_priority_over_heart(self):
        """jaw_ratio > 0.9 checked before jaw_ratio < 0.75."""
        fd = _make_facemesh_data(ratio=1.1, jaw_ratio=0.95, temple_ratio=0.7)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "square"

    def test_heart_takes_priority_over_diamond(self):
        """jaw_ratio < 0.75 checked before temple_ratio < 0.85."""
        fd = _make_facemesh_data(ratio=1.1, jaw_ratio=0.6, temple_ratio=0.7)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "heart"


# ═══════════════════════════════════════════════════════════════════════════════
# Branch 4: ratio <= 1.0
# ═══════════════════════════════════════════════════════════════════════════════

class TestLowRatio:
    """ratio <= 1.0: square / round."""

    def test_square_wide_jaw(self):
        """jaw_ratio > 0.9 → square."""
        fd = _make_facemesh_data(ratio=0.95, jaw_ratio=0.95, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "square"

    def test_round_typical(self):
        """jaw_ratio <= 0.9 → round."""
        fd = _make_facemesh_data(ratio=0.9, jaw_ratio=0.8, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "round"

    def test_round_narrow_jaw(self):
        fd = _make_facemesh_data(ratio=0.85, jaw_ratio=0.6, temple_ratio=0.7)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "round"

    def test_square_at_boundary(self):
        """jaw_ratio = 0.91 at ratio=1.0 → square."""
        fd = _make_facemesh_data(ratio=1.0, jaw_ratio=0.91, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "square"

    def test_round_at_boundary(self):
        """jaw_ratio = 0.9 (not > 0.9) at ratio=1.0 → round."""
        fd = _make_facemesh_data(ratio=1.0, jaw_ratio=0.9, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "round"


# ═══════════════════════════════════════════════════════════════════════════════
# Edge cases
# ═══════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Default fallback and boundary conditions."""

    def test_no_facemesh_data_returns_oval(self):
        """When facemesh_data is None (no face detected), default to oval."""
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=None) == "oval"

    def test_exact_ratio_boundary_1_5(self):
        """ratio = 1.5 is NOT > 1.5, so falls to the 1.3 < ratio branch."""
        fd = _make_facemesh_data(ratio=1.5, jaw_ratio=0.85, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oval"

    def test_exact_ratio_boundary_1_3(self):
        """ratio = 1.3 is NOT > 1.3, so falls to the 1.0 < ratio branch."""
        fd = _make_facemesh_data(ratio=1.3, jaw_ratio=0.85, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oval"

    def test_exact_ratio_boundary_1_0(self):
        """ratio = 1.0 is NOT > 1.0, so falls to the <= 1.0 branch."""
        fd = _make_facemesh_data(ratio=1.0, jaw_ratio=0.85, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "round"

    def test_exact_jaw_boundary_0_75(self):
        """jaw_ratio = 0.75 is NOT < 0.75, so heart is not triggered."""
        fd = _make_facemesh_data(ratio=1.4, jaw_ratio=0.75, temple_ratio=0.8)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "diamond"

    def test_exact_jaw_boundary_0_9(self):
        """jaw_ratio = 0.9 is NOT > 0.9, so square is not triggered in mid-ratio."""
        fd = _make_facemesh_data(ratio=1.2, jaw_ratio=0.9, temple_ratio=0.9)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oval"

    def test_exact_temple_boundary_0_85(self):
        """temple_ratio = 0.85 is NOT < 0.85, so diamond is not triggered."""
        fd = _make_facemesh_data(ratio=1.4, jaw_ratio=0.8, temple_ratio=0.85)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oval"

    def test_zero_cheekbone_width_defaults(self):
        """When cheekbone_width = 0, ratios default to 1.3/0.8/0.9 → oval."""
        fd = _make_facemesh_data(ratio=1.3, jaw_ratio=0.8, temple_ratio=0.9)
        # Override to make cheekbones overlap (zero width)
        fd["landmarks"][234] = (0.5, 0.5, 0.0)
        fd["landmarks"][454] = (0.5, 0.5, 0.0)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == "oval"


# ═══════════════════════════════════════════════════════════════════════════════
# Every shape is reachable
# ═══════════════════════════════════════════════════════════════════════════════

class TestAllShapesReachable:
    """Verify that each of the 7 shapes can be produced by the geometry path."""

    @pytest.mark.parametrize("ratio,jaw_ratio,temple_ratio,expected", [
        (1.6,  0.80, 0.90, "oblong"),
        (1.4,  0.70, 0.90, "heart"),
        (1.4,  0.80, 0.80, "diamond"),
        (1.4,  0.85, 0.90, "oval"),
        (1.2,  0.95, 0.90, "square"),
        (0.9,  0.80, 0.90, "round"),
        # triangle is NOT reachable via the geometry decision tree
        # (it requires the CNN model). This documents that limitation.
    ])
    def test_shape_reachable(self, ratio, jaw_ratio, temple_ratio, expected):
        fd = _make_facemesh_data(ratio=ratio, jaw_ratio=jaw_ratio, temple_ratio=temple_ratio)
        assert detect_face_shape(_DUMMY_IMG, facemesh_data=fd) == expected

    def test_triangle_not_reachable_via_geometry(self):
        """Triangle shape has no geometry path — only the CNN can produce it.
        This test documents the gap so it's not silently forgotten."""
        all_shapes = set()
        # Sweep a range of ratio combinations
        for r in [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8]:
            for jr in [0.4, 0.6, 0.74, 0.75, 0.8, 0.9, 0.91, 0.95]:
                for tr in [0.7, 0.84, 0.85, 0.9, 0.95]:
                    fd = _make_facemesh_data(ratio=r, jaw_ratio=jr, temple_ratio=tr)
                    shape = detect_face_shape(_DUMMY_IMG, facemesh_data=fd)
                    all_shapes.add(shape)
        assert "triangle" not in all_shapes, "triangle became reachable — update tests!"
        assert all_shapes == {"oblong", "heart", "diamond", "oval", "square", "round"}
