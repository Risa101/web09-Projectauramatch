"""
สร้างข้อมูล seed สำหรับ demo:
  1. users ทดสอบ (1 admin + 2 users)
  2. recommendation_rules จาก product_color_shades ที่มีอยู่จริง

วิธีรัน:
  cd backendauramatchnewversion
  python scripts/seed_data.py
"""

import pymysql
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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


# ═══════════════════════════════════════════════════════════════════════════════
# 1. สร้าง Users ทดสอบ
# ═══════════════════════════════════════════════════════════════════════════════
print("\n👤 สร้าง Users ทดสอบ ...")

test_users = [
    ("admin",    "admin@auramatch.com",   "admin123",  "admin"),
    ("testuser", "user@auramatch.com",    "user123",   "user"),
    ("demo",     "demo@auramatch.com",    "demo123",   "user"),
]

for username, email, password, role in test_users:
    cursor.execute("SELECT user_id FROM users WHERE email=%s", (email,))
    if cursor.fetchone():
        print(f"   ⏭️  {username} มีอยู่แล้ว ข้าม")
        continue

    hashed = pwd_context.hash(password)
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, role) VALUES (%s,%s,%s,%s)",
        (username, email, hashed, role),
    )
    user_id = cursor.lastrowid

    # สร้าง user_profile ด้วย
    cursor.execute(
        "INSERT INTO user_profiles (user_id, display_name) VALUES (%s,%s)",
        (user_id, username),
    )
    conn.commit()
    print(f"   ✅ {username} ({email}) role={role}  password={password}")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. สร้าง Recommendation Rules จาก product_color_shades
# ═══════════════════════════════════════════════════════════════════════════════
print("\n📋 สร้าง Recommendation Rules ...")

# เช็คว่ามี rules อยู่แล้วหรือยัง
cursor.execute("SELECT COUNT(*) FROM recommendation_rules")
existing_rules = cursor.fetchone()[0]
if existing_rules > 0:
    print(f"   ⏭️  มี {existing_rules} rules อยู่แล้ว ข้าม")
else:
    # ดึง product ทั้งหมดที่มี shades
    # นับจำนวน shade ของแต่ละ product ตาม skin_tone + undertone
    cursor.execute("""
        SELECT
            p.product_id,
            SUBSTRING_INDEX(pcs.shade_code, '_', 1)  AS tone,
            SUBSTRING_INDEX(pcs.shade_code, '_', -1)  AS undertone,
            COUNT(*) AS shade_count
        FROM products p
        JOIN product_color_shades pcs ON p.product_id = pcs.product_id
        WHERE pcs.shade_code IS NOT NULL
          AND pcs.shade_code LIKE '%\\_%'
        GROUP BY p.product_id, tone, undertone
        ORDER BY p.product_id, shade_count DESC
    """)
    shade_data = cursor.fetchall()
    print(f"   📊 พบ {len(shade_data)} ชุดข้อมูล shade")

    # skin_tone values ที่ valid
    valid_tones = {"fair", "light", "medium", "tan", "dark", "deep"}
    valid_undertones = {"warm", "cool", "neutral"}

    # tone → personal_color mapping
    tone_to_season = {
        ("fair", "cool"):    "summer",
        ("fair", "warm"):    "spring",
        ("fair", "neutral"): "summer",
        ("light", "cool"):   "summer",
        ("light", "warm"):   "spring",
        ("light", "neutral"): "spring",
        ("medium", "cool"):  "summer",
        ("medium", "warm"):  "autumn",
        ("medium", "neutral"): "autumn",
        ("tan", "cool"):     "winter",
        ("tan", "warm"):     "autumn",
        ("tan", "neutral"):  "autumn",
        ("dark", "cool"):    "winter",
        ("dark", "warm"):    "autumn",
        ("dark", "neutral"): "winter",
        ("deep", "cool"):    "winter",
        ("deep", "warm"):    "autumn",
        ("deep", "neutral"): "winter",
    }

    rule_count = 0
    for product_id, tone, undertone, shade_count in shade_data:
        tone = tone.strip().lower()
        undertone = undertone.strip().lower()

        if tone not in valid_tones or undertone not in valid_undertones:
            continue

        # priority ตามจำนวน shades ที่ตรง (ยิ่งมีเฉดสีให้เลือกเยอะยิ่งดี)
        priority = min(shade_count, 10)

        # หา personal_color ที่เหมาะ
        season = tone_to_season.get((tone, undertone), "any")

        cursor.execute(
            """INSERT INTO recommendation_rules
               (product_id, face_shape, skin_tone, skin_undertone,
                personal_color, gender, ethnicity, priority)
               VALUES (%s, 'any', %s, %s, %s, 'any', 'any', %s)""",
            (product_id, tone, undertone, season, priority),
        )
        rule_count += 1

    conn.commit()
    print(f"   ✅ สร้าง {rule_count} rules เรียบร้อย")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. เพิ่ม best_colors / avoid_colors ใน color_palettes
# ═══════════════════════════════════════════════════════════════════════════════
print("\n🎨 อัปเดต Color Palettes ...")

palette_data = {
    "spring": {
        "best_colors":  '["#FF6B6B","#FFA07A","#FFD700","#98FB98","#87CEEB","#FFDAB9","#FF69B4","#F0E68C","#DDA0DD","#FFB347"]',
        "avoid_colors": '["#000000","#808080","#4B0082","#191970","#800000"]',
    },
    "summer": {
        "best_colors":  '["#E6E6FA","#B0C4DE","#DDA0DD","#FFB6C1","#C0C0C0","#778899","#BC8F8F","#D8BFD8","#AFEEEE","#F5DEB3"]',
        "avoid_colors": '["#FF4500","#FF8C00","#FFD700","#8B4513","#000000"]',
    },
    "autumn": {
        "best_colors":  '["#D2691E","#CD853F","#DAA520","#808000","#556B2F","#8B4513","#A0522D","#BC8F8F","#F4A460","#B8860B"]',
        "avoid_colors": '["#FF69B4","#E6E6FA","#00BFFF","#C0C0C0","#F0F8FF"]',
    },
    "winter": {
        "best_colors":  '["#FF0000","#0000FF","#FF00FF","#000000","#FFFFFF","#00FF00","#4B0082","#DC143C","#191970","#C0C0C0"]',
        "avoid_colors": '["#F5DEB3","#FFDAB9","#DEB887","#D2B48C","#FFD700"]',
    },
}

for season, colors in palette_data.items():
    cursor.execute(
        """UPDATE color_palettes
           SET best_colors = %s, avoid_colors = %s
           WHERE season = %s""",
        (colors["best_colors"], colors["avoid_colors"], season),
    )

conn.commit()
print("   ✅ อัปเดต best_colors / avoid_colors ครบ 4 seasons")


# ═══════════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════")
cursor.execute("SELECT COUNT(*) FROM users")
print(f"  users               : {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM user_profiles")
print(f"  user_profiles       : {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM recommendation_rules")
print(f"  recommendation_rules: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM color_palettes WHERE best_colors IS NOT NULL")
print(f"  color_palettes (มีสี): {cursor.fetchone()[0]}")
print("══════════════════════════════════════")
print("✅ Seed data เสร็จแล้ว!")
print()
print("🔑 บัญชีทดสอบ:")
print("   Admin : admin@auramatch.com / admin123")
print("   User  : user@auramatch.com  / user123")
print("   Demo  : demo@auramatch.com  / demo123")

cursor.close()
conn.close()
