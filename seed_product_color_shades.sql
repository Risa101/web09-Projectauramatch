-- ═══════════════════════════════════════════════════════════════
-- Seed Data: product_color_shades
-- สกัดสีจากรูป swatch ด้วย K-Means + CIELAB
-- 
-- Methodology:
--   Griffen, A., Bailey, J., & Whaley, R. (2018).
--   "Beauty Brawl", The Pudding.
--   https://github.com/the-pudding/data/tree/master/makeup-shades
-- 
-- Color Science:
--   sRGB → XYZ (D65) → CIELAB via colour-science 0.4.4
--   Skin tone: ITA (Chardon et al., 1991)
--   Undertone: Hue angle (Xiao et al., 2017)
-- ═══════════════════════════════════════════════════════════════

-- ── Maybelline Super Stay Vinyl Ink Lipstick ──
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Charmed', 'fair_neutral', '#E8C6B3'
  FROM products WHERE name='Maybelline Super Stay Vinyl Ink Lipstick' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Coy', 'fair_neutral', '#EAC5B4'
  FROM products WHERE name='Maybelline Super Stay Vinyl Ink Lipstick' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Peachy', 'fair_neutral', '#E5BDAB'
  FROM products WHERE name='Maybelline Super Stay Vinyl Ink Lipstick' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Unrivaled', 'fair_neutral', '#E9C3AF'
  FROM products WHERE name='Maybelline Super Stay Vinyl Ink Lipstick' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Wicked', 'fair_cool', '#EBC5B6'
  FROM products WHERE name='Maybelline Super Stay Vinyl Ink Lipstick' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Witty', 'fair_neutral', '#E3BDAB'
  FROM products WHERE name='Maybelline Super Stay Vinyl Ink Lipstick' LIMIT 1;
-- ── MAC M·A·Cximal Silky Matte Lipstick ──
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Diva', 'fair_neutral', '#DCB39D'
  FROM products WHERE name='MAC M·A·Cximal Silky Matte Lipstick' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Lady Danger', 'fair_neutral', '#E3B8A4'
  FROM products WHERE name='MAC M·A·Cximal Silky Matte Lipstick' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Marrakesh', 'fair_neutral', '#EAC4B2'
  FROM products WHERE name='MAC M·A·Cximal Silky Matte Lipstick' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Mehr', 'fair_neutral', '#EAE5E1'
  FROM products WHERE name='MAC M·A·Cximal Silky Matte Lipstick' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Ruby Woo', 'fair_cool', '#E1BCAD'
  FROM products WHERE name='MAC M·A·Cximal Silky Matte Lipstick' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Velvet Teddy', 'tan_cool', '#DB746A'
  FROM products WHERE name='MAC M·A·Cximal Silky Matte Lipstick' LIMIT 1;
-- ── Romand Juicy Lasting Tint ──
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Apple Brown', 'dark_cool', '#D85D41'
  FROM products WHERE name='Romand Juicy Lasting Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Bare Grape', 'fair_cool', '#CF9FA3'
  FROM products WHERE name='Romand Juicy Lasting Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Cherry Bomb', 'deep_cool', '#7D1724'
  FROM products WHERE name='Romand Juicy Lasting Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Jujube', 'dark_cool', '#C74644'
  FROM products WHERE name='Romand Juicy Lasting Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Nucadamia', 'fair_cool', '#D9ACA6'
  FROM products WHERE name='Romand Juicy Lasting Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Plum Coke', 'deep_cool', '#591022'
  FROM products WHERE name='Romand Juicy Lasting Tint' LIMIT 1;
-- ── 3CE Velvet Lip Tint ──
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Best Ever', 'fair_cool', '#FABBAD'
  FROM products WHERE name='3CE Velvet Lip Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Childlike', 'light_cool', '#B18D86'
  FROM products WHERE name='3CE Velvet Lip Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Childlike', 'dark_cool', '#F6210B'
  FROM products WHERE name='3CE Velvet Lip Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Daffodil', 'dark_cool', '#CD5E56'
  FROM products WHERE name='3CE Velvet Lip Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Go Now', 'fair_cool', '#F9C7BB'
  FROM products WHERE name='3CE Velvet Lip Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Going Right', 'fair_cool', '#F9C6B9'
  FROM products WHERE name='3CE Velvet Lip Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Know Better', 'fair_cool', '#EEC7BB'
  FROM products WHERE name='3CE Velvet Lip Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Near And Dear', 'medium_cool', '#EF7E74'
  FROM products WHERE name='3CE Velvet Lip Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'New Nude', 'tan_cool', '#E9735A'
  FROM products WHERE name='3CE Velvet Lip Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Overview', 'fair_cool', '#DEAEA9'
  FROM products WHERE name='3CE Velvet Lip Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Persistence', 'fair_warm', '#E1D8DF'
  FROM products WHERE name='3CE Velvet Lip Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Persistence', 'fair_cool', '#F9C5B9'
  FROM products WHERE name='3CE Velvet Lip Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Pink Break', 'fair_cool', '#F9C7BA'
  FROM products WHERE name='3CE Velvet Lip Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Private', 'fair_cool', '#F9BCAE'
  FROM products WHERE name='3CE Velvet Lip Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Save Me', 'fair_cool', '#FAC0B2'
  FROM products WHERE name='3CE Velvet Lip Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Swatch Closeup', 'fair_warm', '#C5C4C2'
  FROM products WHERE name='3CE Velvet Lip Tint' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Taupe', 'dark_cool', '#A02A13'
  FROM products WHERE name='3CE Velvet Lip Tint' LIMIT 1;
-- ── Canmake Cream Cheek ──
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '05 Sweet Apricot', 'tan_cool', '#EB7665'
  FROM products WHERE name='Canmake Cream Cheek' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '07 Coral Orange', 'medium_cool', '#EB7372'
  FROM products WHERE name='Canmake Cream Cheek' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '14 Apple Cream Red', 'tan_cool', '#E74D55'
  FROM products WHERE name='Canmake Cream Cheek' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '16 Almond Terracotta', 'dark_cool', '#C06051'
  FROM products WHERE name='Canmake Cream Cheek' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '19 Cinnamon Milk Tea', 'tan_neutral', '#AD7F65'
  FROM products WHERE name='Canmake Cream Cheek' LIMIT 1;
-- ── Canmake Powder Cheeks ──
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'P01 Powerful Pink', 'fair_cool', '#E69396'
  FROM products WHERE name='Canmake Powder Cheeks' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'P02 Little Shy Pink', 'fair_cool', '#F4BDC8'
  FROM products WHERE name='Canmake Powder Cheeks' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'P03 Cheerful Peach', 'fair_cool', '#F4BBAA'
  FROM products WHERE name='Canmake Powder Cheeks' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'P04 Clever Beige', 'fair_cool', '#F5C0BB'
  FROM products WHERE name='Canmake Powder Cheeks' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'P05 Classy Mauve Pink', 'fair_cool', '#D99AA7'
  FROM products WHERE name='Canmake Powder Cheeks' LIMIT 1;
-- ── Romand Better Than Cheek ──
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Blueberry Chip', 'fair_cool', '#F2B8C0'
  FROM products WHERE name='Romand Better Than Cheek' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Lychee Chip', 'fair_cool', '#E48D98'
  FROM products WHERE name='Romand Better Than Cheek' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Mango Chip', 'tan_cool', '#EA8455'
  FROM products WHERE name='Romand Better Than Cheek' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Nutty Nude', 'light_neutral', '#E5B69A'
  FROM products WHERE name='Romand Better Than Cheek' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Peach Chip', 'light_neutral', '#F7BA9F'
  FROM products WHERE name='Romand Better Than Cheek' LIMIT 1;
-- ── Mistine Matte Complete Blush ──
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '01 Sand Smooth', 'light_cool', '#F5988F'
  FROM products WHERE name='Mistine Matte Complete Blush' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '02 Hot Peach', 'fair_cool', '#F59298'
  FROM products WHERE name='Mistine Matte Complete Blush' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '03 Sweet Candy', 'light_cool', '#F17C82'
  FROM products WHERE name='Mistine Matte Complete Blush' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '04 Hot Pink', 'dark_cool', '#D15152'
  FROM products WHERE name='Mistine Matte Complete Blush' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '05 Caramel Sweet', 'light_cool', '#F1A18B'
  FROM products WHERE name='Mistine Matte Complete Blush' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '06 Pink Coral', 'light_cool', '#F09585'
  FROM products WHERE name='Mistine Matte Complete Blush' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '07 Orange Coral', 'medium_cool', '#EF8C79'
  FROM products WHERE name='Mistine Matte Complete Blush' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '08 Orange Brick', 'dark_cool', '#C85E4C'
  FROM products WHERE name='Mistine Matte Complete Blush' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '09 Pure Peach', 'tan_cool', '#DA6A58'
  FROM products WHERE name='Mistine Matte Complete Blush' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '10 Tanned Red', 'dark_cool', '#A8523F'
  FROM products WHERE name='Mistine Matte Complete Blush' LIMIT 1;
-- ── 3CE Multi Eye Color Palette ──
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Beach Muse', 'light_cool', '#D58A80'
  FROM products WHERE name='3CE Multi Eye Color Palette' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Dry Bouquet All9', 'fair_warm', '#E0DEDB'
  FROM products WHERE name='3CE Multi Eye Color Palette' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Dry Bouquet Bot3', 'fair_cool', '#D79FA1'
  FROM products WHERE name='3CE Multi Eye Color Palette' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Dry Bouquet Mid3', 'fair_cool', '#DDD6D4'
  FROM products WHERE name='3CE Multi Eye Color Palette' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Dry Bouquet Palette', 'medium_cool', '#D78F70'
  FROM products WHERE name='3CE Multi Eye Color Palette' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Dry Bouquet Swatch1', 'fair_neutral', '#F0DACF'
  FROM products WHERE name='3CE Multi Eye Color Palette' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Dry Bouquet Swatch2', 'fair_warm', '#7F8693'
  FROM products WHERE name='3CE Multi Eye Color Palette' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Dry Bouquet Swatches', 'fair_cool', '#E09C9B'
  FROM products WHERE name='3CE Multi Eye Color Palette' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Dry Bouquet Top3', 'fair_neutral', '#DEDBD9'
  FROM products WHERE name='3CE Multi Eye Color Palette' LIMIT 1;
-- ── Romand Better Than Palette ──
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Dusty Fog Garden', 'fair_cool', '#A7958E'
  FROM products WHERE name='Romand Better Than Palette' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Mahogany Garden', 'dark_neutral', '#9B6B51'
  FROM products WHERE name='Romand Better Than Palette' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Pampas Garden', 'medium_cool', '#D9907B'
  FROM products WHERE name='Romand Better Than Palette' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Peony Nude Garden', 'fair_cool', '#E5D7D4'
  FROM products WHERE name='Romand Better Than Palette' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Rosebud Garden', 'fair_cool', '#D59E95'
  FROM products WHERE name='Romand Better Than Palette' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Shade Shadow Garden', 'fair_neutral', '#C8AB9C'
  FROM products WHERE name='Romand Better Than Palette' LIMIT 1;
-- ── Maybelline The Nudes Eyeshadow Palette ──
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Cool Quad', 'fair_neutral', '#C0AD9F'
  FROM products WHERE name='Maybelline The Nudes Eyeshadow Palette' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Neutral Quad', 'dark_warm', '#8C6F57'
  FROM products WHERE name='Maybelline The Nudes Eyeshadow Palette' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Palette', 'deep_warm', '#3F4142'
  FROM products WHERE name='Maybelline The Nudes Eyeshadow Palette' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Warm Quad', 'fair_warm', '#EBDFCC'
  FROM products WHERE name='Maybelline The Nudes Eyeshadow Palette' LIMIT 1;
-- ── Canmake Perfect Stylist Eyes ──
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '05 Pinky Chocolat', 'deep_cool', '#8E5C65'
  FROM products WHERE name='Canmake Perfect Stylist Eyes' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '14 Antique Ruby', 'deep_cool', '#8C6366'
  FROM products WHERE name='Canmake Perfect Stylist Eyes' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '23 Almond Canele', 'deep_cool', '#8E5D65'
  FROM products WHERE name='Canmake Perfect Stylist Eyes' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '25 Mimosa Orange', 'deep_cool', '#895A5E'
  FROM products WHERE name='Canmake Perfect Stylist Eyes' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '26 Mirage Mauve', 'deep_cool', '#8F5E67'
  FROM products WHERE name='Canmake Perfect Stylist Eyes' LIMIT 1;
-- ── Canmake Munyutto Highlighter ──
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '01 Moonlight Gem', 'fair_neutral', '#F8DECD'
  FROM products WHERE name='Canmake Munyutto Highlighter' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '02 Rose Quartz', 'fair_cool', '#F6D3CB'
  FROM products WHERE name='Canmake Munyutto Highlighter' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '03 Warm Rutile', 'fair_neutral', '#F3D7C5'
  FROM products WHERE name='Canmake Munyutto Highlighter' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '04 Blue Topaz', 'fair_warm', '#E7ECF2'
  FROM products WHERE name='Canmake Munyutto Highlighter' LIMIT 1;
-- ── Canmake Glow Fleur Highlighter ──
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '01 Planet Light Detail', 'fair_cool', '#E4E4E4'
  FROM products WHERE name='Canmake Glow Fleur Highlighter' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '01 Planet Light', 'fair_warm', '#E0DFE2'
  FROM products WHERE name='Canmake Glow Fleur Highlighter' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '02 Illuminate Blog', 'fair_neutral', '#A5A3A2'
  FROM products WHERE name='Canmake Glow Fleur Highlighter' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '02 Swatch Blog', 'fair_neutral', '#ADA9A6'
  FROM products WHERE name='Canmake Glow Fleur Highlighter' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Glow Fleur Highlighter', 'fair_warm', '#E1E0E1'
  FROM products WHERE name='Canmake Glow Fleur Highlighter' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Swatch Detail1', 'fair_neutral', '#E4DEDC'
  FROM products WHERE name='Canmake Glow Fleur Highlighter' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Swatch Detail2', 'light_warm', '#FAD19E'
  FROM products WHERE name='Canmake Glow Fleur Highlighter' LIMIT 1;
-- ── Maybelline Fit Me Matte + Poreless Foundation ──
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '115 128 Ivory Warm Nude', 'light_neutral', '#D3AF95'
  FROM products WHERE name='Maybelline Fit Me Matte + Poreless Foundation' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '230 310 Natural Buff Sun Beige', 'light_warm', '#C6A88C'
  FROM products WHERE name='Maybelline Fit Me Matte + Poreless Foundation' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '322 330 Warm Honey Toffee', 'medium_neutral', '#BD9576'
  FROM products WHERE name='Maybelline Fit Me Matte + Poreless Foundation' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'All 24 Shades', 'medium_warm', '#E0AD83'
  FROM products WHERE name='Maybelline Fit Me Matte + Poreless Foundation' LIMIT 1;
-- ── MAC Studio Fix Fluid SPF 15 Foundation ──
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'All Shades', 'tan_neutral', '#AA7D5E'
  FROM products WHERE name='MAC Studio Fix Fluid SPF 15 Foundation' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'All Swatches', 'dark_cool', '#9A6D5E'
  FROM products WHERE name='MAC Studio Fix Fluid SPF 15 Foundation' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'C8 Nc45 Swatch', 'tan_warm', '#AB8A6D'
  FROM products WHERE name='MAC Studio Fix Fluid SPF 15 Foundation' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'C8 Nc45', 'deep_neutral', '#75685F'
  FROM products WHERE name='MAC Studio Fix Fluid SPF 15 Foundation' LIMIT 1;
-- ── Canmake Marshmallow Finish Powder ──
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '01 Dearest Bouquet', 'fair_warm', '#E2D8CE'
  FROM products WHERE name='Canmake Marshmallow Finish Powder' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '02 Sakura Tulle', 'fair_cool', '#F2CBCF'
  FROM products WHERE name='Canmake Marshmallow Finish Powder' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, '03 Plumeria Wreath', 'fair_neutral', '#E0C4B4'
  FROM products WHERE name='Canmake Marshmallow Finish Powder' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Mb Matte Beige', 'light_warm', '#E7BF9E'
  FROM products WHERE name='Canmake Marshmallow Finish Powder' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Mi Matte Ivory Ochre', 'fair_neutral', '#FCDED0'
  FROM products WHERE name='Canmake Marshmallow Finish Powder' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Ml Matte Light Ocher', 'fair_neutral', '#FAD6C3'
  FROM products WHERE name='Canmake Marshmallow Finish Powder' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Mo Matte Ocher', 'fair_neutral', '#FACBB0'
  FROM products WHERE name='Canmake Marshmallow Finish Powder' LIMIT 1;
-- ── Mistine Wings Extra Cover Super Powder ──
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'Overview', 'fair_warm', '#F6DCC8'
  FROM products WHERE name='Mistine Wings Extra Cover Super Powder' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'S1 Ivory White', 'deep_warm', '#434144'
  FROM products WHERE name='Mistine Wings Extra Cover Super Powder' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'S1', 'fair_warm', '#FBE6D4'
  FROM products WHERE name='Mistine Wings Extra Cover Super Powder' LIMIT 1;
INSERT INTO product_color_shades (product_id, shade_name, shade_code, hex_color)
  SELECT product_id, 'S2', 'fair_warm', '#FBE7D3'
  FROM products WHERE name='Mistine Wings Extra Cover Super Powder' LIMIT 1;

-- Total: 114 shades extracted