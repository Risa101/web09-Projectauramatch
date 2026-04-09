"""
AuraMatch Conceptual Class Diagram — UML Style
Traditional UML class diagram rendered with matplotlib.
Style: yellow header / cream body / multiplicity labels / orthogonal lines
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np
import math

# ─── Global style ───
FONT = "DejaVu Sans"
TITLE_FS = 13
ATTR_FS = 10.5
CLASS_W = 5.0
HEADER_H = 0.7
LINE_H = 0.38
PAD = 0.18          # text left padding
HEADER_COLOR = "#FFE082"
BODY_COLOR = "#FFFDE7"
BORDER_COLOR = "#5D4037"
TEXT_COLOR = "#212121"
METHOD_COLOR = "#1565C0"
MULT_COLOR = "#B71C1C"
LINE_COLOR = "#795548"
GROUP_COLOR = "#1565C0"

# ─── Helpers ───
def box_h(attrs, methods):
    n_a = max(len(attrs), 1)
    n_m = len(methods)
    h = HEADER_H + n_a * LINE_H + 0.25
    if n_m:
        h += n_m * LINE_H + 0.15
    else:
        h += 0.1
    return h

# ─── Class data ───
# pos = (col, row) on a logical grid; will be converted to canvas coords.
# Grid: col spacing = 6.0, row spacing varies per row.
COL_W = 6.2
ROW_POSITIONS = {
    # row_id: y_top
    0: 50,    # Row 0 — top
    1: 42.2,  # Row 1
    2: 35.0,  # Row 2
    3: 27.5,  # Row 3
    4: 20.5,  # Row 4
    5: 14.0,  # Row 5
    6: 7.5,   # Row 6 — bottom
}

def grid(col, row):
    return (col * COL_W + 0.5, ROW_POSITIONS[row])

classes = {
    # ═══ ROW 0: User at center-left, Product at center-right ═══
    "User": {
        "attrs": ["# user_id : int <<PK>>", "# username : string", "# email : string",
                  "# password_hash : string", "# role : enum(admin, user)",
                  "# is_active : bool", "# created_at : datetime"],
        "methods": ["+register()", "+login()", "+getProfile()"],
        "pos": grid(0, 0),
    },
    "AnalysisResult": {
        "attrs": ["# analysis_id : int <<PK>>", "# user_id : int <<FK>>",
                  "# image_path : string", "# face_shape : enum(7 shapes)",
                  "# skin_tone : enum(6 levels)", "# skin_undertone : enum(3)",
                  "# personal_color : enum(4 seasons)",
                  "# palette_id : int <<FK>>", "# confidence_score : decimal"],
        "methods": ["+analyzeFace()", "+getSkinLab()"],
        "pos": grid(2, 0),
    },
    "ColorPalette": {
        "attrs": ["# palette_id : int <<PK>>", "# season : enum(4)",
                  "# sub_type : string",
                  "# best_colors : JSON [L*a*b*]",
                  "# avoid_colors : JSON [L*a*b*]", "# makeup_tips : text"],
        "methods": ["+matchSeason()", "+getBestColors()"],
        "pos": grid(4, 0),
    },
    "Product": {
        "attrs": ["# product_id : int <<PK>>", "# brand_id : int <<FK>>",
                  "# category_id : int <<FK>>", "# name : string",
                  "# price : decimal", "# image_url : string",
                  "# personal_color : string", "# commission_rate : decimal"],
        "methods": ["+getDetails()", "+getShades()", "+getLinks()"],
        "pos": grid(6, 0),
    },

    # ═══ ROW 1 ═══
    "UserProfile": {
        "attrs": ["# profile_id : int <<PK>>", "# user_id : int <<FK>>",
                  "# first_name : string", "# last_name : string",
                  "# gender : enum", "# avatar_url : string"],
        "methods": ["+updateProfile()"],
        "pos": grid(0, 1),
    },
    "AnalysisReview": {
        "attrs": ["# review_id : int <<PK>>", "# analysis_id : int <<FK>>",
                  "# user_id : int <<FK>>", "# is_accurate : bool",
                  "# comment : text"],
        "methods": ["+submitReview()"],
        "pos": grid(2, 1),
    },
    "RecommendationRule": {
        "attrs": ["# rule_id : int <<PK>>", "# product_id : int <<FK>>",
                  "# face_shape : enum", "# skin_tone : enum",
                  "# personal_color : enum", "# priority : int"],
        "methods": ["+matchRule()"],
        "pos": grid(4, 1),
    },
    "Brand": {
        "attrs": ["# brand_id : int <<PK>>", "# name : string",
                  "# logo_url : string", "# website_url : string"],
        "methods": ["+getProducts()"],
        "pos": grid(6, 1),
    },
    "ProductCategory": {
        "attrs": ["# category_id : int <<PK>>", "# name : string",
                  "# description : text"],
        "methods": ["+getProducts()"],
        "pos": grid(7.5, 1),
    },

    # ═══ ROW 2 ═══
    "PasswordReset": {
        "attrs": ["# reset_id : int <<PK>>", "# user_id : int <<FK>>",
                  "# token : string", "# expires_at : datetime"],
        "methods": ["+resetPassword()"],
        "pos": grid(0, 2),
    },
    "Recommendation": {
        "attrs": ["# recommendation_id : int <<PK>>",
                  "# analysis_id : int <<FK>>", "# product_id : int <<FK>>",
                  "# score : decimal [S1-S6]"],
        "methods": ["+computeScore()", "+rank()"],
        "pos": grid(2, 2),
    },
    "RecommendationFeedback": {
        "attrs": ["# feedback_id : int <<PK>>",
                  "# recommendation_id : int <<FK>>",
                  "# user_id : int <<FK>>", "# rating : enum(like, dislike)"],
        "methods": ["+submitFeedback()"],
        "pos": grid(4, 2),
    },
    "Favorite": {
        "attrs": ["# favorite_id : int <<PK>>", "# user_id : int <<FK>>",
                  "# product_id : int <<FK>>"],
        "methods": ["+toggle()"],
        "pos": grid(6, 2),
    },
    "ProductColorShade": {
        "attrs": ["# shade_id : int <<PK>>", "# product_id : int <<FK>>",
                  "# shade_name : string", "# hex_color : string"],
        "methods": ["+getColorLab()"],
        "pos": grid(7.5, 2),
    },

    # ═══ ROW 3 ═══
    "SkinConcern": {
        "attrs": ["# concern_id : int <<PK>>", "# name : string",
                  "# description : text"],
        "methods": [],
        "pos": grid(0, 3),
    },
    "UserSkinConcern": {
        "attrs": ["# id : int <<PK>>", "# user_id : int <<FK>>",
                  "# concern_id : int <<FK>>", "# severity : enum"],
        "methods": [],
        "pos": grid(1.5, 3),
    },
    "ProductConcern": {
        "attrs": ["# id : int <<PK>>", "# product_id : int <<FK>>",
                  "# concern_id : int <<FK>>"],
        "methods": [],
        "pos": grid(3, 3),
    },
    "GeminiSession": {
        "attrs": ["# session_id : int <<PK>>", "# user_id : int <<FK>>",
                  "# analysis_id : int <<FK>>", "# title : string"],
        "methods": ["+startChat()", "+getHistory()"],
        "pos": grid(4.5, 3),
    },
    "GeminiMessage": {
        "attrs": ["# message_id : int <<PK>>", "# session_id : int <<FK>>",
                  "# role : enum(user, model)", "# prompt : text",
                  "# response : text"],
        "methods": ["+send()", "+getResponse()"],
        "pos": grid(6, 3),
    },
    "ProductLink": {
        "attrs": ["# link_id : int <<PK>>", "# product_id : int <<FK>>",
                  "# platform : enum(6)", "# url : string"],
        "methods": ["+trackClick()"],
        "pos": grid(7.5, 3),
    },

    # ═══ ROW 4 ═══
    "BlogCategory": {
        "attrs": ["# category_id : int <<PK>>", "# name : string"],
        "methods": [],
        "pos": grid(0, 4),
    },
    "BlogPost": {
        "attrs": ["# post_id : int <<PK>>", "# author_id : int <<FK>>",
                  "# category_id : int <<FK>>", "# title : string",
                  "# content : text", "# is_published : bool"],
        "methods": ["+publish()"],
        "pos": grid(1.5, 4),
    },
    "PhotoEdit": {
        "attrs": ["# edit_id : int <<PK>>", "# user_id : int <<FK>>",
                  "# original_image : string", "# edited_image : string",
                  "# edit_config : JSON", "# source : enum"],
        "methods": ["+applyFilter()", "+save()"],
        "pos": grid(3, 4),
    },
    "SavedLook": {
        "attrs": ["# look_id : int <<PK>>", "# user_id : int <<FK>>",
                  "# name : string", "# makeup_data : JSON"],
        "methods": ["+saveLook()", "+loadLook()"],
        "pos": grid(4.5, 4),
    },
    "ProductReview": {
        "attrs": ["# review_id : int <<PK>>", "# product_id : int <<FK>>",
                  "# user_id : int <<FK>>", "# rating : int(1-5)",
                  "# comment : text"],
        "methods": ["+submitReview()"],
        "pos": grid(6, 4),
    },
    "ProductTag": {
        "attrs": ["# tag_id : int <<PK>>", "# name : string"],
        "methods": [],
        "pos": grid(7.5, 4),
    },
    "ProductTagMap": {
        "attrs": ["# id : int <<PK>>", "# product_id : int <<FK>>",
                  "# tag_id : int <<FK>>"],
        "methods": [],
        "pos": grid(7.5, 5),
    },

    # ═══ ROW 5 ═══
    "Notification": {
        "attrs": ["# notification_id : int <<PK>>", "# user_id : int <<FK>>",
                  "# title : string", "# type : enum", "# is_read : bool"],
        "methods": ["+markRead()"],
        "pos": grid(0, 5),
    },
    "SearchHistory": {
        "attrs": ["# search_id : int <<PK>>", "# user_id : int <<FK>>",
                  "# keyword : string"],
        "methods": [],
        "pos": grid(1.5, 5),
    },
    "AdminLog": {
        "attrs": ["# log_id : int <<PK>>", "# admin_id : int <<FK>>",
                  "# action : string", "# table_name : string",
                  "# old_value : JSON", "# new_value : JSON"],
        "methods": ["+logAction()"],
        "pos": grid(3, 5),
    },
    "UserBehavior": {
        "attrs": ["# id : int <<PK>>", "# user_id : int <<FK>>",
                  "# event_type : string", "# event_data : JSON",
                  "# page : string"],
        "methods": ["+trackEvent()"],
        "pos": grid(4.5, 5),
    },
    "ClickLog": {
        "attrs": ["# log_id : int <<PK>>", "# link_id : int <<FK>>",
                  "# user_id : int <<FK>>", "# platform : enum"],
        "methods": ["+logClick()"],
        "pos": grid(6, 5),
    },

    # ═══ ROW 6 ═══
    "EditFilter": {
        "attrs": ["# filter_id : int <<PK>>", "# name : string",
                  "# category : enum", "# config : JSON"],
        "methods": [],
        "pos": grid(3, 6),
    },
    "EditSticker": {
        "attrs": ["# sticker_id : int <<PK>>", "# name : string",
                  "# category : enum", "# image_url : string"],
        "methods": [],
        "pos": grid(4.5, 6),
    },
    "Commission": {
        "attrs": ["# commission_id : int <<PK>>", "# link_id : int <<FK>>",
                  "# amount : decimal", "# status : enum"],
        "methods": ["+confirm()", "+pay()"],
        "pos": grid(6, 6),
    },
    "Banner": {
        "attrs": ["# banner_id : int <<PK>>", "# title : string",
                  "# image_url : string", "# position : enum",
                  "# is_active : bool"],
        "methods": [],
        "pos": grid(0, 6),
    },
}

# ─── Relationships ───
relationships = [
    # User core
    ("User", "UserProfile", "1", "1"),
    ("User", "PasswordReset", "1", "*"),
    # Analysis
    ("User", "AnalysisResult", "1", "*"),
    ("AnalysisResult", "ColorPalette", "*", "1"),
    ("AnalysisResult", "AnalysisReview", "1", "*"),
    # Recommendations
    ("AnalysisResult", "Recommendation", "1", "*"),
    ("Product", "Recommendation", "1", "*"),
    ("Recommendation", "RecommendationFeedback", "1", "*"),
    ("User", "RecommendationFeedback", "1", "*"),
    ("Product", "RecommendationRule", "1", "*"),
    # Product
    ("Brand", "Product", "1", "*"),
    ("ProductCategory", "Product", "1", "*"),
    ("Product", "ProductColorShade", "1", "*"),
    ("Product", "ProductLink", "1", "*"),
    ("Product", "ProductTagMap", "1", "*"),
    ("ProductTag", "ProductTagMap", "1", "*"),
    # Favorites & Reviews
    ("User", "Favorite", "1", "*"),
    ("Product", "Favorite", "1", "*"),
    ("User", "ProductReview", "1", "*"),
    ("Product", "ProductReview", "1", "*"),
    # Skin Concern
    ("User", "UserSkinConcern", "1", "*"),
    ("SkinConcern", "UserSkinConcern", "1", "*"),
    ("Product", "ProductConcern", "1", "*"),
    ("SkinConcern", "ProductConcern", "1", "*"),
    # Gemini
    ("User", "GeminiSession", "1", "*"),
    ("GeminiSession", "GeminiMessage", "1", "*"),
    ("GeminiSession", "AnalysisResult", "*", "0..1"),
    # Photo Editor
    ("User", "PhotoEdit", "1", "*"),
    ("User", "SavedLook", "1", "*"),
    # Blog
    ("User", "BlogPost", "1", "*"),
    ("BlogCategory", "BlogPost", "1", "*"),
    # Tracking
    ("ProductLink", "ClickLog", "1", "*"),
    ("ProductLink", "Commission", "1", "*"),
    # Notifications & Admin
    ("User", "Notification", "1", "*"),
    ("User", "SearchHistory", "1", "*"),
    ("User", "AdminLog", "1", "*"),
    ("User", "UserBehavior", "1", "*"),
]


# ════════════════════════════════════════════════
# Drawing functions
# ════════════════════════════════════════════════

def draw_class(ax, name, data):
    x, y_top = data["pos"]
    attrs = data["attrs"]
    methods = data["methods"]
    w = CLASS_W
    h = box_h(attrs, methods)

    # --- Outer border (single rectangle for clean look) ---
    outer = Rectangle((x, y_top - h), w, h,
                       facecolor=BODY_COLOR, edgecolor=BORDER_COLOR,
                       linewidth=1.4, zorder=2)
    ax.add_patch(outer)

    # --- Header fill ---
    hdr = Rectangle((x, y_top - HEADER_H), w, HEADER_H,
                     facecolor=HEADER_COLOR, edgecolor=BORDER_COLOR,
                     linewidth=1.4, zorder=3, clip_on=False)
    ax.add_patch(hdr)

    # Header text
    ax.text(x + w / 2, y_top - HEADER_H / 2, name,
            ha="center", va="center", fontsize=TITLE_FS, fontweight="bold",
            fontfamily=FONT, color=TEXT_COLOR, zorder=4)

    # Separator under header
    ax.plot([x, x + w], [y_top - HEADER_H, y_top - HEADER_H],
            color=BORDER_COLOR, linewidth=1.2, zorder=4)

    # Attributes
    cy = y_top - HEADER_H - 0.28
    for a in attrs:
        ax.text(x + PAD, cy, a, ha="left", va="center",
                fontsize=ATTR_FS, fontfamily=FONT, color=TEXT_COLOR, zorder=4)
        cy -= LINE_H

    # Separator before methods
    if methods:
        sep_y = cy + LINE_H * 0.3
        ax.plot([x, x + w], [sep_y, sep_y],
                color=BORDER_COLOR, linewidth=0.8, zorder=4)
        cy -= 0.05
        for m in methods:
            ax.text(x + PAD, cy, m, ha="left", va="center",
                    fontsize=ATTR_FS, fontfamily=FONT, color=METHOD_COLOR, zorder=4)
            cy -= LINE_H

    # Store bbox
    data["_bbox"] = (x, y_top - h, x + w, y_top)


def anchor_points(bbox):
    x0, y0, x1, y1 = bbox
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    return {"top": (cx, y1), "bottom": (cx, y0),
            "left": (x0, cy), "right": (x1, cy)}


def pick_anchors(ba, bb):
    pa = anchor_points(ba)
    pb = anchor_points(bb)
    best, best_d = None, 1e9
    for ka, va in pa.items():
        for kb, vb in pb.items():
            d = math.hypot(va[0] - vb[0], va[1] - vb[1])
            if d < best_d:
                best_d = d
                best = (va, vb, ka, kb)
    return best


# Keep track of used anchor slots to offset overlapping lines
_anchor_usage = {}

def draw_rel(ax, ca, cb, ma, mb):
    ba = classes[ca]["_bbox"]
    bb = classes[cb]["_bbox"]
    pa, pb, sa, sb = pick_anchors(ba, bb)

    # Offset if same anchor used multiple times
    key_a = (ca, sa)
    key_b = (cb, sb)
    off_a = _anchor_usage.get(key_a, 0)
    off_b = _anchor_usage.get(key_b, 0)
    _anchor_usage[key_a] = off_a + 1
    _anchor_usage[key_b] = off_b + 1

    shift = 0.25
    if sa in ("top", "bottom"):
        pa = (pa[0] + (off_a - 0.5) * shift, pa[1])
    else:
        pa = (pa[0], pa[1] + (off_a - 0.5) * shift)
    if sb in ("top", "bottom"):
        pb = (pb[0] + (off_b - 0.5) * shift, pb[1])
    else:
        pb = (pb[0], pb[1] + (off_b - 0.5) * shift)

    # Draw orthogonal line (single bend)
    if sa in ("top", "bottom") and sb in ("top", "bottom"):
        mid_y = (pa[1] + pb[1]) / 2
        ax.plot([pa[0], pa[0], pb[0], pb[0]], [pa[1], mid_y, mid_y, pb[1]],
                color=LINE_COLOR, linewidth=1.0, zorder=1, solid_capstyle="round")
    elif sa in ("left", "right") and sb in ("left", "right"):
        mid_x = (pa[0] + pb[0]) / 2
        ax.plot([pa[0], mid_x, mid_x, pb[0]], [pa[1], pa[1], pb[1], pb[1]],
                color=LINE_COLOR, linewidth=1.0, zorder=1, solid_capstyle="round")
    else:
        # L-shaped
        if sa in ("top", "bottom"):
            ax.plot([pa[0], pa[0], pb[0]], [pa[1], pb[1], pb[1]],
                    color=LINE_COLOR, linewidth=1.0, zorder=1, solid_capstyle="round")
        else:
            ax.plot([pa[0], pb[0], pb[0]], [pa[1], pa[1], pb[1]],
                    color=LINE_COLOR, linewidth=1.0, zorder=1, solid_capstyle="round")

    # Multiplicity text near endpoints
    d = 0.3
    if sa == "top":
        ta = (pa[0] + 0.15, pa[1] + d)
    elif sa == "bottom":
        ta = (pa[0] + 0.15, pa[1] - d)
    elif sa == "right":
        ta = (pa[0] + d, pa[1] + 0.18)
    else:
        ta = (pa[0] - d, pa[1] + 0.18)

    if sb == "top":
        tb = (pb[0] + 0.15, pb[1] + d)
    elif sb == "bottom":
        tb = (pb[0] + 0.15, pb[1] - d)
    elif sb == "right":
        tb = (pb[0] + d, pb[1] + 0.18)
    else:
        tb = (pb[0] - d, pb[1] + 0.18)

    ax.text(ta[0], ta[1], ma, fontsize=9.5, fontweight="bold",
            color=MULT_COLOR, ha="center", va="center", zorder=5)
    ax.text(tb[0], tb[1], mb, fontsize=9.5, fontweight="bold",
            color=MULT_COLOR, ha="center", va="center", zorder=5)


# ════════════════════════════════════════════════
# Build figure
# ════════════════════════════════════════════════
fig_w = 9 * COL_W + 2
fig_h = 52
fig, ax = plt.subplots(figsize=(fig_w, fig_h))
ax.set_xlim(-1, fig_w - 1)
ax.set_ylim(3, 54)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor("white")

# ─── Title ───
ax.text(fig_w / 2 - 1, 53, "AuraMatch — Conceptual Class Diagram",
        ha="center", va="center", fontsize=26, fontweight="bold",
        fontfamily=FONT, color="#3E2723")
ax.text(fig_w / 2 - 1, 52.2,
        "AI-Powered Beauty & Cosmetics Recommendation Platform  |  35 Entities",
        ha="center", va="center", fontsize=15, fontfamily=FONT, color="#5D4037")

# ─── Group labels (background rectangles + text) ───
group_labels = [
    (grid(0, 0)[0] - 0.3, ROW_POSITIONS[0] + 0.6, "User & Authentication"),
    (grid(2, 0)[0] - 0.3, ROW_POSITIONS[0] + 0.6, "AI Face Analysis (CIELAB / CIEDE2000)"),
    (grid(6, 0)[0] - 0.3, ROW_POSITIONS[0] + 0.6, "Product Catalog"),
    (grid(2, 2)[0] - 0.3, ROW_POSITIONS[2] + 0.6, "Recommendation Engine (Multi-Signal S1-S6)"),
    (grid(0, 3)[0] - 0.3, ROW_POSITIONS[3] + 0.6, "Skin Concerns"),
    (grid(4.5, 3)[0] - 0.3, ROW_POSITIONS[3] + 0.6, "Gemini AI Chat"),
    (grid(0, 4)[0] - 0.3, ROW_POSITIONS[4] + 0.6, "Blog"),
    (grid(3, 4)[0] - 0.3, ROW_POSITIONS[4] + 0.6, "Photo Editor"),
    (grid(6, 4)[0] - 0.3, ROW_POSITIONS[4] + 0.6, "Reviews & Tags"),
    (grid(0, 5)[0] - 0.3, ROW_POSITIONS[5] + 0.6, "Admin, Notifications & Analytics"),
    (grid(6, 5)[0] - 0.3, ROW_POSITIONS[5] + 0.6, "Affiliate Tracking"),
]
for gx, gy, label in group_labels:
    ax.text(gx, gy, f"\u00ab{label}\u00bb", fontsize=11.5, fontstyle="italic",
            fontweight="bold", color=GROUP_COLOR, ha="left", va="center", zorder=5)

# ─── Draw classes ───
for name, data in classes.items():
    draw_class(ax, name, data)

# ─── Draw relationships ───
for r in relationships:
    draw_rel(ax, *r)

# ─── Footer ───
ax.text(fig_w / 2 - 1, 4.0,
        "Generated for AuraMatch Project \u2014 Web09  |  Conceptual Class Diagram  |  35 Entities, 37 Relationships",
        ha="center", va="center", fontsize=11, color="#9E9E9E", fontstyle="italic")

plt.tight_layout(pad=1.0)
out_base = "/Users/saridbutchuang/Desktop/web09_Projectauramatch/diagrams/class_diagram"
plt.savefig(out_base + ".png", dpi=150, bbox_inches="tight", facecolor="white")
plt.savefig(out_base + ".pdf", bbox_inches="tight", facecolor="white")
print(f"Saved: {out_base}.png  +  .pdf")
