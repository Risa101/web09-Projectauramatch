"""Characterization tests for color_analysis_service.

These tests pin the current behavior of the CIELAB-based color analysis
pipeline so that future changes are detected. They do NOT test correctness
against ground truth — they capture what the code does *now*.
"""

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


# ── classify_tone_from_lab ────────────────────────────────────────────────────


class TestClassifyToneFromLab:
    @pytest.mark.parametrize("L, expected", [
        (95.0, "fair"),
        (79.0, "fair"),
        (78.0, "light"),    # boundary: exactly 78 is NOT > 78
        (75.0, "light"),
        (69.0, "light"),
        (68.0, "medium"),   # boundary
        (63.0, "medium"),
        (58.0, "tan"),      # boundary
        (53.0, "tan"),
        (48.0, "dark"),     # boundary
        (43.0, "dark"),
        (38.0, "deep"),     # boundary
        (30.0, "deep"),
        (10.0, "deep"),
        (0.0, "deep"),
    ])
    def test_tone_thresholds(self, L, expected):
        assert classify_tone_from_lab(L) == expected

    def test_boundary_fair_light(self):
        assert classify_tone_from_lab(78.001) == "fair"
        assert classify_tone_from_lab(78.0) == "light"

    def test_boundary_light_medium(self):
        assert classify_tone_from_lab(68.001) == "light"
        assert classify_tone_from_lab(68.0) == "medium"

    def test_all_six_tones_reachable(self):
        tones = {classify_tone_from_lab(L) for L in [90, 73, 63, 53, 43, 20]}
        assert tones == {"fair", "light", "medium", "tan", "dark", "deep"}


# ── classify_undertone_from_lab ───────────────────────────────────────────────


class TestClassifyUndertoneFromLab:
    @pytest.mark.parametrize("a, b, expected", [
        # Warm: b > 20 and a > 8
        (10.0, 25.0, "warm"),
        (15.0, 30.0, "warm"),
        (9.0, 21.0, "warm"),
        # Cool: b < 12
        (5.0, 8.0, "cool"),
        (10.0, 11.0, "cool"),
        (0.0, 0.0, "cool"),
        # Cool: a > 12 and b < 16
        (15.0, 14.0, "cool"),
        (13.0, 15.0, "cool"),
        # Neutral: b in [12, 20] and not (a > 12 and b < 16)
        (8.0, 15.0, "neutral"),
        (10.0, 18.0, "neutral"),
        (5.0, 12.0, "neutral"),
    ])
    def test_undertone_classification(self, a, b, expected):
        assert classify_undertone_from_lab(a, b) == expected

    def test_warm_boundary(self):
        # b=20 is NOT > 20, so not warm
        assert classify_undertone_from_lab(10.0, 20.0) == "neutral"
        assert classify_undertone_from_lab(10.0, 20.001) == "warm"

    def test_cool_boundary_low_b(self):
        # b=12 is NOT < 12, so not cool via first condition
        assert classify_undertone_from_lab(5.0, 11.999) == "cool"
        assert classify_undertone_from_lab(5.0, 12.0) == "neutral"

    def test_all_three_undertones_reachable(self):
        undertones = {
            classify_undertone_from_lab(10, 25),   # warm
            classify_undertone_from_lab(5, 8),      # cool
            classify_undertone_from_lab(8, 15),     # neutral
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
    """Pin end-to-end behavior for representative skin tones."""

    @pytest.mark.parametrize("rgb, expected_tone, expected_undertone", [
        ((240, 220, 200), "fair", "neutral"),    # L*≈88.9, a*≈3.7, b*≈12.3
        ((210, 170, 130), "light", "warm"),      # L*≈72.3, a*≈9.2, b*≈26.2
        ((180, 140, 100), "medium", "warm"),     # L*≈61.1, a*≈9.9, b*≈27.2
        ((130, 100, 70), "dark", "neutral"),     # L*≈44.7, a*≈7.9, b*≈21.6
        ((80, 55, 35), "deep", "neutral"),       # L*≈25.4, a*≈8.4, b*≈16.9
        ((40, 25, 15), "deep", "cool"),          # L*≈10.4, a*≈6.0, b*≈9.2
    ])
    def test_tone_undertone_from_uniform_image(self, rgb, expected_tone, expected_undertone):
        img = _make_uniform_image(*rgb)
        L, a, b = extract_skin_lab(img)
        tone = classify_tone_from_lab(L)
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
