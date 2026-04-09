-- ═══════════════════════════════════════════════
-- Seed Data: product_concerns (สินค้า ↔ ปัญหาผิว)
-- Maps products to the skin concerns they address.
-- Concern IDs: 1=สิว, 2=ผิวแห้ง, 3=ผิวมัน, 4=ผิวแพ้ง่าย, 5=ริ้วรอย, 6=ฝ้า/กระ
-- ═══════════════════════════════════════════════

-- ลิปสติก: ผิวแพ้ง่าย (สูตรอ่อนโยน), ผิวแห้ง (ให้ความชุ่มชื้น)
INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 4 FROM products p WHERE p.name='Maybelline Super Stay Vinyl Ink Lipstick' LIMIT 1;
INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 2 FROM products p WHERE p.name='Maybelline Super Stay Vinyl Ink Lipstick' LIMIT 1;

INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 2 FROM products p WHERE p.name='MAC M·A·Cximal Silky Matte Lipstick' LIMIT 1;

INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 2 FROM products p WHERE p.name='Romand Juicy Lasting Tint' LIMIT 1;
INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 4 FROM products p WHERE p.name='Romand Juicy Lasting Tint' LIMIT 1;

INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 2 FROM products p WHERE p.name='3CE Velvet Lip Tint' LIMIT 1;

-- บลัชออน: ผิวมัน (คุมมัน), ผิวแพ้ง่าย, สิว
INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 4 FROM products p WHERE p.name='Canmake Cream Cheek' LIMIT 1;
INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 2 FROM products p WHERE p.name='Canmake Cream Cheek' LIMIT 1;

INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 3 FROM products p WHERE p.name='Canmake Powder Cheeks' LIMIT 1;
INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 1 FROM products p WHERE p.name='Canmake Powder Cheeks' LIMIT 1;

INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 3 FROM products p WHERE p.name='Romand Better Than Cheek' LIMIT 1;

INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 3 FROM products p WHERE p.name='Mistine Matte Complete Blush' LIMIT 1;
INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 1 FROM products p WHERE p.name='Mistine Matte Complete Blush' LIMIT 1;

-- อายแชโดว์: ผิวแพ้ง่าย, ผิวมัน
INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 4 FROM products p WHERE p.name='3CE Multi Eye Color Palette' LIMIT 1;

INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 4 FROM products p WHERE p.name='Romand Better Than Palette' LIMIT 1;
INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 3 FROM products p WHERE p.name='Romand Better Than Palette' LIMIT 1;

INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 3 FROM products p WHERE p.name='Maybelline The Nudes Eyeshadow Palette' LIMIT 1;

INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 4 FROM products p WHERE p.name='Canmake Perfect Stylist Eyes' LIMIT 1;
INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 2 FROM products p WHERE p.name='Canmake Perfect Stylist Eyes' LIMIT 1;

-- ไฮไลท์: ผิวแห้ง (ให้ความชุ่มชื้น), ริ้วรอย (เนื้อบางเบา), ฝ้า/กระ
INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 2 FROM products p WHERE p.name='Canmake Munyutto Highlighter' LIMIT 1;
INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 5 FROM products p WHERE p.name='Canmake Munyutto Highlighter' LIMIT 1;

INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 6 FROM products p WHERE p.name='Canmake Glow Fleur Highlighter' LIMIT 1;

INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 2 FROM products p WHERE p.name='Mistine Wings Extra Cover Highlighter' LIMIT 1;
INSERT INTO product_concerns (product_id, concern_id)
SELECT p.product_id, 6 FROM products p WHERE p.name='Mistine Wings Extra Cover Highlighter' LIMIT 1;

