-- ═══════════════════════════════════════════════
-- Seed Data: สินค้าเครื่องสำอางจริง สำหรับ AuraMatch
-- แหล่งอ้างอิง: Shopee, Watsons, Sephora, Beautrium (เม.ย. 2026)
-- ═══════════════════════════════════════════════

-- ── Brands ──
INSERT INTO brands (name, logo_url, website_url, description) VALUES
('Maybelline', NULL, 'https://www.maybelline.co.th', 'แบรนด์เครื่องสำอางจากอเมริกา'),
('MAC', NULL, 'https://www.maccosmetics.co.th', 'แบรนด์เครื่องสำอางระดับพรีเมียม'),
('Romand', NULL, 'https://romandbeauty.com', 'แบรนด์เครื่องสำอางเกาหลี'),
('Canmake', NULL, 'https://www.canmake.com', 'แบรนด์เครื่องสำอางจากญี่ปุ่น'),
('3CE', NULL, 'https://3ce.com', 'แบรนด์เครื่องสำอางเกาหลี by STYLENANDA'),
('Mistine', NULL, 'https://www.mistine.co.th', 'แบรนด์เครื่องสำอางไทย')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- ── ลิปสติก (category_id = 1) ──
-- แหล่งอ้างอิง: https://www.maybelline.co.th , https://shopee.co.th , https://www.sephora.co.th

INSERT INTO products (name, brand_id, category_id, price, image_url, description, commission_rate) VALUES
-- Maybelline Super Stay Vinyl Ink (ราคา ~299 บาท, อ้างอิง: maybelline.co.th, watsons.co.th)
('Maybelline Super Stay Vinyl Ink Lipstick',
 (SELECT brand_id FROM brands WHERE name='Maybelline' LIMIT 1),
 1, 299.00,
 'https://www.maybelline.co.th/-/media/project/loreal/brand-sites/mny/apac/th/products/lip/lip-color/superstay-vinyl-ink/packshot/maybelline-super-stay-vinyl-ink-702x702.jpg',
 'ลิปจิ้มจุ่มเนื้อไวนิล ติดทน 16 ชม. สีสดชัด เงาฉ่ำ', 5.00),

-- MAC Matte Lipstick (ราคา ~1,050 บาท, อ้างอิง: sephora.co.th, central.co.th)
('MAC M·A·Cximal Silky Matte Lipstick',
 (SELECT brand_id FROM brands WHERE name='MAC' LIMIT 1),
 1, 1050.00,
 'https://www.sephora.co.th/dw/image/v2/BKZF_PRD/on/demandware.static/-/Sites-masterCatalog_MAC/default/dw1df81ec8/images/original/MACXIMAL_SILKY_MATTE_LIPSTICK_633.jpg',
 'ลิปสติกเนื้อแมทท์ซิลกี้ สีชัด เนียนนุ่ม ติดทนนาน', 5.00),

-- Romand Juicy Lasting Tint (ราคา ~350 บาท, อ้างอิง: shopee.co.th, beautrium.com)
('Romand Juicy Lasting Tint',
 (SELECT brand_id FROM brands WHERE name='Romand' LIMIT 1),
 1, 350.00,
 'https://romandbeauty.com/cdn/shop/files/25NEWTINT_PRODUCT_01_1024x.png',
 'ลิปทินท์เนื้อฉ่ำ สีสดใส ติดทนยาวนาน จากเกาหลี', 5.00),

-- 3CE Velvet Lip Tint (ราคา ~590 บาท, อ้างอิง: shopee.co.th, 3ce.com)
('3CE Velvet Lip Tint',
 (SELECT brand_id FROM brands WHERE name='3CE' LIMIT 1),
 1, 590.00,
 'https://3ce.com/cdn/shop/files/3CE_VELVET_LIP_TINT_PDP_01_1024x.png',
 'ลิปทินท์เนื้อเวลเว็ท เนียนนุ่ม สีสวยติดทน', 5.00);


-- ── บลัชออน (category_id = 3) ──
-- แหล่งอ้างอิง: https://shopee.co.th , https://www.watsons.co.th

INSERT INTO products (name, brand_id, category_id, price, image_url, description, commission_rate) VALUES
-- Canmake Cream Cheek (ราคา ~280 บาท, อ้างอิง: watsons.co.th)
('Canmake Cream Cheek',
 (SELECT brand_id FROM brands WHERE name='Canmake' LIMIT 1),
 3, 280.00,
 'https://www.watsons.co.th/medias/BP-311274-1.jpg?context=bWFzdGVyfGltYWdlc3w',
 'ครีมบลัชเนื้อเนียน สีสวยธรรมชาติ ราคาย่อมเยา', 5.00),

-- Canmake Powder Cheeks (ราคา ~280 บาท, อ้างอิง: watsons.co.th, shopee.co.th)
('Canmake Powder Cheeks',
 (SELECT brand_id FROM brands WHERE name='Canmake' LIMIT 1),
 3, 280.00,
 'https://www.watsons.co.th/medias/BP-304932-1.jpg?context=bWFzdGVyfGltYWdlc3w',
 'บลัชออนเนื้อฝุ่น สีสวยละมุน ปัดง่าย ติดทน', 5.00),

-- Romand Better Than Cheek (ราคา ~350 บาท, อ้างอิง: shopee.co.th, beautrium.com)
('Romand Better Than Cheek',
 (SELECT brand_id FROM brands WHERE name='Romand' LIMIT 1),
 3, 350.00,
 'https://romandbeauty.com/cdn/shop/products/romand-better-than-cheek_1024x.png',
 'บลัชเนื้อแมทท์ เม็ดสีแน่น สีสวยติดทนทั้งวัน', 5.00),

-- Mistine Blush (ราคา ~169 บาท, อ้างอิง: shopee.co.th, mistine.co.th)
('Mistine Matte Complete Blush',
 (SELECT brand_id FROM brands WHERE name='Mistine' LIMIT 1),
 3, 169.00,
 'https://www.mistine.co.th/uploads/product/product-thumb-1024x1024.jpg',
 'บลัชเนื้อแมทท์จากไทย สีสวย ราคาเข้าถึงง่าย', 5.00);


-- ── อายแชโดว์ (category_id = 4) ──
-- แหล่งอ้างอิง: https://shopee.co.th , https://thebeautrium.com , https://www.sephora.co.th

INSERT INTO products (name, brand_id, category_id, price, image_url, description, commission_rate) VALUES
-- 3CE Multi Eye Color Palette (ราคา ~1,250 บาท, อ้างอิง: shopee.co.th, beautrium.com)
('3CE Multi Eye Color Palette',
 (SELECT brand_id FROM brands WHERE name='3CE' LIMIT 1),
 4, 1250.00,
 'https://3ce.com/cdn/shop/files/3CE_MULTI_EYE_COLOR_PALETTE_PDP_01_1024x.png',
 'พาเลทอายแชโดว์ 9 สี เนื้อนุ่ม เม็ดสีชัด เบลนด์ง่าย', 5.00),

-- Romand Better Than Palette (ราคา ~690 บาท, อ้างอิง: shopee.co.th, beautrium.com)
('Romand Better Than Palette',
 (SELECT brand_id FROM brands WHERE name='Romand' LIMIT 1),
 4, 690.00,
 'https://romandbeauty.com/cdn/shop/products/romand-better-than-palette_1024x.png',
 'พาเลทอายแชโดว์ 10 สี มีทั้งแมทท์ ชิมเมอร์ กลิตเตอร์', 5.00),

-- Maybelline The Nudes Palette (ราคา ~499 บาท, อ้างอิง: shopee.co.th, watsons.co.th)
('Maybelline The Nudes Eyeshadow Palette',
 (SELECT brand_id FROM brands WHERE name='Maybelline' LIMIT 1),
 4, 499.00,
 'https://www.maybelline.co.th/-/media/project/loreal/brand-sites/mny/apac/th/products/eye/eye-shadow/the-nudes-palette/packshot/maybelline-the-nudes-702x702.jpg',
 'พาเลทอายแชโดว์ 12 สี โทน nude เหมาะใช้ได้ทุกวัน', 5.00),

-- Canmake Perfect Stylist Eyes (ราคา ~350 บาท, อ้างอิง: watsons.co.th)
('Canmake Perfect Stylist Eyes',
 (SELECT brand_id FROM brands WHERE name='Canmake' LIMIT 1),
 4, 350.00,
 'https://www.watsons.co.th/medias/BP-275837-1.jpg?context=bWFzdGVyfGltYWdlc3w',
 'พาเลทอายแชโดว์ 5 สี จากญี่ปุ่น ขนาดพกพา', 5.00);


-- ── ไฮไลท์ (category_id = 5) ──
-- แหล่งอ้างอิง: https://www.watsons.co.th , https://shopee.co.th

INSERT INTO products (name, brand_id, category_id, price, image_url, description, commission_rate) VALUES
-- Canmake Munyutto Highlighter (ราคา ~300 บาท, อ้างอิง: watsons.co.th)
('Canmake Munyutto Highlighter',
 (SELECT brand_id FROM brands WHERE name='Canmake' LIMIT 1),
 5, 300.00,
 'https://www.watsons.co.th/medias/BP-304932-1.jpg?context=bWFzdGVyfGltYWdlc3w',
 'ไฮไลท์เนื้อเจลลี่ เนียนนุ่ม หน้าฉ่ำเล่นแสง ติดทนทั้งวัน', 5.00),

-- Canmake Glow Fleur Highlighter (ราคา ~380 บาท, อ้างอิง: watsons.co.th)
('Canmake Glow Fleur Highlighter',
 (SELECT brand_id FROM brands WHERE name='Canmake' LIMIT 1),
 5, 380.00,
 'https://www.watsons.co.th/medias/BP-265107-1.jpg?context=bWFzdGVyfGltYWdlc3w',
 'ไฮไลท์เนื้อฝุ่น ผสมชิมเมอร์ละเอียด หน้าวิ้ง', 5.00),

-- Mistine Wings Extra Cover Highlighter (ราคา ~179 บาท, อ้างอิง: shopee.co.th)
('Mistine Wings Extra Cover Highlighter',
 (SELECT brand_id FROM brands WHERE name='Mistine' LIMIT 1),
 5, 179.00,
 'https://www.mistine.co.th/uploads/product/product-thumb-1024x1024.jpg',
 'ไฮไลท์จากแบรนด์ไทย ราคาย่อมเยา ใช้ง่าย', 5.00);


-- ── เพิ่ม Product Links (Shopee) ──
-- ลิปสติก
INSERT INTO product_links (product_id, platform, url)
SELECT product_id, 'shopee', 'https://shopee.co.th/search?keyword=maybelline+vinyl+ink'
FROM products WHERE name='Maybelline Super Stay Vinyl Ink Lipstick' LIMIT 1;

INSERT INTO product_links (product_id, platform, url)
SELECT product_id, 'shopee', 'https://shopee.co.th/search?keyword=mac+matte+lipstick'
FROM products WHERE name='MAC M·A·Cximal Silky Matte Lipstick' LIMIT 1;

INSERT INTO product_links (product_id, platform, url)
SELECT product_id, 'shopee', 'https://shopee.co.th/search?keyword=romand+juicy+lasting+tint'
FROM products WHERE name='Romand Juicy Lasting Tint' LIMIT 1;

INSERT INTO product_links (product_id, platform, url)
SELECT product_id, 'shopee', 'https://shopee.co.th/search?keyword=3ce+velvet+lip+tint'
FROM products WHERE name='3CE Velvet Lip Tint' LIMIT 1;

-- บลัชออน
INSERT INTO product_links (product_id, platform, url)
SELECT product_id, 'shopee', 'https://shopee.co.th/search?keyword=canmake+cream+cheek'
FROM products WHERE name='Canmake Cream Cheek' LIMIT 1;

INSERT INTO product_links (product_id, platform, url)
SELECT product_id, 'shopee', 'https://shopee.co.th/search?keyword=canmake+powder+cheeks'
FROM products WHERE name='Canmake Powder Cheeks' LIMIT 1;

INSERT INTO product_links (product_id, platform, url)
SELECT product_id, 'shopee', 'https://shopee.co.th/search?keyword=romand+better+than+cheek'
FROM products WHERE name='Romand Better Than Cheek' LIMIT 1;

INSERT INTO product_links (product_id, platform, url)
SELECT product_id, 'shopee', 'https://shopee.co.th/search?keyword=mistine+blush'
FROM products WHERE name='Mistine Matte Complete Blush' LIMIT 1;

-- อายแชโดว์
INSERT INTO product_links (product_id, platform, url)
SELECT product_id, 'shopee', 'https://shopee.co.th/search?keyword=3ce+multi+eye+color+palette'
FROM products WHERE name='3CE Multi Eye Color Palette' LIMIT 1;

INSERT INTO product_links (product_id, platform, url)
SELECT product_id, 'shopee', 'https://shopee.co.th/search?keyword=romand+better+than+palette'
FROM products WHERE name='Romand Better Than Palette' LIMIT 1;

INSERT INTO product_links (product_id, platform, url)
SELECT product_id, 'shopee', 'https://shopee.co.th/search?keyword=maybelline+the+nudes+palette'
FROM products WHERE name='Maybelline The Nudes Eyeshadow Palette' LIMIT 1;

INSERT INTO product_links (product_id, platform, url)
SELECT product_id, 'shopee', 'https://shopee.co.th/search?keyword=canmake+perfect+stylist+eyes'
FROM products WHERE name='Canmake Perfect Stylist Eyes' LIMIT 1;

-- ไฮไลท์
INSERT INTO product_links (product_id, platform, url)
SELECT product_id, 'shopee', 'https://shopee.co.th/search?keyword=canmake+munyutto+highlighter'
FROM products WHERE name='Canmake Munyutto Highlighter' LIMIT 1;

INSERT INTO product_links (product_id, platform, url)
SELECT product_id, 'shopee', 'https://shopee.co.th/search?keyword=canmake+glow+fleur+highlighter'
FROM products WHERE name='Canmake Glow Fleur Highlighter' LIMIT 1;

INSERT INTO product_links (product_id, platform, url)
SELECT product_id, 'shopee', 'https://shopee.co.th/search?keyword=mistine+highlighter'
FROM products WHERE name='Mistine Wings Extra Cover Highlighter' LIMIT 1;
