import math
import numpy as np
from sklearn.cluster import KMeans
import colour

# ── Module-level cache for palette references ────────────────────────────────
_palette_cache = None


def rgb_to_lab(rgb_pixels: np.ndarray) -> np.ndarray:
    """Convert an (N, 3) array of RGB values (0-255) to CIELAB.

    Uses sRGB → XYZ (D65 illuminant) → L*a*b* via colour-science.
    """
    rgb_norm = rgb_pixels.astype(np.float64) / 255.0
    xyz = colour.sRGB_to_XYZ(rgb_norm)
    lab = colour.XYZ_to_Lab(xyz)
    return lab


def extract_skin_lab(rgb_image: np.ndarray) -> tuple:
    """Extract dominant skin color in L*a*b* from an RGB image.

    Crops center region, converts to CIELAB, clusters with K-Means,
    and returns the (L, a, b) centroid of the largest cluster.
    """
    h, w = rgb_image.shape[:2]
    center_region = rgb_image[h // 4:3 * h // 4, w // 4:3 * w // 4]
    pixels = center_region.reshape(-1, 3)

    lab_pixels = rgb_to_lab(pixels)

    kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
    kmeans.fit(lab_pixels)

    largest_cluster = np.argmax(np.bincount(kmeans.labels_))
    dominant_lab = kmeans.cluster_centers_[largest_cluster]

    return float(dominant_lab[0]), float(dominant_lab[1]), float(dominant_lab[2])


def extract_skin_lab_from_bbox(rgb_image: np.ndarray, bbox: tuple) -> tuple:
    """Extract dominant skin color from the cheek region within a face bounding box.

    Samples the middle third of the face bbox (cheek area), filters outlier
    pixels (hair, highlights), then clusters with K-Means.
    """
    x1, y1, x2, y2 = bbox
    bh, bw = y2 - y1, x2 - x1
    cheek = rgb_image[y1 + bh // 3:y1 + 2 * bh // 3, x1 + bw // 4:x1 + 3 * bw // 4]
    if cheek.size == 0:
        return extract_skin_lab(rgb_image)

    pixels = cheek.reshape(-1, 3)
    lab_pixels = rgb_to_lab(pixels)

    # Filter outliers: very dark (hair/eyebrows) and very bright (highlights)
    mask = (lab_pixels[:, 0] > 20) & (lab_pixels[:, 0] < 95)
    lab_filtered = lab_pixels[mask] if mask.sum() > 50 else lab_pixels

    kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
    kmeans.fit(lab_filtered)

    largest_cluster = np.argmax(np.bincount(kmeans.labels_))
    c = kmeans.cluster_centers_[largest_cluster]

    return float(c[0]), float(c[1]), float(c[2])


def classify_tone_from_lab(L: float, b: float) -> str:
    """Classify skin tone using Individual Typology Angle (ITA).

    ITA = arctan((L* - 50) / b*) × (180/π)

    References:
        Chardon, A., Cretois, I., & Hourseau, C. (1991). Skin colour typology
        and suntanning pathways. Int J Cosmet Sci, 13(4), 191-208.

        Del Bino, S., & Bernerd, F. (2013). Variations in skin colour and the
        biological consequences of ultraviolet radiation exposure.
        Br J Dermatol, 169(s3), 33-40.

    Thresholds (Chardon et al. 1991, Table 1):
        ITA > 55°  → fair (Very Light)
        ITA > 41°  → light (Light)
        ITA > 28°  → medium (Intermediate)
        ITA > 10°  → tan (Tan / Mat)
        ITA > -30° → dark (Brown)
        ITA ≤ -30° → deep (Dark)
    """
    if abs(b) < 0.01:
        b = 0.01  # avoid division by zero
    ita = math.atan2(L - 50, b) * (180.0 / math.pi)

    if ita > 55:
        return "fair"
    elif ita > 41:
        return "light"
    elif ita > 28:
        return "medium"
    elif ita > 10:
        return "tan"
    elif ita > -30:
        return "dark"
    else:
        return "deep"


def classify_undertone_from_lab(a: float, b: float) -> str:
    """Classify skin undertone using CIELAB hue angle (h_ab).

    h_ab = atan2(b*, a*) in degrees, range [0, 360).

    References:
        Xiao, K., Yates, J. M., Zardawi, F., et al. (2017). Characterising
        the variations in ethnic skin colours: a new calibrated data base for
        human skin. Skin Res Technol, 23(1), 21-29.

        Ly, B. C. K., et al. (2020). Research Techniques Made Simple:
        Cutaneous Colorimetry. J Invest Dermatol, 140(1), 3-12.e1.

    Thresholds (derived from Xiao et al. 2017 measured skin hue distributions):
        h_ab > 65° → warm (yellow-dominant, typical of warm-toned skin)
        h_ab < 50° → cool (red/pink-dominant, typical of cool-toned skin)
        50° ≤ h_ab ≤ 65° → neutral
    """
    h_ab = math.atan2(b, a) * (180.0 / math.pi)
    if h_ab < 0:
        h_ab += 360

    if h_ab > 65:
        return "warm"
    elif h_ab < 50:
        return "cool"
    else:
        return "neutral"


def load_palette_references(db_session) -> list:
    """Query ColorPalette table and extract skin_reference centroids.

    Returns a list of dicts:
        {palette_id, season, sub_type, centroid_lab: (L, a, b)}

    Results are cached after the first call.
    """
    global _palette_cache
    if _palette_cache is not None:
        return _palette_cache

    from models.analysis import ColorPalette

    palettes = db_session.query(ColorPalette).all()
    refs = []
    for p in palettes:
        best = p.best_colors
        if not best or "skin_reference" not in best:
            continue
        sr = best["skin_reference"]
        refs.append({
            "palette_id": p.palette_id,
            "season": p.season,
            "sub_type": p.sub_type,
            "centroid_lab": (sr["L"], sr["a"], sr["b"]),
        })

    _palette_cache = refs
    return refs


def match_season_by_delta_e(skin_lab: tuple, palette_refs: list) -> tuple:
    """Match skin L*a*b* against palette reference centroids using CIEDE2000.

    Args:
        skin_lab: (L, a, b) of detected skin
        palette_refs: list from load_palette_references()

    Returns:
        (season: str, palette_id: int, confidence_score: float)

    Falls back to ("spring", None, 85.0) if no palette refs available.
    """
    if not palette_refs:
        return "spring", None, 85.0

    skin_arr = np.array(skin_lab)

    scores = []
    for ref in palette_refs:
        centroid = np.array(ref["centroid_lab"])
        de = colour.difference.delta_E_CIE2000(skin_arr, centroid)
        scores.append((de, ref))

    scores.sort(key=lambda x: x[0])

    best_de, best_ref = scores[0]

    if len(scores) >= 2:
        second_de = scores[1][0]
        denominator = best_de + second_de
        if denominator > 0:
            raw_confidence = 100.0 * (1.0 - best_de / denominator)
        else:
            raw_confidence = 99.0
    else:
        raw_confidence = 85.0

    confidence = max(50.0, min(99.0, raw_confidence))

    return best_ref["season"], best_ref["palette_id"], round(confidence, 2)
