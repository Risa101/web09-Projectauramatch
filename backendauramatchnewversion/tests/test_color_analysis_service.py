"""Characterization tests for color_analysis_service.

Tests verify the CIELAB-based color analysis pipeline including:
  - ITA-based skin tone classification (Chardon et al. 1991)
  - Hue-angle-based undertone classification (Xiao et al. 2017)
  - CIEDE2000 season matching

Run: python3 -m pytest tests/test_color_analysis_service.py -v
"""

import math
import numpy as np
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.color_analysis_service import (
    rgb_to_lab,
    extract_skin_lab,
    classify_tone_from_lab,
    classify_undertone_from_lab,
    match_season_by_delta_e,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

PALETTE_REFS = [
    {"palette_id": 1, "season": "spring", "sub_type": "light", "centroid_lab": (75.0, 14.0, 22.0)},
    {"palette_id": 2, "season": "spring", "sub_type": "true", "centroid_lab": (68.0, 16.0, 28.0)},
    {"palette_id": 3, "season": "spring", "sub_type": "bright", "centroid_lab": (62.0, 18.0, 32.0)},
    {"palette_id": 4, "season": "summer", "sub_type": "light", "centroid_lab": (78.0, 10.0, 12.0)},
    {"palette_id": 5, "season": "summer", "sub_type": "true", "centroid_lab": (72.0, 8.0, 10.0)},
    {"palette_id": 6, "season": "summer", "sub_type": "soft", "centroid_lab": (65.0, 9.0, 14.0)},
    {"palette_id": 7, "season": "autumn", "sub_type": "soft", "centroid_lab": (70.0, 14.0, 26.0)},
    {"palette_id": 8, "season": "autumn", "sub_type": "true", "centroid_lab": (60.0, 16.0, 30.0)},
    {"palette_id": 9, "season": "autumn", "sub_type": "deep", "centroid_lab": (50.0, 18.0, 28.0)},
    {"palette_id": 10, "season": "winter", "sub_type": "bright", "centroid_lab": (73.0, 6.0, 8.0)},
    {"palette_id": 11, "season": "winter", "sub_type": "true", "centroid_lab": (55.0, 8.0, 10.0)},
    {"palette_id": 12, "season": "winter", "sub_type": "deep", "centroid_lab": (40.0, 10.0, 14.0)},
]


def _make_uniform_image(r, g, b, height=100, width=100):
    """Create a uniform-color RGB image (H x W x 3, uint8)."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:, :] = [r, g, b]
    return img


def _ita(L, b):
    """Compute ITA for reference in test comments."""
    if abs(b) < 0.01:
        b = 0.01
    return math.atan2(L - 50, b) * (180.0 / math.pi)


def _hab(a, b):
    """Compute hue angle for reference in test comments."""
    h = math.atan2(b, a) * (180.0 / math.pi)
    return h + 360 if h < 0 else h


# ── rgb_to_lab ────────────────────────────────────────────────────────────────


class TestRgbToLab:
    def test_black(self):
        lab = rgb_to_lab(np.array([[0, 0, 0]]))
        assert lab.shape == (1, 3)
        assert pytest.approx(lab[0, 0], abs=0.5) == 0.0  # L* ≈ 0

    def test_white(self):
        lab = rgb_to_lab(np.array([[255, 255, 255]]))
        assert pytest.approx(lab[0, 0], abs=0.5) == 100.0  # L* ≈ 100

    def test_neutral_gray(self):
        lab = rgb_to_lab(np.array([[128, 128, 128]]))
        L, a, b = lab[0]
        assert 50 < L < 55  # mid-lightness
        assert abs(a) < 1.0  # near-zero chroma
        assert abs(b) < 1.0

    def test_pure_red_has_positive_a(self):
        lab = rgb_to_lab(np.array([[255, 0, 0]]))
        assert lab[0, 1] > 50  # a* strongly positive (red)

    def test_pure_blue_has_negative_b(self):
        lab = rgb_to_lab(np.array([[0, 0, 255]]))
        assert lab[0, 2] < -50  # b* strongly negative (blue)

    def test_batch_shape(self):
        pixels = np.array([[255, 0, 0], [0, 255, 0], [0, 0, 255]])
        lab = rgb_to_lab(pixels)
        assert lab.shape == (3, 3)

    def test_output_dtype_is_float(self):
        lab = rgb_to_lab(np.array([[100, 150, 200]], dtype=np.uint8))
        assert lab.dtype == np.float64

    def test_typical_skin_tone_range(self):
        """A warm medium skin tone should land in expected L*a*b* ranges."""
        lab = rgb_to_lab(np.array([[198, 160, 120]]))
        L, a, b = lab[0]
        assert 60 < L < 75
        assert 5 < a < 20
        assert 20 < b < 40


# ── extract_skin_lab ──────────────────────────────────────────────────────────


class TestExtractSkinLab:
    def test_uniform_image_returns_that_color(self):
        img = _make_uniform_image(200, 160, 130)
        L, a, b = extract_skin_lab(img)
        # Should match the single color's Lab conversion
        expected = rgb_to_lab(np.array([[200, 160, 130]]))[0]
        assert pytest.approx(L, abs=1.0) == expected[0]
        assert pytest.approx(a, abs=1.0) == expected[1]
        assert pytest.approx(b, abs=1.0) == expected[2]

    def test_returns_three_floats(self):
        img = _make_uniform_image(180, 140, 110)
        result = extract_skin_lab(img)
        assert len(result) == 3
        assert all(isinstance(v, float) for v in result)

    def test_lightness_in_valid_range(self):
        img = _make_uniform_image(150, 120, 90)
        L, _, _ = extract_skin_lab(img)
        assert 0 <= L <= 100

    def test_deterministic_with_same_input(self):
        img = _make_uniform_image(190, 155, 125)
        r1 = extract_skin_lab(img)
        r2 = extract_skin_lab(img)
        assert r1 == r2

    def test_different_colors_give_different_results(self):
        light = extract_skin_lab(_make_uniform_image(240, 220, 200))
        dark = extract_skin_lab(_make_uniform_image(80, 50, 30))
        assert light[0] > dark[0]  # lighter image has higher L*


# ── classify_tone_from_lab (ITA-based, Chardon et al. 1991) ──────────────────


class TestClassifyToneFromLab:
    """Skin tone classification via ITA = arctan((L*-50)/b*) × 180/π.

    Thresholds from Chardon et al. (1991):
        >55° fair, >41° light, >28° medium, >10° tan, >-30° dark, else deep
    """

    @pytest.mark.parametrize("L, b, expected", [
        # fair: ITA > 55°
        (90.0, 15.0, "fair"),     # ITA ≈ 69.4°
        (80.0, 10.0, "fair"),     # ITA ≈ 71.6°
        (75.0, 12.0, "fair"),     # ITA ≈ 64.4°
        # light: 41° < ITA ≤ 55°
        (70.0, 15.0, "light"),    # ITA ≈ 53.1°
        (65.0, 12.0, "light"),    # ITA ≈ 51.3°
        (68.0, 20.0, "light"),    # ITA ≈ 42.0°
        # medium: 28° < ITA ≤ 41°
        (62.0, 18.0, "medium"),   # ITA ≈ 33.7°
        (60.0, 15.0, "medium"),   # ITA ≈ 33.7°
    ])
    def test_tone_thresholds(self, L, b, expected):
        assert classify_tone_from_lab(L, b) == expected

    # Fix the parametrize — let me recalculate
    @pytest.mark.parametrize("L, b, expected", [
        # medium: 28° < ITA ≤ 41°
        (58.0, 12.0, "medium"),   # ITA ≈ 33.7°
        (55.0, 8.0, "medium"),    # ITA ≈ 32.0°
        # tan: 10° < ITA ≤ 28°
        (55.0, 20.0, "tan"),      # ITA ≈ 14.0°
        (53.0, 15.0, "tan"),      # ITA ≈ 11.3°
        # dark: -30° < ITA ≤ 10°
        (50.0, 15.0, "dark"),     # ITA ≈ 0.0°
        (48.0, 12.0, "dark"),     # ITA ≈ -9.5°
        (42.0, 15.0, "dark"),     # ITA ≈ -28.1°
        # deep: ITA ≤ -30°
        (30.0, 10.0, "deep"),     # ITA ≈ -63.4°
        (20.0, 15.0, "deep"),     # ITA ≈ -63.4°
        (10.0, 5.0, "deep"),      # ITA ≈ -82.9°
    ])
    def test_tone_thresholds_lower(self, L, b, expected):
        assert classify_tone_from_lab(L, b) == expected

    def test_boundary_fair_light(self):
        """ITA exactly at 55° boundary."""
        # ITA=55° when (L-50)/b = tan(55°) = 1.4281
        # With b=10: L = 50 + 14.281 = 64.281
        assert classify_tone_from_lab(64.29, 10.0) == "fair"   # ITA ≈ 55.01°
        assert classify_tone_from_lab(64.27, 10.0) == "light"  # ITA ≈ 54.99°

    def test_boundary_light_medium(self):
        """ITA exactly at 41° boundary."""
        # tan(41°) = 0.8693; with b=10: L = 50 + 8.693 = 58.693
        assert classify_tone_from_lab(58.70, 10.0) == "light"  # ITA ≈ 41.01°
        assert classify_tone_from_lab(58.69, 10.0) == "medium" # ITA ≈ 40.99°

    def test_all_six_tones_reachable(self):
        tones = {
            classify_tone_from_lab(90, 15),   # fair
            classify_tone_from_lab(70, 15),   # light
            classify_tone_from_lab(58, 12),   # medium
            classify_tone_from_lab(55, 20),   # tan
            classify_tone_from_lab(48, 12),   # dark
            classify_tone_from_lab(20, 10),   # deep
        }
        assert tones == {"fair", "light", "medium", "tan", "dark", "deep"}

    def test_zero_b_handled(self):
        """b*=0 should not cause division by zero."""
        result = classify_tone_from_lab(80.0, 0.0)
        assert result in {"fair", "light", "medium", "tan", "dark", "deep"}

    def test_ita_considers_both_L_and_b(self):
        """Same L* but different b* should give different tones."""
        # L=65, b=5: ITA ≈ 71.6° → fair
        # L=65, b=30: ITA ≈ 26.6° → tan
        assert classify_tone_from_lab(65.0, 5.0) == "fair"
        assert classify_tone_from_lab(65.0, 30.0) == "tan"


# ── classify_undertone_from_lab (hue angle, Xiao et al. 2017) ────────────────


class TestClassifyUndertoneFromLab:
    """Undertone classification via h_ab = atan2(b*, a*) in degrees.

    Thresholds from Xiao et al. (2017) skin color distributions:
        h_ab > 65° → warm, h_ab < 50° → cool, else neutral
    """

    @pytest.mark.parametrize("a, b, expected", [
        # Warm: h_ab > 65°
        (10.0, 25.0, "warm"),    # h_ab ≈ 68.2°
        (5.0, 20.0, "warm"),     # h_ab ≈ 76.0°
        (15.0, 35.0, "warm"),    # h_ab ≈ 66.8°
        (8.0, 22.0, "warm"),     # h_ab ≈ 70.0°
        # Cool: h_ab < 50°
        (15.0, 8.0, "cool"),     # h_ab ≈ 28.1°
        (12.0, 10.0, "cool"),    # h_ab ≈ 39.8°
        (20.0, 15.0, "cool"),    # h_ab ≈ 36.9°
        (10.0, 5.0, "cool"),     # h_ab ≈ 26.6°
        # Neutral: 50° ≤ h_ab ≤ 65°
        (10.0, 15.0, "neutral"), # h_ab ≈ 56.3°
        (8.0, 12.0, "neutral"),  # h_ab ≈ 56.3°
        (12.0, 18.0, "neutral"), # h_ab ≈ 56.3°
        (9.0, 14.0, "neutral"),  # h_ab ≈ 57.3°
    ])
    def test_undertone_classification(self, a, b, expected):
        assert classify_undertone_from_lab(a, b) == expected

    def test_warm_boundary(self):
        """h_ab at 65° boundary."""
        # h_ab = 65° when b/a = tan(65°) = 2.1445
        # With a=10: b = 21.445
        assert classify_undertone_from_lab(10.0, 21.45) == "warm"    # h_ab ≈ 65.01°
        assert classify_undertone_from_lab(10.0, 21.44) == "neutral" # h_ab ≈ 64.99°

    def test_cool_boundary(self):
        """h_ab at 50° boundary."""
        # h_ab = 50° when b/a = tan(50°) = 1.1918
        # With a=10: b = 11.918
        assert classify_undertone_from_lab(10.0, 11.91) == "cool"     # h_ab ≈ 49.97°
        assert classify_undertone_from_lab(10.0, 11.92) == "neutral"  # h_ab ≈ 49.98° — hmm close

    def test_all_three_undertones_reachable(self):
        undertones = {
            classify_undertone_from_lab(5, 20),    # warm (h_ab ≈ 76°)
            classify_undertone_from_lab(15, 8),     # cool (h_ab ≈ 28°)
            classify_undertone_from_lab(10, 15),    # neutral (h_ab ≈ 56°)
        }
        assert undertones == {"warm", "cool", "neutral"}


# ── match_season_by_delta_e ───────────────────────────────────────────────────


class TestMatchSeasonByDeltaE:
    def test_empty_refs_returns_fallback(self):
        season, pid, conf = match_season_by_delta_e((65.0, 14.0, 22.0), [])
        assert season == "spring"
        assert pid is None
        assert conf == 85.0

    def test_exact_match_spring_light(self):
        """Skin exactly at spring-light centroid should match spring."""
        season, pid, conf = match_season_by_delta_e((75.0, 14.0, 22.0), PALETTE_REFS)
        assert season == "spring"
        assert pid == 1

    def test_exact_match_winter_deep(self):
        """Skin exactly at winter-deep centroid should match winter."""
        season, pid, conf = match_season_by_delta_e((40.0, 10.0, 14.0), PALETTE_REFS)
        assert season == "winter"
        assert pid == 12

    def test_exact_match_summer_true(self):
        season, pid, conf = match_season_by_delta_e((72.0, 8.0, 10.0), PALETTE_REFS)
        assert season == "summer"
        assert pid == 5

    def test_exact_match_autumn_true(self):
        season, pid, conf = match_season_by_delta_e((60.0, 16.0, 30.0), PALETTE_REFS)
        assert season == "autumn"
        assert pid == 8

    def test_confidence_is_high_for_exact_match(self):
        _, _, conf = match_season_by_delta_e((75.0, 14.0, 22.0), PALETTE_REFS)
        assert conf >= 80.0

    def test_confidence_clamped_to_range(self):
        """Confidence should always be in [50, 99]."""
        for lab in [(75, 14, 22), (40, 10, 14), (60, 12, 20), (90, 0, 0)]:
            _, _, conf = match_season_by_delta_e(lab, PALETTE_REFS)
            assert 50.0 <= conf <= 99.0

    def test_very_distant_skin_still_returns_a_match(self):
        """Even an extreme Lab value should return a season, not crash."""
        season, pid, conf = match_season_by_delta_e((10.0, -30.0, -50.0), PALETTE_REFS)
        assert season in ("spring", "summer", "autumn", "winter")
        assert pid is not None
        assert 50.0 <= conf <= 99.0

    def test_returns_three_values(self):
        result = match_season_by_delta_e((65.0, 12.0, 18.0), PALETTE_REFS)
        assert len(result) == 3

    def test_palette_id_is_int(self):
        _, pid, _ = match_season_by_delta_e((65.0, 12.0, 18.0), PALETTE_REFS)
        assert isinstance(pid, int)

    def test_single_ref_returns_that_ref(self):
        single = [PALETTE_REFS[0]]
        season, pid, conf = match_season_by_delta_e((50.0, 10.0, 15.0), single)
        assert season == "spring"
        assert pid == 1
        assert conf == 85.0  # single ref uses fallback confidence

    def test_nearby_skin_matches_nearest_centroid(self):
        """Skin slightly warm of summer-light should still match summer-light
        rather than spring-light, because it's geometrically closer."""
        # summer-light centroid: (78, 10, 12)
        # spring-light centroid: (75, 14, 22)
        # Test point: (77, 10, 13) — very close to summer-light
        season, pid, _ = match_season_by_delta_e((77.0, 10.0, 13.0), PALETTE_REFS)
        assert season == "summer"
        assert pid == 4


# ── Characterization: full pipeline snapshots ─────────────────────────────────


class TestPipelineSnapshots:
    """Pin end-to-end behavior for representative skin tones.

    These use ITA (skin tone) and h_ab (undertone) formulas.
    RGB → Lab values are approximate (computed via colour-science sRGB→XYZ→Lab).
    """

    @pytest.mark.parametrize("rgb, expected_tone, expected_undertone", [
        # (240,220,200): L*≈88.9, a*≈3.7, b*≈12.3 → ITA≈72.5° fair, h_ab≈73.3° warm
        ((240, 220, 200), "fair", "warm"),
        # (210,170,130): L*≈72.3, a*≈9.2, b*≈26.2 → ITA≈40.4° medium, h_ab≈70.6° warm
        ((210, 170, 130), "medium", "warm"),
        # (180,140,100): L*≈61.1, a*≈9.9, b*≈27.2 → ITA≈22.2° tan, h_ab≈70.0° warm
        ((180, 140, 100), "tan", "warm"),
        # (130,100,70): L*≈44.7, a*≈7.9, b*≈21.6 → ITA≈-13.8° dark, h_ab≈69.9° warm
        ((130, 100, 70), "dark", "warm"),
        # (80,55,35): L*≈25.4, a*≈8.4, b*≈16.9 → ITA≈-55.5° deep, h_ab≈63.6° neutral
        ((80, 55, 35), "deep", "neutral"),
        # (40,25,15): L*≈10.4, a*≈6.0, b*≈9.2 → ITA≈-76.9° deep, h_ab≈56.9° neutral
        ((40, 25, 15), "deep", "neutral"),
    ])
    def test_tone_undertone_from_uniform_image(self, rgb, expected_tone, expected_undertone):
        img = _make_uniform_image(*rgb)
        L, a, b = extract_skin_lab(img)
        tone = classify_tone_from_lab(L, b)
        undertone = classify_undertone_from_lab(a, b)
        assert tone == expected_tone
        assert undertone == expected_undertone

    @pytest.mark.parametrize("rgb, expected_season", [
        ((240, 220, 200), "summer"),    # L*≈88.9 → nearest summer-light
        ((210, 170, 130), "autumn"),    # L*≈72.3, b*≈26 → nearest autumn-soft
        ((130, 100, 70), "winter"),     # L*≈44.7 → nearest winter-deep
        ((40, 25, 15), "winter"),       # L*≈10.4 → nearest winter-deep
    ])
    def test_season_from_uniform_image(self, rgb, expected_season):
        img = _make_uniform_image(*rgb)
        L, a, b = extract_skin_lab(img)
        season, _, _ = match_season_by_delta_e((L, a, b), PALETTE_REFS)
        assert season == expected_season
