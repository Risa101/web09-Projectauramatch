from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from config.database import get_db
from models.misc import SkinConcern, UserSkinConcern
from models.user import User
from routes.auth import get_current_user

router = APIRouter(prefix="/skin-concerns", tags=["Skin Concerns"])


class UserConcernItem(BaseModel):
    concern_id: int
    severity: str = "mild"


class UpdateConcernsRequest(BaseModel):
    concerns: list[UserConcernItem]


@router.get("/")
def list_skin_concerns(db: Session = Depends(get_db)):
    """List all available skin concerns."""
    concerns = db.query(SkinConcern).all()
    return [
        {
            "concern_id": c.concern_id,
            "name": c.name,
            "description": c.description,
            "icon_url": c.icon_url,
        }
        for c in concerns
    ]


@router.get("/me")
def get_my_concerns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's skin concerns."""
    rows = (
        db.query(UserSkinConcern)
        .filter(UserSkinConcern.user_id == current_user.user_id)
        .all()
    )
    return [
        {
            "id": r.id,
            "concern_id": r.concern_id,
            "name": r.concern.name if r.concern else None,
            "severity": r.severity,
        }
        for r in rows
    ]


@router.put("/me")
def update_my_concerns(
    body: UpdateConcernsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Replace the current user's skin concerns with the given list."""
    # Validate severity values
    valid_severities = {"mild", "moderate", "severe"}
    for item in body.concerns:
        if item.severity not in valid_severities:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid severity '{item.severity}'. Must be one of: {valid_severities}",
            )

    # Validate concern IDs exist
    if body.concerns:
        concern_ids = [item.concern_id for item in body.concerns]
        existing = db.query(SkinConcern.concern_id).filter(
            SkinConcern.concern_id.in_(concern_ids)
        ).all()
        existing_ids = {r.concern_id for r in existing}
        invalid = set(concern_ids) - existing_ids
        if invalid:
            raise HTTPException(status_code=404, detail=f"Concern IDs not found: {invalid}")

    # Delete existing and replace
    db.query(UserSkinConcern).filter(
        UserSkinConcern.user_id == current_user.user_id
    ).delete()

    for item in body.concerns:
        db.add(UserSkinConcern(
            user_id=current_user.user_id,
            concern_id=item.concern_id,
            severity=item.severity,
        ))

    db.commit()
    return {"message": "Skin concerns updated", "count": len(body.concerns)}
