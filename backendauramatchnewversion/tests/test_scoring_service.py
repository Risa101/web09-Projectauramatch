"""
Characterization tests for the multi-signal scoring engine.

Tests pure scoring functions only (no database required).
Run: python3 -m pytest tests/test_scoring_service.py -v
"""

import pytest
from services.scoring_service import (
    hex_to_lab,
    compute_color_proximity,
    compute_avoid_penalty,
    compute_personal_color_score,
    compute_final_score,
    compute_concern_bonus,
    rating_to_s5,
)


# ── hex_to_lab ──────────────────────────────────────────────────────────────

class TestHexToLab:
    def test_pure_white(self):
        L, a, b = hex_to_lab("#FFFFFF")
        assert abs(L - 100.0) < 1.0
        assert abs(a) < 1.0
        assert abs(b) < 1.0

    def test_pure_black(self):
        L, a, b = hex_to_lab("#000000")
        assert abs(L) < 1.0

    def test_red_has_positive_a(self):
        L, a, b = hex_to_lab("#FF0000")
        assert a > 40  # red is strongly positive a*

    def test_caching_returns_same_result(self):
        r1 = hex_to_lab("#AABBCC")
        r2 = hex_to_lab("#AABBCC")
        assert r1 == r2


# ── compute_color_proximity (S2) ────────────────────────────────────────────

class TestColorProximity:
    def test_perfect_match_yields_300(self):
        shade = [(65.0, 30.0, 20.0)]
        palette = [(65.0, 30.0, 20.0)]
        score = compute_color_proximity(shade, palette)
        assert abs(score - 300.0) < 1.0

    def test_very_distant_yields_zero(self):
        shade = [(90.0, -40.0, -30.0)]  # cool bright
        palette = [(30.0, 40.0, 50.0)]  # warm dark
        score = compute_color_proximity(shade, palette)
        assert score == 0.0

    def test_mid_range_distance(self):
        # delta E ~25 should yield ~150
        shade = [(65.0, 30.0, 20.0)]
        palette = [(65.0, 5.0, 20.0)]  # shifted a* by 25
        score = compute_color_proximity(shade, palette)
        assert 100.0 < score < 250.0

    def test_multiple_shades_takes_best(self):
        # One shade is distant, one is close
        shades = [(90.0, -40.0, -30.0), (65.0, 30.0, 20.0)]
        palette = [(65.0, 30.0, 20.0)]
        score = compute_color_proximity(shades, palette)
        assert abs(score - 300.0) < 1.0  # best shade matches

    def test_no_shades_returns_neutral(self):
        score = compute_color_proximity([], [(65.0, 30.0, 20.0)])
        assert score == 150.0

    def test_no_palette_returns_neutral(self):
        score = compute_color_proximity([(65.0, 30.0, 20.0)], [])
        assert score == 150.0


# ── compute_avoid_penalty (S4) ──────────────────────────────────────────────

class TestAvoidPenalty:
    def test_exact_avoid_match_yields_max_penalty(self):
        shade = [(30.0, 30.0, 15.0)]
        avoid = [(30.0, 30.0, 15.0)]
        score = compute_avoid_penalty(shade, avoid)
        assert abs(score - (-100.0)) < 1.0

    def test_distant_from_avoid_no_penalty(self):
        shade = [(80.0, -20.0, 30.0)]
        avoid = [(30.0, 30.0, 15.0)]
        score = compute_avoid_penalty(shade, avoid)
        assert score == 0.0

    def test_close_but_not_exact(self):
        # delta E ~7.5 → penalty ~-50
        shade = [(30.0, 30.0, 15.0)]
        avoid = [(30.0, 22.5, 15.0)]  # shifted a* by ~7.5
        score = compute_avoid_penalty(shade, avoid)
        assert -80.0 < score < -20.0

    def test_no_shades_no_penalty(self):
        assert compute_avoid_penalty([], [(30.0, 30.0, 15.0)]) == 0.0

    def test_no_avoid_colors_no_penalty(self):
        assert compute_avoid_penalty([(30.0, 30.0, 15.0)], []) == 0.0


# ── compute_personal_color_score (S3) ───────────────────────────────────────

class TestPersonalColorScore:
    def test_exact_match(self):
        assert compute_personal_color_score("spring,summer", "spring") == 150.0

    def test_no_match(self):
        assert compute_personal_color_score("spring,summer", "winter") == 0.0

    def test_single_season_match(self):
        assert compute_personal_color_score("autumn", "autumn") == 150.0

    def test_null_product_returns_neutral(self):
        assert compute_personal_color_score(None, "spring") == 75.0

    def test_empty_string_returns_neutral(self):
        assert compute_personal_color_score("", "spring") == 75.0

    def test_case_insensitive(self):
        assert compute_personal_color_score("Spring,Summer", "spring") == 150.0


# ── compute_final_score ─────────────────────────────────────────────────────

class TestFinalScore:
    def test_all_max_signals(self):
        # 300 + 300 + 150 + 0 + 100 + 50 = 900
        score = compute_final_score(300, 300, 150, 0, 100, 50)
        assert score == 900.0

    def test_clamp_upper_bound(self):
        score = compute_final_score(300, 300, 150, 0, 100, 200)
        assert score == 999.99

    def test_clamp_lower_bound(self):
        score = compute_final_score(0, 0, 0, -100, 0, 0)
        assert score == 0.0

    def test_penalty_reduces_score(self):
        without_penalty = compute_final_score(300, 300, 150, 0, 50, 25)
        with_penalty = compute_final_score(300, 300, 150, -80, 50, 25)
        assert with_penalty < without_penalty
        assert with_penalty == without_penalty - 80

    def test_known_composite(self):
        # S1=200, S2=150, S3=75, S4=-30, S5=50, S6=25 = 470
        score = compute_final_score(200, 150, 75, -30, 50, 25)
        assert score == 470.0

    def test_all_zeros(self):
        assert compute_final_score(0, 0, 0, 0, 0, 0) == 0.0


# ── compute_concern_bonus ──────────────────────────────────────────────────

class TestConcernBonus:
    def test_no_overlap(self):
        assert compute_concern_bonus({1, 2}, {3, 4}) == 0.0

    def test_single_overlap(self):
        assert compute_concern_bonus({1, 2, 3}, {2, 4}) == 20.0

    def test_double_overlap(self):
        assert compute_concern_bonus({1, 2, 3}, {2, 3}) == 40.0

    def test_triple_overlap_capped_at_60(self):
        assert compute_concern_bonus({1, 2, 3, 4}, {1, 2, 3}) == 60.0

    def test_more_than_three_overlap_still_capped(self):
        assert compute_concern_bonus({1, 2, 3, 4}, {1, 2, 3, 4}) == 60.0

    def test_empty_product_concerns(self):
        assert compute_concern_bonus(set(), {1, 2}) == 0.0

    def test_empty_user_concerns(self):
        assert compute_concern_bonus({1, 2}, set()) == 0.0

    def test_both_empty(self):
        assert compute_concern_bonus(set(), set()) == 0.0


# ── rating_to_s5 ─────────────────────────────────────────────────────────

class TestRatingToS5:
    def test_perfect_rating(self):
        assert rating_to_s5(5.0) == 100.0

    def test_lowest_rating(self):
        assert rating_to_s5(1.0) == 20.0

    def test_mid_rating(self):
        assert abs(rating_to_s5(3.0) - 60.0) < 0.01

    def test_none_returns_default(self):
        assert rating_to_s5(None) == 50.0

    def test_fractional_rating(self):
        assert abs(rating_to_s5(4.5) - 90.0) < 0.01
