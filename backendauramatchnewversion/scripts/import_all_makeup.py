"""
Import ข้อมูลเครื่องสำอางทั้งหมดเข้า MySQL จาก 5 ไฟล์ใน /Downloads/archive

ไฟล์ที่ import:
  allShades.csv     – foundation shades + hex + hue + lightness  (6,816 rows)
  allCategories.csv – foundation shades + hex + lightness         (5,307 rows)
  allNumbers.csv    – foundation shades + hex + lightness         (3,117 rows)
  sephora.csv       – Sephora products (ไม่มี hex)                (4,371 rows)
  ulta.csv          – ULTA products    (ไม่มี hex)                (4,004 rows)

วิธีรัน:
  cd backendauramatchnewversion
  python scripts/import_all_makeup.py
"""

import pandas as pd
import pymysql
from dotenv import load_dotenv
import os
import math

load_dotenv()

ARCHIVE = "/Users/saridbutchuang/Downloads/archive"

conn = pymysql.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "auramatchnewversion"),
    charset="utf8mb4",
    unix_socket="/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock",
)
cursor = conn.cursor()
print("✅ Connected to database")

# ── Helper: category id cache ──────────────────────────────────────────────────
_cat_cache: dict = {}

def get_or_create_category(name: str) -> int:
    if name in _cat_cache:
        return _cat_cache[name]
    cursor.execute("SELECT category_id FROM product_categories WHERE name=%s", (name,))
    row = cursor.fetchone()
    if row:
        _cat_cache[name] = row[0]
    else:
        cursor.execute("INSERT INTO product_categories (name) VALUES (%s)", (name,))
        conn.commit()
        _cat_cache[name] = cursor.lastrowid
    return _cat_cache[name]


# ── Helper: brand cache ────────────────────────────────────────────────────────
_brand_cache: dict = {}

def get_or_create_brand(name: str) -> int:
    if name in _brand_cache:
        return _brand_cache[name]
    cursor.execute("SELECT brand_id FROM brands WHERE name=%s", (name,))
    row = cursor.fetchone()
    if row:
        _brand_cache[name] = row[0]
    else:
        cursor.execute("INSERT INTO brands (name) VALUES (%s)", (name,))
        conn.commit()
        _brand_cache[name] = cursor.lastrowid
    return _brand_cache[name]


# ── Helper: product cache ──────────────────────────────────────────────────────
_product_cache: dict = {}

def get_or_create_product(brand_id: int, brand_name: str, product_name: str, cat_id: int) -> int:
    key = f"{brand_id}|{product_name}"
    if key in _product_cache:
        return _product_cache[key]
    cursor.execute(
        "SELECT product_id FROM products WHERE brand_id=%s AND name=%s",
        (brand_id, product_name),
    )
    row = cursor.fetchone()
    if row:
        _product_cache[key] = row[0]
    else:
        cursor.execute(
            "INSERT INTO products (brand_id, category_id, name, is_active) VALUES (%s,%s,%s,1)",
            (brand_id, cat_id, product_name),
        )
        conn.commit()
        _product_cache[key] = cursor.lastrowid
    return _product_cache[key]


def add_link(product_id: int, url: str):
    if not url or str(url).strip() in ("", "nan"):
        return
    url = str(url).strip()
    if "sephora" in url:
        platform = "sephora"
    elif "ulta" in url:
        platform = "ulta"
    elif "shopee" in url:
        platform = "shopee"
    elif "lazada" in url:
        platform = "lazada"
    else:
        platform = "other"
    cursor.execute(
        "SELECT link_id FROM product_links WHERE product_id=%s AND platform=%s",
        (product_id, platform),
    )
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO product_links (product_id, platform, url) VALUES (%s,%s,%s)",
            (product_id, platform, url[:500]),
        )
        conn.commit()


def nan_str(v) -> str:
    s = str(v).strip()
    return "" if s == "nan" else s


def safe_float(v):
    try:
        f = float(v)
        return None if math.isnan(f) else f
    except Exception:
        return None


# ── lightness → skin_tone ─────────────────────────────────────────────────────
def lightness_to_tone(l) -> str:
    v = safe_float(l)
    if v is None:
        return "medium"
    if v >= 0.85:   return "fair"
    elif v >= 0.70: return "light"
    elif v >= 0.55: return "medium"
    elif v >= 0.40: return "tan"
    elif v >= 0.25: return "dark"
    else:           return "deep"


# ── hue → undertone ───────────────────────────────────────────────────────────
def hue_to_undertone(h) -> str:
    v = safe_float(h)
    if v is None:
        return "neutral"
    if 15 <= v <= 45 or v <= 15 or v >= 330:
        return "warm"
    elif 180 <= v <= 270:
        return "cool"
    return "neutral"


def add_shade(product_id: int, shade_name: str, hex_color: str, shade_code: str):
    if not hex_color or hex_color == "nan":
        return
    if not hex_color.startswith("#"):
        hex_color = "#" + hex_color
    hex_color = hex_color[:7]
    label = (shade_name[:100] if shade_name and shade_name != "nan" else hex_color)
    cursor.execute(
        """INSERT INTO product_color_shades
           (product_id, shade_name, shade_code, hex_color, is_active)
           VALUES (%s,%s,%s,%s,1)""",
        (product_id, label, shade_code[:50], hex_color),
    )
    conn.commit()


# ═══════════════════════════════════════════════════════════════════════════════
# 1. allShades.csv  (มี hue, sat, lightness, hex)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n📦 [1/5] allShades.csv ...")
df = pd.read_csv(f"{ARCHIVE}/allShades.csv")
cat_id = get_or_create_category("รองพื้น")
count = 0
for _, row in df.iterrows():
    brand = nan_str(row.get("brand", ""))
    product = nan_str(row.get("product", ""))
    if not brand or not product:
        continue
    bid = get_or_create_brand(brand)
    pid = get_or_create_product(bid, brand, product, cat_id)
    add_link(pid, row.get("url", ""))
    tone = lightness_to_tone(row.get("lightness"))
    under = hue_to_undertone(row.get("hue"))
    shade_name = nan_str(row.get("name", ""))
    add_shade(pid, shade_name, nan_str(row.get("hex", "")), f"{tone}_{under}")
    count += 1
print(f"   ✅ {count} shades imported")

# ═══════════════════════════════════════════════════════════════════════════════
# 2. allCategories.csv  (มี hex, lightness, categories)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n📦 [2/5] allCategories.csv ...")
df = pd.read_csv(f"{ARCHIVE}/allCategories.csv")
count = 0
for _, row in df.iterrows():
    brand = nan_str(row.get("brand", ""))
    product = nan_str(row.get("product", ""))
    if not brand or not product:
        continue
    # ตั้ง category จาก 'categories' column ถ้ามี
    cat_name = nan_str(row.get("categories", "")) or "รองพื้น"
    cid = get_or_create_category(cat_name)
    bid = get_or_create_brand(brand)
    pid = get_or_create_product(bid, brand, product, cid)
    add_link(pid, row.get("url", ""))
    tone = lightness_to_tone(row.get("lightness"))
    # allCategories ไม่มี hue ใช้ specific/name เป็น hint
    specific = nan_str(row.get("specific", "")).lower()
    if any(k in specific for k in ["w", "warm", "gold", "peach", "beige"]):
        under = "warm"
    elif any(k in specific for k in ["n", "cool", "pink", "rose"]):
        under = "cool"
    else:
        under = "neutral"
    shade_name = nan_str(row.get("name", ""))
    add_shade(pid, shade_name, nan_str(row.get("hex", "")), f"{tone}_{under}")
    count += 1
print(f"   ✅ {count} shades imported")

# ═══════════════════════════════════════════════════════════════════════════════
# 3. allNumbers.csv  (มี hex, lightness)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n📦 [3/5] allNumbers.csv ...")
df = pd.read_csv(f"{ARCHIVE}/allNumbers.csv")
cat_id = get_or_create_category("รองพื้น")
count = 0
for _, row in df.iterrows():
    brand = nan_str(row.get("brand", ""))
    product = nan_str(row.get("product", ""))
    if not brand or not product:
        continue
    bid = get_or_create_brand(brand)
    pid = get_or_create_product(bid, brand, product, cat_id)
    tone = lightness_to_tone(row.get("lightness"))
    specific = nan_str(row.get("specific", "")).lower()
    if any(k in specific for k in ["w", "warm", "gold", "n", "neutral"]):
        under = "warm"
    elif any(k in specific for k in ["c", "cool", "pink"]):
        under = "cool"
    else:
        under = "neutral"
    shade_name = nan_str(row.get("name", ""))
    add_shade(pid, shade_name, nan_str(row.get("hex", "")), f"{tone}_{under}")
    count += 1
print(f"   ✅ {count} shades imported")

# ═══════════════════════════════════════════════════════════════════════════════
# 4. sephora.csv  (ไม่มี hex — import เป็น product + link)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n📦 [4/5] sephora.csv ...")
df = pd.read_csv(f"{ARCHIVE}/sephora.csv")
cat_id = get_or_create_category("รองพื้น")
count = 0
for _, row in df.iterrows():
    brand = nan_str(row.get("brand", ""))
    product = nan_str(row.get("product", ""))
    if not brand or not product:
        continue
    bid = get_or_create_brand(brand)
    pid = get_or_create_product(bid, brand, product, cat_id)
    add_link(pid, row.get("url", ""))
    count += 1
print(f"   ✅ {count} products imported")

# ═══════════════════════════════════════════════════════════════════════════════
# 5. ulta.csv  (ไม่มี hex — import เป็น product + link)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n📦 [5/5] ulta.csv ...")
df = pd.read_csv(f"{ARCHIVE}/ulta.csv")
cat_id = get_or_create_category("รองพื้น")
count = 0
for _, row in df.iterrows():
    brand = nan_str(row.get("brand", ""))
    product = nan_str(row.get("product", ""))
    if not brand or not product:
        continue
    bid = get_or_create_brand(brand)
    pid = get_or_create_product(bid, brand, product, cat_id)
    add_link(pid, row.get("url", ""))
    count += 1
print(f"   ✅ {count} products imported")

# ── Summary ───────────────────────────────────────────────────────────────────
cursor.execute("SELECT COUNT(*) FROM brands")
print(f"\n══════════════════════════════")
print(f"  brands              : {cursor.fetchone()[0]:,}")
cursor.execute("SELECT COUNT(*) FROM products")
print(f"  products            : {cursor.fetchone()[0]:,}")
cursor.execute("SELECT COUNT(*) FROM product_color_shades")
print(f"  product_color_shades: {cursor.fetchone()[0]:,}")
cursor.execute("SELECT COUNT(*) FROM product_links")
print(f"  product_links       : {cursor.fetchone()[0]:,}")
print(f"══════════════════════════════")
print("✅ Import ทั้งหมดเสร็จแล้ว!")

cursor.close()
conn.close()
