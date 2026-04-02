from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session, joinedload
from config.database import get_db
from models.analysis import AnalysisResult, ColorPalette
from models.product import Product
from models.user import User
from routes.auth import get_current_user
from routes.recommendations import generate_recs_for_analysis
from services.ai_service import analyze_face, FACE_SHAPE_TIPS
import os, shutil, uuid

router = APIRouter(prefix="/analysis", tags=["Analysis"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def create_analysis(
    gender: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    result = analyze_face(filepath, gender, db_session=db)

    analysis = AnalysisResult(
        user_id=current_user.user_id,
        image_path=filepath,
        gender=gender,
        face_shape=result.get("face_shape"),
        skin_tone=result.get("skin_tone"),
        skin_undertone=result.get("skin_undertone"),
        personal_color=result.get("personal_color"),
        palette_id=result.get("palette_id"),
        ethnicity=result.get("ethnicity"),
        confidence_score=result.get("confidence_score")
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # ── Build enriched response ──────────────────────────────────────────────

    # Auto-generate recommendations
    recs = generate_recs_for_analysis(analysis, db)

    # Load palette data
    palette_data = None
    if analysis.palette_id:
        palette = db.query(ColorPalette).filter(
            ColorPalette.palette_id == analysis.palette_id
        ).first()
        if palette:
            palette_data = {
                "palette_id": palette.palette_id,
                "season": palette.season,
                "sub_type": palette.sub_type,
                "best_colors": palette.best_colors,
                "avoid_colors": palette.avoid_colors,
                "makeup_tips": palette.makeup_tips,
            }

    # Face shape tips
    tips = FACE_SHAPE_TIPS.get(analysis.face_shape, {})

    # Format recommendations
    rec_list = []
    for rec in recs[:20]:
        p = (
            db.query(Product)
            .options(joinedload(Product.brand), joinedload(Product.links))
            .filter(Product.product_id == rec.product_id)
            .first()
        )
        if p:
            rec_list.append({
                "recommendation_id": rec.recommendation_id,
                "score": float(rec.score) if rec.score else 0,
                "product": {
                    "product_id": p.product_id,
                    "name": p.name,
                    "price": float(p.price) if p.price else None,
                    "image_url": p.image_url,
                    "brand": p.brand.name if p.brand else None,
                    "links": [
                        {"platform": l.platform, "url": l.url}
                        for l in p.links if l.is_active
                    ],
                },
            })

    return {
        "analysis_id": analysis.analysis_id,
        "user_id": analysis.user_id,
        "image_path": analysis.image_path,
        "gender": analysis.gender,
        "face_shape": analysis.face_shape,
        "skin_tone": analysis.skin_tone,
        "skin_undertone": analysis.skin_undertone,
        "personal_color": analysis.personal_color,
        "ethnicity": analysis.ethnicity,
        "confidence_score": float(analysis.confidence_score) if analysis.confidence_score else None,
        "created_at": str(analysis.created_at) if analysis.created_at else None,
        "palette": palette_data,
        "face_shape_tips": tips,
        "recommendations": rec_list,
    }


@router.get("/history")
def get_my_analyses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(AnalysisResult).filter(
        AnalysisResult.user_id == current_user.user_id
    ).order_by(AnalysisResult.created_at.desc()).all()


@router.get("/{analysis_id}")
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(AnalysisResult).filter(AnalysisResult.analysis_id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis
