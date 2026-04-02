from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.database import get_db
from models.user import User
from models.misc import UserProfile
from models.analysis import AnalysisResult
from routes.auth import get_current_user

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/")
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.user_id).first()
    return {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": str(current_user.created_at),
        "profile": {
            "first_name": profile.first_name if profile else None,
            "last_name": profile.last_name if profile else None,
            "display_name": profile.display_name if profile else None,
            "avatar_url": profile.avatar_url if profile else None,
            "birth_date": str(profile.birth_date) if profile and profile.birth_date else None,
            "gender": profile.gender if profile else None,
            "nationality": profile.nationality if profile else None,
            "bio": profile.bio if profile else None,
        } if profile else None,
    }


@router.put("/")
def update_profile(
    first_name: str = None,
    last_name: str = None,
    display_name: str = None,
    bio: str = None,
    gender: str = None,
    nationality: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.user_id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.user_id)
        db.add(profile)

    if first_name is not None:
        profile.first_name = first_name
    if last_name is not None:
        profile.last_name = last_name
    if display_name is not None:
        profile.display_name = display_name
    if bio is not None:
        profile.bio = bio
    if gender is not None:
        profile.gender = gender
    if nationality is not None:
        profile.nationality = nationality

    db.commit()
    return {"message": "Profile updated"}


@router.get("/analyses")
def get_my_analyses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analyses = (
        db.query(AnalysisResult)
        .filter(AnalysisResult.user_id == current_user.user_id)
        .order_by(AnalysisResult.created_at.desc())
        .all()
    )
    return [
        {
            "analysis_id": a.analysis_id,
            "face_shape": a.face_shape,
            "skin_tone": a.skin_tone,
            "skin_undertone": a.skin_undertone,
            "personal_color": a.personal_color,
            "confidence_score": float(a.confidence_score) if a.confidence_score else None,
            "created_at": str(a.created_at),
        }
        for a in analyses
    ]
