"""
ดาวน์โหลดรูป swatch จากเว็บ official/retailer

รูปจะถูกบันทึกใน swatches/{product-folder}/{shade-name}.jpg
สำหรับใช้กับ extract_product_colors.py

แหล่งรูป:
- Maybelline Official: maybelline.co.th, maybelline.com
- MAC Official: maccosmetics.com
- Romand Official: romandbeauty.com
- 3CE Official: 3cecosmetics.com
- Canmake Official: canmake.com
- Shopee/Watsons Thailand (product images)

⚠️  หมายเหตุ:
- URL รูปอาจเปลี่ยนแปลงได้ตามเว็บ retailer
- ถ้า URL ใดดาวน์โหลดไม่ได้ script จะข้ามและแจ้งเตือน
- สามารถเพิ่ม/แก้ไข URL ได้ใน SWATCH_URLS dict
- หรือจะใส่รูปเองใน swatches/ โฟลเดอร์ก็ได้ (ไม่ต้องรัน script นี้)

วิธีรัน:
    cd backendauramatchnewversion
    python scripts/download_swatches.py
"""

import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
import ssl
import time

SWATCHES_DIR = Path(__file__).parent.parent / "swatches"

# ═══════════════════════════════════════════════════════════════════════════════
# Swatch URLs — อ้างอิงจากเว็บ official / retailer
#
# ⚠️ URL เหล่านี้เป็นลิงก์ตรงจากเว็บ retailer ณ วันที่สร้าง (เม.ย. 2026)
#    อาจเปลี่ยนแปลงได้ — ถ้าดาวน์โหลดไม่ได้ ให้:
#    1. เข้าเว็บ retailer ด้วยตนเอง
#    2. คลิกขวารูป swatch → Copy Image Address
#    3. แก้ URL ใน dict นี้ หรือดาวน์โหลดรูปใส่โฟลเดอร์ swatches/ เอง
# ═══════════════════════════════════════════════════════════════════════════════

SWATCH_URLS = {
    # ──────────────────────────────────────────────
    # ลิปสติก
    # ──────────────────────────────────────────────
    "maybelline-vinyl-ink": {
        # แหล่ง: maybelline.com product page swatch images
        # ⚠️ ถ้า URL ไม่ทำงาน → ค้นหา "Maybelline Vinyl Ink [shade] swatch"
        #    แล้วดาวน์โหลดรูปใส่โฟลเดอร์เอง
    },
    "mac-matte": {
        # แหล่ง: maccosmetics.com product page
    },
    "romand-juicy-lasting": {
        # แหล่ง: romandbeauty.com product page
    },
    "3ce-velvet-lip": {
        # แหล่ง: 3cecosmetics.com product page
    },

    # ──────────────────────────────────────────────
    # บลัชออน
    # ──────────────────────────────────────────────
    "canmake-cream-cheek": {},
    "canmake-powder-cheeks": {},
    "romand-better-than-cheek": {},
    "mistine-blush": {},

    # ──────────────────────────────────────────────
    # อายแชโดว์
    # ──────────────────────────────────────────────
    "3ce-multi-eye": {},
    "romand-better-than-palette": {},
    "maybelline-the-nudes": {},
    "canmake-perfect-stylist": {},

    # ──────────────────────────────────────────────
    # ไฮไลท์
    # ──────────────────────────────────────────────
    "canmake-munyutto": {},
    "canmake-glow-fleur": {},
    "mistine-highlighter": {},

    # ──────────────────────────────────────────────
    # รองพื้น
    # ──────────────────────────────────────────────
    "maybelline-fit-me": {},
    "mac-studio-fix": {},
    "canmake-marshmallow": {},
    "mistine-wings-powder": {},
}


def download_image(url: str, save_path: Path, timeout: int = 15) -> bool:
    """Download image from URL → save to local path."""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        })

        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            data = resp.read()

        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_bytes(data)
        return True

    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        print(f"   ❌ ดาวน์โหลดไม่ได้: {e}")
        return False


def main():
    print("═" * 60)
    print("  AuraMatch — ดาวน์โหลดรูป swatch เครื่องสำอาง")
    print("═" * 60)

    SWATCHES_DIR.mkdir(parents=True, exist_ok=True)

    total = 0
    success = 0
    failed = 0
    empty_folders = []

    for folder_name, shades in SWATCH_URLS.items():
        folder_path = SWATCHES_DIR / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)

        if not shades:
            empty_folders.append(folder_name)
            continue

        print(f"\n📦 {folder_name}/")

        for shade_name, url in shades.items():
            total += 1
            ext = ".jpg"
            if ".png" in url.lower():
                ext = ".png"
            elif ".webp" in url.lower():
                ext = ".webp"

            save_path = folder_path / f"{shade_name}{ext}"

            if save_path.exists():
                print(f"   ⏭️  {shade_name} — มีอยู่แล้ว")
                success += 1
                continue

            print(f"   ⬇️  {shade_name}...", end=" ", flush=True)
            if download_image(url, save_path):
                size_kb = save_path.stat().st_size / 1024
                print(f"✅ ({size_kb:.0f} KB)")
                success += 1
            else:
                failed += 1

            time.sleep(0.5)  # rate limiting

    print(f"\n{'═' * 60}")
    print(f"  ดาวน์โหลดสำเร็จ : {success}/{total}")
    if failed:
        print(f"  ล้มเหลว         : {failed}")
    print(f"  โฟลเดอร์ทั้งหมด : {SWATCHES_DIR}")
    print(f"{'═' * 60}")

    if empty_folders:
        print(f"\n⚠️  โฟลเดอร์ต่อไปนี้ยังไม่มี URL — ต้องหารูป swatch เอง:")
        for f in empty_folders:
            print(f"   📁 swatches/{f}/")
        print()
        print("   วิธีหารูป swatch:")
        print("   1. เข้าเว็บ official ของแบรนด์ (เช่น romandbeauty.com)")
        print("   2. ไปหน้าสินค้า → คลิกเลือกเฉดสี")
        print("   3. คลิกขวาที่รูป swatch → Save Image As")
        print("   4. ตั้งชื่อไฟล์เป็นชื่อเฉดสี เช่น ruby-woo.jpg")
        print("   5. ใส่ในโฟลเดอร์ที่ถูกต้อง")
        print()
        print("   หรือ screenshot จากหน้าเว็บแล้ว crop เฉพาะส่วน swatch")
        print()
        print(f"   หลังใส่รูปครบ → รัน: python scripts/extract_product_colors.py")


if __name__ == "__main__":
    main()
