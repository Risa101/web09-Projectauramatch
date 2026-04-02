from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from models.analysis import AnalysisResult
from models.user import User
from routes.auth import get_current_user
from services.ai_service import analyze_face
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
    return analysis


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
