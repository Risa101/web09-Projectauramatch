"""
สกัดสีเด่นจากรูป swatch ของเครื่องสำอาง → seed SQL

Methodology:
    อ้างอิงจาก Griffen, A., Bailey, J., & Whaley, R. (2018).
    "Beauty Brawl", The Pudding.
    https://pudding.cool/2018/06/makeup-shades/
    https://github.com/the-pudding/data/tree/master/makeup-shades

    ขั้นตอน:
    1. โหลดรูป swatch (จากไฟล์ local หรือ URL)
    2. Crop เฉพาะบริเวณ swatch (ตัดขอบขาว/พื้นหลัง)
    3. K-Means clustering → dominant color (สีเด่น)
    4. แปลง sRGB → XYZ (D65) → CIELAB ด้วย colour-science library
       Ref: Sharma, G., Wu, W., & Dalal, E.N. (2005).
       "The CIEDE2000 color-difference formula", Color Research & Application.
    5. จำแนก skin tone / undertone ตามทฤษฎี Personal Color:
       - ITA (Chardon et al., 1991) → skin tone
       - Hue angle (Xiao et al., 2017) → undertone
    6. Export เป็น INSERT INTO product_color_shades SQL

วิธีรัน:
    cd backendauramatchnewversion
    python scripts/extract_product_colors.py

    โครงสร้าง swatches/:
    swatches/
    ├── maybelline-vinyl-ink/
    │   ├── peachy.jpg
    │   ├── coy.jpg
    │   └── ...
    ├── mac-matte/
    │   ├── ruby-woo.jpg
    │   └── ...
    └── ...

    ชื่อโฟลเดอร์ต้องตรงกับ PRODUCT_MAP ด้านล่าง
    ชื่อไฟล์ = shade name (ไม่รวมนามสกุล)
"""

import os
import sys
import math
import numpy as np
from pathlib import Path
from sklearn.cluster import KMeans

try:
    import colour
except ImportError:
    print("❌ ต้องติดตั้ง colour-science: pip install colour-science")
    sys.exit(1)

try:
    import cv2
except ImportError:
    print("❌ ต้องติดตั้ง opencv-python: pip install opencv-python")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
# Config
# ═══════════════════════════════════════════════════════════════════════════════

SWATCHES_DIR = Path(__file__).parent.parent / "swatches"
OUTPUT_SQL = Path(__file__).parent.parent.parent / "seed_product_color_shades.sql"

# Map โฟลเดอร์ swatch → ชื่อสินค้าใน DB
PRODUCT_MAP = {
    # ลิปสติก (category_id = 1)
    "maybelline-vinyl-ink":     "Maybelline Super Stay Vinyl Ink Lipstick",
    "mac-matte":                "MAC M·A·Cximal Silky Matte Lipstick",
    "romand-juicy-lasting":     "Romand Juicy Lasting Tint",
    "3ce-velvet-lip":           "3CE Velvet Lip Tint",
    # บลัชออน (category_id = 3)
    "canmake-cream-cheek":      "Canmake Cream Cheek",
    "canmake-powder-cheeks":    "Canmake Powder Cheeks",
    "romand-better-than-cheek": "Romand Better Than Cheek",
    "mistine-blush":            "Mistine Matte Complete Blush",
    # อายแชโดว์ (category_id = 4)
    "3ce-multi-eye":            "3CE Multi Eye Color Palette",
    "romand-better-than-palette": "Romand Better Than Palette",
    "maybelline-the-nudes":     "Maybelline The Nudes Eyeshadow Palette",
    "canmake-perfect-stylist":  "Canmake Perfect Stylist Eyes",
    # ไฮไลท์ (category_id = 5)
    "canmake-munyutto":         "Canmake Munyutto Highlighter",
    "canmake-glow-fleur":       "Canmake Glow Fleur Highlighter",
    "mistine-highlighter":      "Mistine Wings Extra Cover Highlighter",
    # รองพื้น (category_id = 2)
    "maybelline-fit-me":        "Maybelline Fit Me Matte + Poreless Foundation",
    "mac-studio-fix":           "MAC Studio Fix Fluid SPF 15 Foundation",
    "canmake-marshmallow":      "Canmake Marshmallow Finish Powder",
    "mistine-wings-powder":     "Mistine Wings Extra Cover Super Powder",
}

# K-Means clusters สำหรับสกัดสีเด่น
N_CLUSTERS = 5
# ตัดขอบรูปกี่ % (ป้องกันพื้นหลังขาว/ดำ)
CROP_MARGIN_PCT = 0.15


# ═══════════════════════════════════════════════════════════════════════════════
# Color Science Functions
# ═══════════════════════════════════════════════════════════════════════════════

def rgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    """Convert (N,3) RGB [0-255] → CIELAB via sRGB → XYZ (D65) → Lab.

    Ref: colour-science library (colour.sRGB_to_XYZ, colour.XYZ_to_Lab)
    """
    rgb_norm = rgb.astype(np.float64) / 255.0
    xyz = colour.sRGB_to_XYZ(rgb_norm)
    lab = colour.XYZ_to_Lab(xyz)
    return lab


def lab_to_hex(L: float, a: float, b: float) -> str:
    """Convert CIELAB → sRGB hex (#RRGGBB).

    Ref: reverse path Lab → XYZ (D65) → sRGB
    """
    lab = np.array([L, a, b])
    xyz = colour.Lab_to_XYZ(lab)
    rgb = colour.XYZ_to_sRGB(xyz)
    rgb_clipped = np.clip(rgb * 255, 0, 255).astype(int)
    return "#{:02X}{:02X}{:02X}".format(*rgb_clipped)


def classify_tone(L: float, b_val: float) -> str:
    """Classify skin tone via ITA (Individual Typology Angle).

    ITA = arctan((L* - 50) / b*) × (180/π)

    Ref: Chardon, A., Cretois, I., & Hourseau, C. (1991).
         Skin colour typology and suntanning pathways.
         Int J Cosmet Sci, 13(4), 191-208.
    """
    if b_val == 0:
        b_val = 0.001
    ita = math.atan2(L - 50, b_val) * (180.0 / math.pi)

    if ita > 55:
        return "fair"
    elif ita > 41:
        return "light"
    elif ita > 28:
        return "medium"
    elif ita > 10:
        return "tan"
    elif ita > -30:
        return "dark"
    else:
        return "deep"


def classify_undertone(a: float, b_val: float) -> str:
    """Classify undertone via CIELAB hue angle.

    h_ab = atan2(b*, a*) in degrees

    Ref: Xiao, K., et al. (2017). Characterising the variations in
         ethnic skin colours. Skin Res Technol, 23(1), 21-29.
    """
    h_ab = math.degrees(math.atan2(b_val, a))
    if h_ab < 0:
        h_ab += 360

    if h_ab > 65:
        return "warm"
    elif h_ab < 50:
        return "cool"
    else:
        return "neutral"


# ═══════════════════════════════════════════════════════════════════════════════
# Image Processing
# ═══════════════════════════════════════════════════════════════════════════════

def load_and_crop(image_path: str) -> np.ndarray:
    """Load image, crop margins to remove background, return RGB array."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"ไม่สามารถโหลดรูป: {image_path}")

    # BGR → RGB
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Crop ขอบออก (ป้องกันพื้นหลังขาว/ดำ)
    h, w = rgb.shape[:2]
    margin_h = int(h * CROP_MARGIN_PCT)
    margin_w = int(w * CROP_MARGIN_PCT)
    cropped = rgb[margin_h:h - margin_h, margin_w:w - margin_w]

    return cropped


def extract_dominant_color(rgb_image: np.ndarray) -> tuple:
    """Extract dominant color via K-Means clustering → CIELAB.

    Returns (L, a, b, hex) of the dominant cluster.

    Methodology ref: Griffen et al. (2018), The Pudding.
    Used K-Means on swatch images to extract representative product colors.
    """
    pixels = rgb_image.reshape(-1, 3)

    # Convert to CIELAB
    lab_pixels = rgb_to_lab(pixels)

    # Filter extreme values (pure white/black background remnants)
    mask = (lab_pixels[:, 0] > 15) & (lab_pixels[:, 0] < 95)
    lab_filtered = lab_pixels[mask] if mask.sum() > 100 else lab_pixels

    # K-Means clustering
    n_clusters = min(N_CLUSTERS, len(lab_filtered))
    kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    kmeans.fit(lab_filtered)

    # Find dominant cluster (largest)
    labels = kmeans.labels_
    largest_idx = np.argmax(np.bincount(labels))
    dominant = kmeans.cluster_centers_[largest_idx]

    L, a, b = float(dominant[0]), float(dominant[1]), float(dominant[2])
    hex_color = lab_to_hex(L, a, b)

    return L, a, b, hex_color


# ═══════════════════════════════════════════════════════════════════════════════
# SQL Generation
# ═══════════════════════════════════════════════════════════════════════════════

def generate_sql(results: list) -> str:
    """Generate INSERT SQL from extraction results."""
    lines = []
    lines.append("-- ═══════════════════════════════════════════════════════════════")
    lines.append("-- Seed Data: product_color_shades")
    lines.append("-- สกัดสีจากรูป swatch ด้วย K-Means + CIELAB")
    lines.append("-- ")
    lines.append("-- Methodology:")
    lines.append("--   Griffen, A., Bailey, J., & Whaley, R. (2018).")
    lines.append('--   "Beauty Brawl", The Pudding.')
    lines.append("--   https://github.com/the-pudding/data/tree/master/makeup-shades")
    lines.append("-- ")
    lines.append("-- Color Science:")
    lines.append("--   sRGB → XYZ (D65) → CIELAB via colour-science 0.4.4")
    lines.append("--   Skin tone: ITA (Chardon et al., 1991)")
    lines.append("--   Undertone: Hue angle (Xiao et al., 2017)")
    lines.append("-- ═══════════════════════════════════════════════════════════════")
    lines.append("")

    current_product = None
    for r in results:
        if r["product_name"] != current_product:
            current_product = r["product_name"]
            lines.append(f"-- ── {current_product} ──")

        shade_name = r["shade_name"].replace("'", "''")
        shade_code = f"{r['tone']}_{r['undertone']}"
        hex_color = r["hex"]
        product_name = r["product_name"].replace("'", "''")

        lines.append(
            f"INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)"
            f"\n  SELECT product_id, '{shade_name}', '{shade_code}', '{hex_color}'"
            f"\n  FROM products WHERE name='{product_name}' LIMIT 1;"
        )

    lines.append("")
    lines.append(f"-- Total: {len(results)} shades extracted")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    if not SWATCHES_DIR.exists():
        print(f"❌ ไม่พบโฟลเดอร์ swatches: {SWATCHES_DIR}")
        print(f"   สร้างโฟลเดอร์และใส่รูป swatch ตามโครงสร้าง:")
        print(f"   {SWATCHES_DIR}/")
        for folder in PRODUCT_MAP:
            print(f"   ├── {folder}/")
            print(f"   │   ├── shade-name-1.jpg")
            print(f"   │   └── shade-name-2.jpg")
        sys.exit(1)

    results = []
    total_images = 0
    skipped = 0

    for folder_name, product_name in PRODUCT_MAP.items():
        folder_path = SWATCHES_DIR / folder_name
        if not folder_path.exists():
            print(f"⚠️  ข้าม {folder_name}/ — ไม่พบโฟลเดอร์")
            continue

        # หารูปทุกนามสกุล
        image_files = sorted(
            f for f in folder_path.iterdir()
            if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")
        )

        if not image_files:
            print(f"⚠️  ข้าม {folder_name}/ — ไม่มีรูป")
            continue

        print(f"\n🎨 {product_name} ({len(image_files)} shades)")

        for img_path in image_files:
            total_images += 1
            shade_name = img_path.stem.replace("-", " ").replace("_", " ").title()

            try:
                rgb_image = load_and_crop(str(img_path))
                L, a, b, hex_color = extract_dominant_color(rgb_image)
                tone = classify_tone(L, b)
                undertone = classify_undertone(a, b)

                results.append({
                    "product_name": product_name,
                    "shade_name": shade_name,
                    "tone": tone,
                    "undertone": undertone,
                    "hex": hex_color,
                    "L": round(L, 2),
                    "a": round(a, 2),
                    "b": round(b, 2),
                })

                print(f"   ✅ {shade_name:30s} {hex_color}  L={L:.1f} a={a:.1f} b={b:.1f}  → {tone}/{undertone}")

            except Exception as e:
                print(f"   ❌ {shade_name}: {e}")
                skipped += 1

    if not results:
        print("\n❌ ไม่มีรูป swatch ให้สกัดสี")
        print("   ใส่รูปใน swatches/ แล้วรันใหม่")
        sys.exit(1)

    # Generate SQL
    sql = generate_sql(results)
    OUTPUT_SQL.write_text(sql, encoding="utf-8")
    print(f"\n{'═' * 60}")
    print(f"  สกัดสำเร็จ : {len(results)} shades")
    print(f"  ข้าม       : {skipped}")
    print(f"  SQL output : {OUTPUT_SQL}")
    print(f"{'═' * 60}")

    # Print summary table
    print("\n📊 สรุปตาม Personal Color Season:")
    from collections import Counter
    tone_counts = Counter(r["tone"] for r in results)
    ut_counts = Counter(r["undertone"] for r in results)
    print(f"   Skin Tone  : {dict(tone_counts)}")
    print(f"   Undertone  : {dict(ut_counts)}")


if __name__ == "__main__":
    main()
