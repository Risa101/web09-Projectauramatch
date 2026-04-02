-- ============================================================
--  AuraMatch Database Schema
--  Web Application for Facial Structure and Personal Color
--  Analysis Using AI for Cosmetic Recommendation
-- ============================================================

CREATE DATABASE IF NOT EXISTS auramatchnewversion
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE auramatchnewversion;

-- ============================================================
-- GROUP 1: USER & AUTH (3 tables)
-- ============================================================

CREATE TABLE users (
    user_id       INT PRIMARY KEY AUTO_INCREMENT,
    username      VARCHAR(50)  UNIQUE NOT NULL,
    email         VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role          ENUM('admin','user') DEFAULT 'user',
    is_active     TINYINT(1) DEFAULT 1,
    created_at    DATETIME DEFAULT NOW()
);

CREATE TABLE user_profiles (
    profile_id   INT PRIMARY KEY AUTO_INCREMENT,
    user_id      INT UNIQUE NOT NULL,
    first_name   VARCHAR(100),
    last_name    VARCHAR(100),
    display_name VARCHAR(100),
    avatar_url   VARCHAR(255),
    birth_date   DATE,
    gender       ENUM('female','male','non_binary','prefer_not_to_say'),
    nationality  VARCHAR(100),
    bio          TEXT,
    updated_at   DATETIME DEFAULT NOW() ON UPDATE NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE password_resets (
    reset_id   INT PRIMARY KEY AUTO_INCREMENT,
    user_id    INT NOT NULL,
    token      VARCHAR(255) UNIQUE NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================
-- GROUP 2: AI ANALYSIS (3 tables)
-- ============================================================

CREATE TABLE color_palettes (
    palette_id  INT PRIMARY KEY AUTO_INCREMENT,
    season      ENUM('spring','summer','autumn','winter') NOT NULL,
    sub_type    VARCHAR(50),
    description TEXT,
    best_colors JSON,
    avoid_colors JSON,
    makeup_tips TEXT,
    created_at  DATETIME DEFAULT NOW()
);

CREATE TABLE analysis_results (
    analysis_id      INT PRIMARY KEY AUTO_INCREMENT,
    user_id          INT NOT NULL,
    image_path       VARCHAR(255),
    gender           ENUM('female','male','non_binary'),
    ethnicity        ENUM('asian','caucasian','african','latino',
                          'middle_eastern','south_asian','mixed','other'),
    nationality      VARCHAR(100),
    face_shape       ENUM('oval','round','square','heart',
                          'oblong','diamond','triangle'),
    skin_tone        ENUM('fair','light','medium','tan','dark','deep'),
    skin_undertone   ENUM('warm','cool','neutral'),
    personal_color   ENUM('spring','summer','autumn','winter'),
    palette_id       INT,
    confidence_score DECIMAL(5,2),
    created_at       DATETIME DEFAULT NOW(),
    FOREIGN KEY (user_id)    REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (palette_id) REFERENCES color_palettes(palette_id)
);

CREATE TABLE analysis_reviews (
    review_id   INT PRIMARY KEY AUTO_INCREMENT,
    analysis_id INT NOT NULL,
    user_id     INT NOT NULL,
    is_accurate TINYINT(1),
    comment     TEXT,
    created_at  DATETIME DEFAULT NOW(),
    FOREIGN KEY (analysis_id) REFERENCES analysis_results(analysis_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)     REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================
-- GROUP 3: SKIN CONCERNS (3 tables)
-- ============================================================

CREATE TABLE skin_concerns (
    concern_id  INT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    icon_url    VARCHAR(255)
);

CREATE TABLE user_skin_concerns (
    id         INT PRIMARY KEY AUTO_INCREMENT,
    user_id    INT NOT NULL,
    concern_id INT NOT NULL,
    severity   ENUM('mild','moderate','severe') DEFAULT 'mild',
    created_at DATETIME DEFAULT NOW(),
    FOREIGN KEY (user_id)    REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (concern_id) REFERENCES skin_concerns(concern_id)
);

CREATE TABLE product_concerns (
    id         INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    concern_id INT NOT NULL,
    FOREIGN KEY (concern_id) REFERENCES skin_concerns(concern_id)
);

-- ============================================================
-- GROUP 4: GEMINI AI (2 tables)
-- ============================================================

CREATE TABLE gemini_sessions (
    session_id  INT PRIMARY KEY AUTO_INCREMENT,
    user_id     INT NOT NULL,
    analysis_id INT,
    title       VARCHAR(200),
    created_at  DATETIME DEFAULT NOW(),
    FOREIGN KEY (user_id)     REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (analysis_id) REFERENCES analysis_results(analysis_id) ON DELETE SET NULL
);

CREATE TABLE gemini_messages (
    message_id   INT PRIMARY KEY AUTO_INCREMENT,
    session_id   INT NOT NULL,
    role         ENUM('user','model') NOT NULL,
    prompt       TEXT,
    response     TEXT,
    image_input  VARCHAR(255),
    image_output VARCHAR(255),
    created_at   DATETIME DEFAULT NOW(),
    FOREIGN KEY (session_id) REFERENCES gemini_sessions(session_id) ON DELETE CASCADE
);

-- ============================================================
-- GROUP 5: PHOTO EDITOR - Meitu Style (3 tables)
-- ============================================================

CREATE TABLE edit_filters (
    filter_id     INT PRIMARY KEY AUTO_INCREMENT,
    name          VARCHAR(100) NOT NULL,
    category      ENUM('beauty','color','light','vintage','makeup') NOT NULL,
    thumbnail_url VARCHAR(255),
    config        JSON,
    is_active     TINYINT(1) DEFAULT 1,
    created_at    DATETIME DEFAULT NOW()
);

CREATE TABLE edit_stickers (
    sticker_id INT PRIMARY KEY AUTO_INCREMENT,
    name       VARCHAR(100) NOT NULL,
    category   ENUM('face','decoration','text','emoji') NOT NULL,
    image_url  VARCHAR(255),
    is_active  TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT NOW()
);

CREATE TABLE photo_edits (
    edit_id        INT PRIMARY KEY AUTO_INCREMENT,
    user_id        INT NOT NULL,
    original_image VARCHAR(255),
    edited_image   VARCHAR(255),
    edit_config    JSON,
    source         ENUM('upload','analysis','gemini') DEFAULT 'upload',
    created_at     DATETIME DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================
-- GROUP 6: PRODUCT (7 tables)
-- ============================================================

CREATE TABLE brands (
    brand_id    INT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(100) NOT NULL,
    logo_url    VARCHAR(255),
    website_url VARCHAR(255),
    description TEXT,
    is_active   TINYINT(1) DEFAULT 1,
    created_at  DATETIME DEFAULT NOW()
);

CREATE TABLE product_categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    icon_url    VARCHAR(255)
);

CREATE TABLE products (
    product_id      INT PRIMARY KEY AUTO_INCREMENT,
    brand_id        INT,
    category_id     INT,
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    price           DECIMAL(10,2),
    image_url       VARCHAR(255),
    commission_rate DECIMAL(5,2) DEFAULT 0,
    is_active       TINYINT(1) DEFAULT 1,
    created_at      DATETIME DEFAULT NOW(),
    FOREIGN KEY (brand_id)    REFERENCES brands(brand_id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES product_categories(category_id) ON DELETE SET NULL
);

ALTER TABLE product_concerns
    ADD FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE;

CREATE TABLE product_links (
    link_id    INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    platform   ENUM('shopee','tiktok','lazada') NOT NULL,
    url        VARCHAR(500) NOT NULL,
    is_active  TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT NOW(),
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

CREATE TABLE product_tags (
    tag_id INT PRIMARY KEY AUTO_INCREMENT,
    name   VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE product_tag_map (
    id         INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    tag_id     INT NOT NULL,
    UNIQUE KEY uq_product_tag (product_id, tag_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id)     REFERENCES product_tags(tag_id) ON DELETE CASCADE
);

CREATE TABLE product_color_shades (
    shade_id   INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    shade_name VARCHAR(100),
    shade_code VARCHAR(20),
    hex_color  VARCHAR(7),
    image_url  VARCHAR(255),
    is_active  TINYINT(1) DEFAULT 1,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- ============================================================
-- GROUP 7: RECOMMENDATION (4 tables)
-- ============================================================

CREATE TABLE recommendation_rules (
    rule_id        INT PRIMARY KEY AUTO_INCREMENT,
    product_id     INT NOT NULL,
    face_shape     ENUM('oval','round','square','heart','oblong',
                        'diamond','triangle','any') DEFAULT 'any',
    skin_tone      ENUM('fair','light','medium','tan','dark','deep','any') DEFAULT 'any',
    skin_undertone ENUM('warm','cool','neutral','any') DEFAULT 'any',
    personal_color ENUM('spring','summer','autumn','winter','any') DEFAULT 'any',
    gender         ENUM('female','male','any') DEFAULT 'any',
    ethnicity      ENUM('asian','caucasian','african','latino',
                        'middle_eastern','south_asian','mixed','any') DEFAULT 'any',
    priority       INT DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

CREATE TABLE recommendations (
    recommendation_id INT PRIMARY KEY AUTO_INCREMENT,
    analysis_id       INT NOT NULL,
    product_id        INT NOT NULL,
    score             DECIMAL(5,2),
    created_at        DATETIME DEFAULT NOW(),
    FOREIGN KEY (analysis_id) REFERENCES analysis_results(analysis_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id)  REFERENCES products(product_id)
);

CREATE TABLE favorites (
    favorite_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id     INT NOT NULL,
    product_id  INT NOT NULL,
    created_at  DATETIME DEFAULT NOW(),
    UNIQUE KEY uq_favorite (user_id, product_id),
    FOREIGN KEY (user_id)    REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

CREATE TABLE recommendation_feedback (
    feedback_id       INT PRIMARY KEY AUTO_INCREMENT,
    recommendation_id INT NOT NULL,
    user_id           INT NOT NULL,
    rating            ENUM('like','dislike') NOT NULL,
    created_at        DATETIME DEFAULT NOW(),
    FOREIGN KEY (recommendation_id) REFERENCES recommendations(recommendation_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)           REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================
-- GROUP 8: REVIEW (2 tables)
-- ============================================================

CREATE TABLE product_reviews (
    review_id   INT PRIMARY KEY AUTO_INCREMENT,
    product_id  INT NOT NULL,
    user_id     INT NOT NULL,
    rating      TINYINT(1) NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment     TEXT,
    image_url   VARCHAR(255),
    platform    ENUM('shopee','tiktok','lazada','other'),
    is_verified TINYINT(1) DEFAULT 0,
    created_at  DATETIME DEFAULT NOW(),
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)    REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================
-- GROUP 9: COMMISSION & TRACKING (2 tables)
-- ============================================================

CREATE TABLE click_logs (
    log_id     INT PRIMARY KEY AUTO_INCREMENT,
    link_id    INT NOT NULL,
    user_id    INT,
    platform   ENUM('shopee','tiktok','lazada') NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    clicked_at DATETIME DEFAULT NOW(),
    FOREIGN KEY (link_id) REFERENCES product_links(link_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE TABLE commissions (
    commission_id INT PRIMARY KEY AUTO_INCREMENT,
    link_id       INT NOT NULL,
    user_id       INT,
    platform      ENUM('shopee','tiktok','lazada') NOT NULL,
    amount        DECIMAL(10,2),
    status        ENUM('pending','confirmed','paid') DEFAULT 'pending',
    clicked_at    DATETIME DEFAULT NOW(),
    FOREIGN KEY (link_id) REFERENCES product_links(link_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- ============================================================
-- GROUP 10: BLOG (2 tables)
-- ============================================================

CREATE TABLE blog_categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    created_at  DATETIME DEFAULT NOW()
);

CREATE TABLE blog_posts (
    post_id       INT PRIMARY KEY AUTO_INCREMENT,
    category_id   INT,
    author_id     INT NOT NULL,
    title         VARCHAR(200) NOT NULL,
    slug          VARCHAR(200) UNIQUE,
    content       LONGTEXT,
    thumbnail_url VARCHAR(255),
    views         INT DEFAULT 0,
    is_published  TINYINT(1) DEFAULT 0,
    published_at  DATETIME,
    created_at    DATETIME DEFAULT NOW(),
    updated_at    DATETIME DEFAULT NOW() ON UPDATE NOW(),
    FOREIGN KEY (category_id) REFERENCES blog_categories(category_id) ON DELETE SET NULL,
    FOREIGN KEY (author_id)   REFERENCES users(user_id)
);

-- ============================================================
-- GROUP 11: NOTIFICATION (1 table)
-- ============================================================

CREATE TABLE notifications (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id         INT NOT NULL,
    title           VARCHAR(200) NOT NULL,
    message         TEXT,
    type            ENUM('recommendation','promotion','system','review') DEFAULT 'system',
    is_read         TINYINT(1) DEFAULT 0,
    created_at      DATETIME DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================
-- GROUP 12: MARKETING (2 tables)
-- ============================================================

CREATE TABLE banners (
    banner_id  INT PRIMARY KEY AUTO_INCREMENT,
    title      VARCHAR(200),
    image_url  VARCHAR(255) NOT NULL,
    link_url   VARCHAR(500),
    position   ENUM('home_top','home_middle','sidebar') DEFAULT 'home_top',
    starts_at  DATETIME,
    ends_at    DATETIME,
    is_active  TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT NOW()
);

CREATE TABLE search_history (
    search_id  INT PRIMARY KEY AUTO_INCREMENT,
    user_id    INT,
    keyword    VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- ============================================================
-- GROUP 13: ADMIN (1 table)
-- ============================================================

CREATE TABLE admin_logs (
    log_id     INT PRIMARY KEY AUTO_INCREMENT,
    admin_id   INT NOT NULL,
    action     VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    record_id  INT,
    old_value  JSON,
    new_value  JSON,
    ip_address VARCHAR(45),
    created_at DATETIME DEFAULT NOW(),
    FOREIGN KEY (admin_id) REFERENCES users(user_id)
);

-- ============================================================
-- SAMPLE SEED DATA
-- ============================================================

-- Skin Concerns
INSERT INTO skin_concerns (name, description) VALUES
('สิว',         'ปัญหาสิวและรูขุมขน'),
('ผิวแห้ง',     'ผิวขาดความชุ่มชื้น'),
('ผิวมัน',      'ผิวมันเงา ควบคุมมันยาก'),
('ผิวแพ้ง่าย',  'ผิวบาง แพ้ง่าย แดง'),
('ริ้วรอย',     'ริ้วรอยและความหย่อนคล้อย'),
('ฝ้า/กระ',    'จุดด่างดำและฝ้า');

-- Product Categories
INSERT INTO product_categories (name) VALUES
('ลิปสติก'),
('รองพื้น'),
('บลัชออน'),
('อายแชโดว์'),
('ไฮไลท์'),
('คอนซีลเลอร์'),
('สกินแคร์');

-- Color Palettes
INSERT INTO color_palettes (season, sub_type, description, makeup_tips) VALUES
('spring',  'Bright Spring',  'สีสดใส อบอุ่น มีชีวิตชีวา',  'เลือกลิปสีคอรัล ส้ม พีช บลัชสีพีช'),
('summer',  'Soft Summer',    'สีนุ่มนวล เย็น พาสเทล',       'เลือกลิปสีชมพูม่วง บลัชสีกุหลาบ'),
('autumn',  'Deep Autumn',    'สีอบอุ่น เข้ม ดิน',           'เลือกลิปสีน้ำตาลแดง อิฐ บลัชสีทอง'),
('winter',  'True Winter',    'สีเข้ม คม ตัดกัน',            'เลือกลิปสีแดง เบอร์กันดี บลัชสีเย็น');

-- ============================================================
-- SUMMARY: 35 TABLES TOTAL
-- ============================================================
-- Group 1  | User & Auth        | users, user_profiles, password_resets
-- Group 2  | AI Analysis        | color_palettes, analysis_results, analysis_reviews
-- Group 3  | Skin Concerns      | skin_concerns, user_skin_concerns, product_concerns
-- Group 4  | Gemini AI          | gemini_sessions, gemini_messages
-- Group 5  | Photo Editor       | edit_filters, edit_stickers, photo_edits
-- Group 6  | Product            | brands, product_categories, products, product_links,
--          |                    | product_tags, product_tag_map, product_color_shades
-- Group 7  | Recommendation     | recommendation_rules, recommendations,
--          |                    | favorites, recommendation_feedback
-- Group 8  | Review             | product_reviews
-- Group 9  | Commission         | click_logs, commissions
-- Group 10 | Blog               | blog_categories, blog_posts
-- Group 11 | Notification       | notifications
-- Group 12 | Marketing          | banners, search_history
-- Group 13 | Admin              | admin_logs
-- ============================================================
