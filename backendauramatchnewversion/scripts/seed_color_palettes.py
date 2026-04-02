"""Seed the color_palettes table with 12-season personal color reference data.

Each row contains:
  - season / sub_type: the 4-season base + 12-season modifier
  - best_colors JSON: includes a skin_reference centroid (L*a*b*) for CIEDE2000
    matching, plus an array of recommended palette colors
  - avoid_colors JSON: colors to avoid for this sub-season

Run: python scripts/seed_color_palettes.py
Idempotent — skips insert if rows already exist.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.database import SessionLocal
from models.analysis import ColorPalette


PALETTES = [
    # ── Spring ────────────────────────────────────────────────────────────────
    {
        "season": "spring",
        "sub_type": "light",
        "description": "Light Spring: warm undertone, light and delicate coloring",
        "best_colors": {
            "skin_reference": {"L": 75.0, "a": 14.0, "b": 22.0},
            "colors": [
                {"name": "Peach", "L": 76.0, "a": 15.0, "b": 26.0, "hex": "#FFCBA4"},
                {"name": "Light Coral", "L": 65.0, "a": 30.0, "b": 20.0, "hex": "#F08080"},
                {"name": "Warm Ivory", "L": 90.0, "a": 2.0, "b": 14.0, "hex": "#FFF8DC"},
                {"name": "Soft Gold", "L": 80.0, "a": 5.0, "b": 40.0, "hex": "#F0D58C"},
                {"name": "Aquamarine", "L": 78.0, "a": -20.0, "b": 2.0, "hex": "#7FFFD4"},
            ],
        },
        "avoid_colors": {
            "colors": [
                {"name": "Black", "L": 0.0, "a": 0.0, "b": 0.0, "hex": "#000000"},
                {"name": "Deep Burgundy", "L": 25.0, "a": 30.0, "b": 15.0, "hex": "#800020"},
            ],
        },
        "makeup_tips": "Use warm peach and coral tones for blush and lip. Avoid heavy dark shades. Gold-toned highlighter works well.",
    },
    {
        "season": "spring",
        "sub_type": "true",
        "description": "True Spring: classic warm, clear, and medium-light coloring",
        "best_colors": {
            "skin_reference": {"L": 68.0, "a": 16.0, "b": 28.0},
            "colors": [
                {"name": "Warm Coral", "L": 62.0, "a": 35.0, "b": 28.0, "hex": "#FF6F61"},
                {"name": "Sunflower", "L": 82.0, "a": 5.0, "b": 60.0, "hex": "#FFDA03"},
                {"name": "Tangerine", "L": 65.0, "a": 40.0, "b": 55.0, "hex": "#FF9966"},
                {"name": "Lime Green", "L": 75.0, "a": -30.0, "b": 45.0, "hex": "#A4C639"},
                {"name": "Turquoise", "L": 70.0, "a": -25.0, "b": -5.0, "hex": "#40E0D0"},
            ],
        },
        "avoid_colors": {
            "colors": [
                {"name": "Charcoal", "L": 20.0, "a": 0.0, "b": 0.0, "hex": "#36454F"},
                {"name": "Cool Mauve", "L": 55.0, "a": 15.0, "b": -10.0, "hex": "#E0B0FF"},
            ],
        },
        "makeup_tips": "Warm coral lips, golden bronzer, and warm brown eyeshadow. Avoid cool pinks and silver tones.",
    },
    {
        "season": "spring",
        "sub_type": "bright",
        "description": "Bright Spring: warm with high contrast and vivid coloring",
        "best_colors": {
            "skin_reference": {"L": 62.0, "a": 18.0, "b": 32.0},
            "colors": [
                {"name": "Hot Coral", "L": 58.0, "a": 50.0, "b": 35.0, "hex": "#FF4040"},
                {"name": "Electric Blue", "L": 55.0, "a": -5.0, "b": -40.0, "hex": "#0892D0"},
                {"name": "Bright Yellow", "L": 90.0, "a": -5.0, "b": 75.0, "hex": "#FFE135"},
                {"name": "Kelly Green", "L": 55.0, "a": -40.0, "b": 30.0, "hex": "#4CBB17"},
                {"name": "Warm Fuchsia", "L": 50.0, "a": 55.0, "b": -5.0, "hex": "#FF00FF"},
            ],
        },
        "avoid_colors": {
            "colors": [
                {"name": "Dusty Rose", "L": 60.0, "a": 15.0, "b": 5.0, "hex": "#DCAE96"},
                {"name": "Olive", "L": 50.0, "a": -5.0, "b": 20.0, "hex": "#808000"},
            ],
        },
        "makeup_tips": "Bold warm lips (coral, warm red), vibrant blush. High-pigment eyeshadow in warm jewel tones.",
    },

    # ── Summer ────────────────────────────────────────────────────────────────
    {
        "season": "summer",
        "sub_type": "light",
        "description": "Light Summer: cool undertone, light and soft coloring",
        "best_colors": {
            "skin_reference": {"L": 78.0, "a": 10.0, "b": 12.0},
            "colors": [
                {"name": "Powder Blue", "L": 80.0, "a": -5.0, "b": -15.0, "hex": "#B0E0E6"},
                {"name": "Lavender", "L": 75.0, "a": 10.0, "b": -15.0, "hex": "#E6E6FA"},
                {"name": "Soft Rose", "L": 70.0, "a": 18.0, "b": 5.0, "hex": "#FFB7C5"},
                {"name": "Sage", "L": 65.0, "a": -10.0, "b": 10.0, "hex": "#BCB88A"},
                {"name": "Mauve", "L": 60.0, "a": 15.0, "b": -8.0, "hex": "#E0B0FF"},
            ],
        },
        "avoid_colors": {
            "colors": [
                {"name": "Bright Orange", "L": 65.0, "a": 40.0, "b": 60.0, "hex": "#FF8C00"},
                {"name": "True Black", "L": 0.0, "a": 0.0, "b": 0.0, "hex": "#000000"},
            ],
        },
        "makeup_tips": "Soft pink and rose lips, cool-toned blush. Lavender and taupe eyeshadow. Silver-toned accessories.",
    },
    {
        "season": "summer",
        "sub_type": "true",
        "description": "True Summer: classic cool, muted, medium coloring",
        "best_colors": {
            "skin_reference": {"L": 72.0, "a": 8.0, "b": 10.0},
            "colors": [
                {"name": "Dusty Rose", "L": 60.0, "a": 20.0, "b": 5.0, "hex": "#DCAE96"},
                {"name": "Slate Blue", "L": 55.0, "a": 0.0, "b": -20.0, "hex": "#6A5ACD"},
                {"name": "Cool Cocoa", "L": 45.0, "a": 8.0, "b": 10.0, "hex": "#8B7D6B"},
                {"name": "Raspberry", "L": 40.0, "a": 40.0, "b": -5.0, "hex": "#E30B5C"},
                {"name": "Periwinkle", "L": 65.0, "a": 10.0, "b": -25.0, "hex": "#CCCCFF"},
            ],
        },
        "avoid_colors": {
            "colors": [
                {"name": "Warm Gold", "L": 75.0, "a": 5.0, "b": 50.0, "hex": "#FFD700"},
                {"name": "Rust", "L": 45.0, "a": 30.0, "b": 40.0, "hex": "#B7410E"},
            ],
        },
        "makeup_tips": "Cool rose and berry lips. Soft plum and cool taupe eyeshadow. Avoid orangey bronzers.",
    },
    {
        "season": "summer",
        "sub_type": "soft",
        "description": "Soft Summer: cool-neutral, muted, blended coloring",
        "best_colors": {
            "skin_reference": {"L": 65.0, "a": 9.0, "b": 14.0},
            "colors": [
                {"name": "Soft Teal", "L": 55.0, "a": -15.0, "b": -8.0, "hex": "#5F9EA0"},
                {"name": "Dusty Plum", "L": 40.0, "a": 20.0, "b": -10.0, "hex": "#8E4585"},
                {"name": "Mushroom", "L": 55.0, "a": 3.0, "b": 8.0, "hex": "#C9B29B"},
                {"name": "Soft Navy", "L": 25.0, "a": 0.0, "b": -15.0, "hex": "#2C3E50"},
                {"name": "Muted Rose", "L": 60.0, "a": 15.0, "b": 3.0, "hex": "#C08081"},
            ],
        },
        "avoid_colors": {
            "colors": [
                {"name": "Neon Yellow", "L": 95.0, "a": -10.0, "b": 80.0, "hex": "#FFFF00"},
                {"name": "Bright Red", "L": 50.0, "a": 60.0, "b": 40.0, "hex": "#FF0000"},
            ],
        },
        "makeup_tips": "Muted mauve and dusty rose tones. Soft smoky eyes with cool grays. Avoid anything too bright or warm.",
    },

    # ── Autumn ────────────────────────────────────────────────────────────────
    {
        "season": "autumn",
        "sub_type": "soft",
        "description": "Soft Autumn: warm-neutral, muted, earthy coloring",
        "best_colors": {
            "skin_reference": {"L": 70.0, "a": 14.0, "b": 26.0},
            "colors": [
                {"name": "Camel", "L": 65.0, "a": 10.0, "b": 30.0, "hex": "#C19A6B"},
                {"name": "Olive Green", "L": 45.0, "a": -10.0, "b": 25.0, "hex": "#6B8E23"},
                {"name": "Terracotta", "L": 50.0, "a": 25.0, "b": 30.0, "hex": "#E2725B"},
                {"name": "Warm Taupe", "L": 55.0, "a": 5.0, "b": 12.0, "hex": "#B8A99A"},
                {"name": "Burnt Sienna", "L": 45.0, "a": 25.0, "b": 35.0, "hex": "#E97451"},
            ],
        },
        "avoid_colors": {
            "colors": [
                {"name": "Icy Pink", "L": 85.0, "a": 10.0, "b": -5.0, "hex": "#FFB6C1"},
                {"name": "Electric Blue", "L": 55.0, "a": -5.0, "b": -40.0, "hex": "#0892D0"},
            ],
        },
        "makeup_tips": "Warm muted tones: terracotta blush, nude-warm lips. Eyeshadow in olive, bronze, copper.",
    },
    {
        "season": "autumn",
        "sub_type": "true",
        "description": "True Autumn: classic warm, rich, earthy coloring",
        "best_colors": {
            "skin_reference": {"L": 60.0, "a": 16.0, "b": 30.0},
            "colors": [
                {"name": "Pumpkin", "L": 60.0, "a": 35.0, "b": 50.0, "hex": "#FF7518"},
                {"name": "Forest Green", "L": 35.0, "a": -25.0, "b": 20.0, "hex": "#228B22"},
                {"name": "Warm Red", "L": 45.0, "a": 50.0, "b": 35.0, "hex": "#CC0000"},
                {"name": "Chocolate", "L": 30.0, "a": 15.0, "b": 20.0, "hex": "#7B3F00"},
                {"name": "Mustard", "L": 70.0, "a": 5.0, "b": 55.0, "hex": "#E1AD01"},
            ],
        },
        "avoid_colors": {
            "colors": [
                {"name": "Cool Pink", "L": 70.0, "a": 25.0, "b": -10.0, "hex": "#FF69B4"},
                {"name": "Icy Blue", "L": 80.0, "a": -5.0, "b": -20.0, "hex": "#ADD8E6"},
            ],
        },
        "makeup_tips": "Rich warm tones: burnt orange, brick red lips. Bronze and copper eyeshadow. Gold accessories.",
    },
    {
        "season": "autumn",
        "sub_type": "deep",
        "description": "Deep Autumn: warm, dark, rich coloring",
        "best_colors": {
            "skin_reference": {"L": 50.0, "a": 18.0, "b": 28.0},
            "colors": [
                {"name": "Burgundy", "L": 30.0, "a": 30.0, "b": 15.0, "hex": "#800020"},
                {"name": "Dark Teal", "L": 35.0, "a": -15.0, "b": -10.0, "hex": "#008080"},
                {"name": "Burnt Orange", "L": 55.0, "a": 30.0, "b": 45.0, "hex": "#CC5500"},
                {"name": "Espresso", "L": 25.0, "a": 8.0, "b": 15.0, "hex": "#3C1414"},
                {"name": "Olive", "L": 45.0, "a": -8.0, "b": 30.0, "hex": "#808000"},
            ],
        },
        "avoid_colors": {
            "colors": [
                {"name": "Pastel Pink", "L": 85.0, "a": 10.0, "b": 2.0, "hex": "#FFD1DC"},
                {"name": "Lemon Yellow", "L": 92.0, "a": -8.0, "b": 70.0, "hex": "#FFF44F"},
            ],
        },
        "makeup_tips": "Deep warm tones: burgundy or brick lips. Rich brown and copper eyeshadow. Bronzer with warm undertone.",
    },

    # ── Winter ────────────────────────────────────────────────────────────────
    {
        "season": "winter",
        "sub_type": "bright",
        "description": "Bright Winter: cool with high contrast, vivid coloring",
        "best_colors": {
            "skin_reference": {"L": 73.0, "a": 6.0, "b": 8.0},
            "colors": [
                {"name": "True Red", "L": 45.0, "a": 55.0, "b": 30.0, "hex": "#FF0000"},
                {"name": "Royal Blue", "L": 35.0, "a": 10.0, "b": -45.0, "hex": "#4169E1"},
                {"name": "Hot Pink", "L": 55.0, "a": 55.0, "b": -5.0, "hex": "#FF69B4"},
                {"name": "Emerald", "L": 50.0, "a": -40.0, "b": 15.0, "hex": "#50C878"},
                {"name": "Pure White", "L": 100.0, "a": 0.0, "b": 0.0, "hex": "#FFFFFF"},
            ],
        },
        "avoid_colors": {
            "colors": [
                {"name": "Muted Peach", "L": 72.0, "a": 12.0, "b": 20.0, "hex": "#FFDAB9"},
                {"name": "Olive Drab", "L": 50.0, "a": -5.0, "b": 20.0, "hex": "#6B8E23"},
            ],
        },
        "makeup_tips": "Bold cool lips (true red, hot pink). Bright jewel-toned eyeshadow. Silver accessories. High contrast looks.",
    },
    {
        "season": "winter",
        "sub_type": "true",
        "description": "True Winter: classic cool, deep, and clear coloring",
        "best_colors": {
            "skin_reference": {"L": 55.0, "a": 8.0, "b": 10.0},
            "colors": [
                {"name": "Cool Red", "L": 42.0, "a": 50.0, "b": 20.0, "hex": "#DC143C"},
                {"name": "Navy", "L": 20.0, "a": 5.0, "b": -25.0, "hex": "#000080"},
                {"name": "Magenta", "L": 48.0, "a": 60.0, "b": -15.0, "hex": "#FF00FF"},
                {"name": "Pine Green", "L": 30.0, "a": -25.0, "b": 10.0, "hex": "#01796F"},
                {"name": "True Black", "L": 0.0, "a": 0.0, "b": 0.0, "hex": "#000000"},
            ],
        },
        "avoid_colors": {
            "colors": [
                {"name": "Warm Gold", "L": 75.0, "a": 5.0, "b": 50.0, "hex": "#FFD700"},
                {"name": "Peach", "L": 76.0, "a": 15.0, "b": 26.0, "hex": "#FFCBA4"},
            ],
        },
        "makeup_tips": "Cool berry and wine lips. Smoky eyes with cool grays and deep plums. Silver or platinum accessories.",
    },
    {
        "season": "winter",
        "sub_type": "deep",
        "description": "Deep Winter: cool, very dark, rich coloring",
        "best_colors": {
            "skin_reference": {"L": 40.0, "a": 10.0, "b": 14.0},
            "colors": [
                {"name": "Deep Berry", "L": 30.0, "a": 35.0, "b": -5.0, "hex": "#8E4585"},
                {"name": "Black", "L": 0.0, "a": 0.0, "b": 0.0, "hex": "#000000"},
                {"name": "Dark Ruby", "L": 35.0, "a": 45.0, "b": 15.0, "hex": "#9B111E"},
                {"name": "Deep Teal", "L": 30.0, "a": -18.0, "b": -10.0, "hex": "#004D4D"},
                {"name": "Icy White", "L": 95.0, "a": 0.0, "b": -2.0, "hex": "#F0F8FF"},
            ],
        },
        "avoid_colors": {
            "colors": [
                {"name": "Warm Camel", "L": 65.0, "a": 10.0, "b": 30.0, "hex": "#C19A6B"},
                {"name": "Light Orange", "L": 75.0, "a": 20.0, "b": 50.0, "hex": "#FFA500"},
            ],
        },
        "makeup_tips": "Deep rich lips (dark berry, wine, deep red). Dramatic smoky eyes. High contrast with dark and bright colors.",
    },
]


def seed():
    db = SessionLocal()
    try:
        existing = db.query(ColorPalette).count()
        if existing >= 12:
            print(f"color_palettes already has {existing} rows — skipping seed.")
            return

        for data in PALETTES:
            palette = ColorPalette(
                season=data["season"],
                sub_type=data["sub_type"],
                description=data["description"],
                best_colors=data["best_colors"],
                avoid_colors=data["avoid_colors"],
                makeup_tips=data["makeup_tips"],
            )
            db.add(palette)

        db.commit()
        print(f"Seeded {len(PALETTES)} color palettes successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
