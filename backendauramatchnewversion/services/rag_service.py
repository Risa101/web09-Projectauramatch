"""RAG (Retrieval-Augmented Generation) service for the Gemini Beauty Consultant.

Orchestrates the pipeline: user query -> ChromaDB retrieval -> context building
-> Gemini generation with product knowledge and user personalization.
"""
import logging
import os

from PIL import Image
from sqlalchemy.orm import Session, joinedload

from config.chromadb_config import get_collection
from services.embedding_service import embed_single
from services.gemini_service import create_gemini_model

logger = logging.getLogger(__name__)

MAX_HISTORY_MESSAGES = 10

BEAUTY_CONSULTANT_PERSONA = (
    "คุณคือ AuraMatch Beauty Consultant — ผู้เชี่ยวชาญด้านความงามและเครื่องสำอางส่วนตัว\n\n"
    "บทบาทของคุณ:\n"
    "- ให้คำแนะนำเรื่องเครื่องสำอาง สกินแคร์ และเมกอัพที่เหมาะกับผู้ใช้\n"
    "- ตอบคำถามเป็นภาษาไทยด้วยน้ำเสียงเป็นมิตรและเป็นมืออาชีพ\n"
    "- ตอบกระชับ ได้ใจความ ไม่ยาวเกินไป\n\n"
    "กฎเด็ดขาดเรื่องสินค้า (Brand Restriction):\n"
    "- ห้ามแนะนำหรือเอ่ยถึงชื่อแบรนด์และชื่อสินค้าอื่นที่ไม่มีอยู่ใน "
    "\"สินค้าที่เกี่ยวข้องจากระบบ\" โดยเด็ดขาด\n"
    "- ถ้ามีรายชื่อสินค้าในระบบให้มา ให้แนะนำเฉพาะสินค้าเหล่านั้นเท่านั้น "
    "ห้ามแต่งชื่อสินค้า แบรนด์ หรือราคาขึ้นเอง\n"
    "- หากไม่มีสินค้าที่ตรงกับความต้องการ ให้แนะนำเคล็ดลับความงามทั่วไป"
    "โดยไม่ระบุชื่อแบรนด์\n\n"
    "กฎเรื่อง Personal Color Fallback:\n"
    "- หากผู้ใช้ถามเกี่ยวกับการเลือกสีเครื่องสำอางตาม Personal Color "
    "แต่ไม่มีข้อมูล Analysis Context (เช่น ผู้ใช้ยังไม่ได้วิเคราะห์หน้า) "
    "ให้แนะนำอย่างสุภาพให้ผู้ใช้ไปทำแบบทดสอบวิเคราะห์ใบหน้าที่หน้า Analyze ก่อน "
    "หรือสอบถามว่าผู้ใช้ทราบฤดูกาล (Spring, Summer, Autumn, Winter) "
    "ของตนเองหรือไม่\n\n"
    "ข้อมูลสำคัญ — No Denial of Personal Color Data:\n"
    "- ระบบ AuraMatch มีข้อมูล Personal Color สำหรับสินค้าทุกชิ้นในร้าน\n"
    "- ห้าม AI ปฏิเสธหรืออ้างว่าระบบไม่มีข้อมูลนี้โดยเด็ดขาด"
)


def retrieve_product_context(query: str, top_k: int = 5) -> list[int] | None:
    """Query ChromaDB for product IDs relevant to the user's message.

    Returns a list of product_id ints, or None on any failure.
    """
    try:
        collection = get_collection()
        if collection is None or collection.count() == 0:
            return None

        query_embedding = embed_single(query)
        if query_embedding is None:
            return None

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"is_active": 1},
        )

        if not results or not results["ids"] or not results["ids"][0]:
            return None

        product_ids = []
        for meta in results["metadatas"][0]:
            pid = meta.get("product_id")
            if pid is not None:
                product_ids.append(int(pid))

        return product_ids if product_ids else None
    except Exception as exc:
        logger.warning("RAG retrieval failed: %s", exc)
        return None


def fetch_products_by_ids(product_ids: list[int], db: Session) -> list[dict]:
    """Fetch full product details from MySQL by IDs."""
    if not product_ids:
        return []

    from models.product import Product

    products = (
        db.query(Product)
        .options(joinedload(Product.brand), joinedload(Product.category))
        .filter(Product.product_id.in_(product_ids))
        .all()
    )

    return [
        {
            "product_id": p.product_id,
            "name": p.name,
            "brand_name": p.brand.name if p.brand else None,
            "category_name": p.category.name if p.category else None,
            "price": float(p.price) if p.price else None,
            "description": p.description,
            "personal_color": p.personal_color,
        }
        for p in products
    ]


def format_product_context(products: list[dict] | None) -> str:
    """Format product list into a Thai-labeled text block for the system prompt."""
    if not products:
        return ""

    lines = ["--- สินค้าที่เกี่ยวข้องจากระบบ ---"]
    for i, p in enumerate(products, 1):
        name = p.get("name") or "ไม่ระบุ"
        brand = p.get("brand_name") or "ไม่ระบุ"
        category = p.get("category_name") or "ไม่ระบุ"
        price = f"฿{p['price']:.0f}" if p.get("price") else "ไม่ระบุ"
        desc = p.get("description") or ""

        lines.append(
            f"{i}. [ชื่อ] {name} | [แบรนด์] {brand} | [หมวด] {category} | [ราคา] {price}"
        )
        if desc:
            lines.append(f"   รายละเอียด: {desc}")

    return "\n".join(lines)


def build_analysis_context(analysis) -> str:
    """Format user's analysis data into Thai text for the system prompt."""
    if analysis is None:
        return ""

    parts = ["--- ข้อมูลผู้ใช้ ---"]
    if analysis.face_shape:
        parts.append(f"รูปทรงใบหน้า: {analysis.face_shape}")
    if analysis.skin_tone:
        parts.append(f"สีผิว: {analysis.skin_tone}")
    if analysis.skin_undertone:
        parts.append(f"อันเดอร์โทน: {analysis.skin_undertone}")
    if analysis.personal_color:
        parts.append(f"Personal Color: {analysis.personal_color}")

    return "\n".join(parts) if len(parts) > 1 else ""


def build_system_prompt(product_context: str, analysis_context: str) -> str:
    """Combine persona + dynamic context into the full system instruction."""
    sections = [BEAUTY_CONSULTANT_PERSONA]

    if analysis_context:
        sections.append(analysis_context)
    if product_context:
        sections.append(product_context)

    return "\n\n".join(sections)


def format_chat_history(messages: list) -> list[dict]:
    """Convert GeminiMessage ORM objects to Gemini SDK content format.

    Returns at most MAX_HISTORY_MESSAGES entries (last N messages).
    """
    if not messages:
        return []

    recent = messages[-MAX_HISTORY_MESSAGES:]
    history = []

    for msg in recent:
        if msg.prompt:
            history.append({"role": "user", "parts": [msg.prompt]})
        if msg.response:
            history.append({"role": "model", "parts": [msg.response]})

    return history


async def generate_rag_response(
    prompt: str,
    session_messages: list,
    analysis=None,
    image_path: str | None = None,
    db: Session | None = None,
    top_k: int = 5,
) -> tuple:
    """Main RAG orchestrator. Returns (response_text, None)."""
    try:
        # 1. Retrieve relevant products from ChromaDB
        product_ids = retrieve_product_context(prompt, top_k)

        # 2. Fetch full product data from MySQL
        products = []
        if product_ids and db is not None:
            products = fetch_products_by_ids(product_ids, db)

        # 3. Build context strings
        product_context = format_product_context(products)
        analysis_context = build_analysis_context(analysis)

        # 4. Build system prompt
        system_prompt = build_system_prompt(product_context, analysis_context)

        # 5. Format chat history
        history = format_chat_history(session_messages)

        # 6. Build the current user message
        user_parts = [prompt]
        if image_path and os.path.exists(image_path):
            user_parts.append(Image.open(image_path))

        contents = [*history, {"role": "user", "parts": user_parts}]

        # 7. Generate with Gemini
        model = create_gemini_model(system_instruction=system_prompt)
        response = model.generate_content(contents)

        return response.text, None
    except Exception as e:
        logger.error("RAG generation failed: %s", e)
        return f"Error: {str(e)}", None
