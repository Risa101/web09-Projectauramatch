"""
TF-IDF Product Recommendation Service
แนะนำสินค้าที่คล้ายกันโดยใช้ TF-IDF + Cosine Similarity
วิเคราะห์จาก: ชื่อสินค้า, description, category, brand
"""
import math
import re
from collections import Counter


def tokenize(text):
    """แยกคำ (ทั้งไทยและอังกฤษ)"""
    if not text:
        return []
    text = text.lower().strip()
    # แยกคำภาษาอังกฤษ + แยกตัวอักษรไทยเป็นกลุ่ม
    tokens = re.findall(r'[a-z]+|[ก-๙]+', text)
    return [t for t in tokens if len(t) > 1]


def build_document(product):
    """สร้าง document จากข้อมูลสินค้า (ให้น้ำหนักต่างกัน)"""
    parts = []
    # ชื่อสินค้า (น้ำหนัก x3)
    name = product.get('name', '') or ''
    parts.extend(tokenize(name) * 3)
    # Description (น้ำหนัก x2)
    desc = product.get('description', '') or ''
    parts.extend(tokenize(desc) * 2)
    # Category (น้ำหนัก x2)
    cat = product.get('category_name', '') or ''
    parts.extend(tokenize(cat) * 2)
    # Brand (น้ำหนัก x2)
    brand = product.get('brand_name', '') or ''
    parts.extend(tokenize(brand) * 2)
    return parts


def compute_tf(tokens):
    """คำนวณ Term Frequency"""
    counter = Counter(tokens)
    total = len(tokens)
    if total == 0:
        return {}
    return {word: count / total for word, count in counter.items()}


def compute_idf(documents):
    """คำนวณ Inverse Document Frequency"""
    n = len(documents)
    idf = {}
    all_words = set()
    for doc in documents:
        all_words.update(set(doc))

    for word in all_words:
        containing = sum(1 for doc in documents if word in set(doc))
        idf[word] = math.log((n + 1) / (containing + 1)) + 1  # smoothed IDF

    return idf


def compute_tfidf(tf, idf):
    """คำนวณ TF-IDF vector"""
    return {word: tf_val * idf.get(word, 0) for word, tf_val in tf.items()}


def cosine_similarity(vec_a, vec_b):
    """คำนวณ Cosine Similarity ระหว่าง 2 vectors"""
    # หา intersection ของ keys
    common_words = set(vec_a.keys()) & set(vec_b.keys())
    if not common_words:
        return 0.0

    dot_product = sum(vec_a[w] * vec_b[w] for w in common_words)
    norm_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    norm_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def get_similar_products(target_product, all_products, top_n=6):
    """
    หาสินค้าที่คล้ายกับ target_product มากที่สุด
    ใช้ TF-IDF + Cosine Similarity

    Args:
        target_product: dict ของสินค้าเป้าหมาย
        all_products: list ของ dict สินค้าทั้งหมด
        top_n: จำนวนสินค้าที่จะแนะนำ

    Returns:
        list ของ dict สินค้าที่คล้ายกัน พร้อม similarity score
    """
    target_id = target_product.get('product_id')

    # สร้าง documents
    documents = []
    product_map = {}
    for p in all_products:
        doc = build_document(p)
        documents.append(doc)
        product_map[len(documents) - 1] = p

    target_doc = build_document(target_product)
    documents.append(target_doc)
    target_idx = len(documents) - 1

    # คำนวณ IDF จากทุก documents
    idf = compute_idf(documents)

    # คำนวณ TF-IDF ของ target
    target_tf = compute_tf(documents[target_idx])
    target_tfidf = compute_tfidf(target_tf, idf)

    # คำนวณ similarity กับทุกสินค้า
    similarities = []
    for i in range(len(documents) - 1):  # ไม่รวม target
        p = product_map[i]
        if p.get('product_id') == target_id:
            continue

        doc_tf = compute_tf(documents[i])
        doc_tfidf = compute_tfidf(doc_tf, idf)
        sim = cosine_similarity(target_tfidf, doc_tfidf)

        if sim > 0:
            similarities.append({
                **p,
                'similarity_score': round(sim, 4)
            })

    # เรียงตาม similarity สูงสุด
    similarities.sort(key=lambda x: x['similarity_score'], reverse=True)

    return similarities[:top_n]
