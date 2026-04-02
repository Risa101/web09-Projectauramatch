"""
Script import ข้อมูล Cosmetic Foundation Shades เข้า MySQL
ใช้ไฟล์ที่ดาวน์โหลดไว้แล้วใน /Users/saridbutchuang/Downloads/archive

วิธีรัน:
  cd backendauramatchnewversion
  python scripts/import_makeup_data.py
"""

import pandas as pd
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

ARCHIVE_PATH = "/Users/saridbutchuang/Downloads/archive"

# ── Database Connection ──────────────────────────────
conn = pymysql.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "auramatchnewversion"),
    charset="utf8mb4"
)
cursor = conn.cursor()
print("✅ Connected to database")

# ── Load allShades.csv (มี hex, lightness ครบ) ──────
df = pd.read_csv(f"{ARCHIVE_PATH}/allShades.csv")
print(f"📦 allShades.csv: {df.shape[0]} rows, columns: {df.columns.tolist()}")
print(df.head(2))

# ── ฟังก์ชันแปลง lightness → skin_tone ─────────────
def lightness_to_skin_tone(lightness):
    if pd.isna(lightness):
        return 'medium'
    l = float(lightness)
    if l >= 0.85:  return 'fair'
    elif l >= 0.70: return 'light'
    elif l >= 0.55: return 'medium'
    elif l >= 0.40: return 'tan'
    elif l >= 0.25: return 'dark'
    else:           return 'deep'

# ── ฟังก์ชันแปลง hue → undertone ────────────────────
def hue_to_undertone(hue):
    if pd.isna(hue):
        return 'neutral'
    h = float(hue)
    if 15 <= h <= 45:  return 'warm'
    elif h <= 15 or h >= 330: return 'warm'
    elif 180 <= h <= 270: return 'cool'
    else: return 'neutral'

# ── Ensure category exists ───────────────────────────
cursor.execute("SELECT category_id FROM product_categories WHERE name = 'รองพื้น'")
row = cursor.fetchone()
if row:
    cat_id = row[0]
else:
    cursor.execute("INSERT INTO product_categories (name) VALUES ('รองพื้น')")
    conn.commit()
    cat_id = cursor.lastrowid
print(f"📂 Category 'รองพื้น' id = {cat_id}")

# ── Import ───────────────────────────────────────────
brand_map   = {}
product_map = {}
count_brands   = 0
count_products = 0
count_shades   = 0

total = len(df)
for i, row in df.iterrows():
    brand_name   = str(row.get('brand',   '')).strip()
    product_name = str(row.get('product', '')).strip()
    shade_name   = str(row.get('name',    '')).strip()
    hex_color    = str(row.get('hex',     '')).strip()
    url          = str(row.get('url',     '')).strip()
    lightness    = row.get('lightness', None)
    hue          = row.get('hue', None)
    description  = str(row.get('description', '')).strip()

    if not brand_name or not product_name or brand_name == 'nan':
        continue

    # ── Brand ──
    if brand_name not in brand_map:
        cursor.execute("SELECT brand_id FROM brands WHERE name = %s", (brand_name,))
        r = cursor.fetchone()
        if r:
            brand_map[brand_name] = r[0]
        else:
            cursor.execute("INSERT INTO brands (name) VALUES (%s)", (brand_name,))
            conn.commit()
            brand_map[brand_name] = cursor.lastrowid
            count_brands += 1

    brand_id = brand_map[brand_name]

    # ── Product ──
    product_key = f"{brand_name}|{product_name}"
    if product_key not in product_map:
        cursor.execute(
            "SELECT product_id FROM products WHERE name = %s AND brand_id = %s",
            (product_name, brand_id)
        )
        r = cursor.fetchone()
        if r:
            product_map[product_key] = r[0]
        else:
            cursor.execute(
                "INSERT INTO products (brand_id, category_id, name, is_active) VALUES (%s,%s,%s,1)",
                (brand_id, cat_id, product_name)
            )
            conn.commit()
            pid = cursor.lastrowid
            product_map[product_key] = pid
            count_products += 1

            # Link (Sephora/Ulta URL)
            if url and url != 'nan':
                platform = 'shopee'
                if 'sephora' in url: platform = 'shopee'
                elif 'ulta' in url:  platform = 'lazada'
                cursor.execute(
                    "INSERT INTO product_links (product_id, platform, url) VALUES (%s,%s,%s)",
                    (pid, platform, url)
                )
                conn.commit()

    product_id = product_map[product_key]

    # ── Shade ──
    if hex_color and hex_color != 'nan':
        if not hex_color.startswith('#'):
            hex_color = '#' + hex_color
        skin_tone  = lightness_to_skin_tone(lightness)
        undertone  = hue_to_undertone(hue)

        cursor.execute(
            """INSERT INTO product_color_shades
               (product_id, shade_name, shade_code, hex_color, is_active)
               VALUES (%s,%s,%s,%s,1)""",
            (product_id, shade_name[:100] if shade_name != 'nan' else hex_color,
             skin_tone + '_' + undertone, hex_color[:7])
        )
        conn.commit()
        count_shades += 1

    if (i+1) % 500 == 0:
        print(f"  ... {i+1}/{total} rows processed")

print(f"\n✅ Import เสร็จแล้ว!")
print(f"   Brands   : {count_brands}")
print(f"   Products : {count_products}")
print(f"   Shades   : {count_shades}")

cursor.close()
conn.close()
