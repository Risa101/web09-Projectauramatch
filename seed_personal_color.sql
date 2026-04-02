-- เพิ่ม column personal_color
ALTER TABLE products ADD COLUMN personal_color VARCHAR(50) NULL AFTER image_url;

-- ═══════════════════════════════════════════
-- ใส่ข้อมูล Personal Color ให้สินค้า
-- อ้างอิงทฤษฎี Personal Color Analysis:
-- Spring = โทนอุ่นสว่าง (ส้ม, พีช, ทอง, ชมพูอุ่น)
-- Summer = โทนเย็นนุ่ม (ชมพูอ่อน, ม่วงอ่อน, โรส, เทา)
-- Autumn = โทนอุ่นเข้ม (แดงอิฐ, น้ำตาล, ส้มเข้ม, เบอร์รี่)
-- Winter = โทนเย็นสด (แดงสด, ม่วงเข้ม, น้ำเงิน, ดำ)
-- ═══════════════════════════════════════════

-- ลิปสติก
UPDATE products SET personal_color = 'spring,autumn' WHERE name LIKE '%Vinyl Ink%';
UPDATE products SET personal_color = 'winter,autumn' WHERE name LIKE '%Silky Matte%';
UPDATE products SET personal_color = 'spring,summer' WHERE name LIKE '%Juicy Lasting%';
UPDATE products SET personal_color = 'summer,winter' WHERE name LIKE '%Velvet Lip%';

-- บลัชออน
UPDATE products SET personal_color = 'summer,spring' WHERE name = 'Canmake Cream Cheek';
UPDATE products SET personal_color = 'spring,summer' WHERE name = 'Canmake Powder Cheeks';
UPDATE products SET personal_color = 'autumn,winter' WHERE name = 'Romand Better Than Cheek';
UPDATE products SET personal_color = 'spring,summer,autumn,winter' WHERE name LIKE '%Mistine%Blush%';

-- อายแชโดว์
UPDATE products SET personal_color = 'summer,winter' WHERE name LIKE '%3CE Multi Eye%';
UPDATE products SET personal_color = 'spring,autumn' WHERE name LIKE '%Romand Better Than Palette%';
UPDATE products SET personal_color = 'spring,summer,autumn,winter' WHERE name LIKE '%Nudes%Palette%';
UPDATE products SET personal_color = 'summer,spring' WHERE name LIKE '%Perfect Stylist%';

-- ไฮไลท์
UPDATE products SET personal_color = 'summer,winter' WHERE name LIKE '%Munyutto%';
UPDATE products SET personal_color = 'spring,autumn' WHERE name LIKE '%Glow Fleur%';
UPDATE products SET personal_color = 'spring,summer,autumn,winter' WHERE name LIKE '%Mistine%Highlighter%';

-- สินค้าที่ยังไม่มี personal_color → ใส่ทุก season (เหมาะทุกคน)
UPDATE products SET personal_color = 'spring,summer,autumn,winter' WHERE personal_color IS NULL AND is_active = 1;
