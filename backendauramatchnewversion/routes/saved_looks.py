from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from models.saved_look import SavedLook
from models.user import User
from routes.auth import get_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/looks", tags=["Saved Looks"])

LOOK_CATEGORIES = ["กลางวัน", "กลางคืน", "ปาร์ตี้", "ทำงาน", "ลุคเกาหลี", "ลุคธรรมชาติ", "อื่นๆ"]


class LookCreate(BaseModel):
    name: str
    category: Optional[str] = None
    makeup_data: dict
    filter_data: Optional[dict] = None


class LookUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None


@router.get("/categories")
def get_look_categories():
    """ดึงหมวดหมู่ลุคที่เลือกได้"""
    return LOOK_CATEGORIES


@router.get("/")
def get_my_looks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """ดึงลุคที่บันทึกไว้ทั้งหมดของผู้ใช้"""
    looks = (
        db.query(SavedLook)
        .filter(SavedLook.user_id == current_user.user_id)
        .order_by(SavedLook.created_at.desc())
        .all()
    )
    return [
        {
            "look_id": l.look_id,
            "name": l.name,
            "category": l.category,
            "makeup_data": l.makeup_data,
            "filter_data": l.filter_data,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in looks
    ]


@router.post("/")
def save_look(
    look: LookCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """บันทึกลุคใหม่"""
    new_look = SavedLook(
        user_id=current_user.user_id,
        name=look.name,
        category=look.category,
        makeup_data=look.makeup_data,
        filter_data=look.filter_data,
    )
    db.add(new_look)
    db.commit()
    db.refresh(new_look)
    return {
        "look_id": new_look.look_id,
        "name": new_look.name,
        "category": new_look.category,
        "message": "บันทึกลุคสำเร็จ",
    }


@router.put("/{look_id}")
def update_look(
    look_id: int,
    look: LookUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """แก้ไขชื่อ/หมวดหมู่ลุค"""
    saved = db.query(SavedLook).filter(
        SavedLook.look_id == look_id,
        SavedLook.user_id == current_user.user_id
    ).first()
    if not saved:
        raise HTTPException(status_code=404, detail="ไม่พบลุคนี้")
    if look.name:
        saved.name = look.name
    if look.category:
        saved.category = look.category
    db.commit()
    return {"message": "แก้ไขสำเร็จ"}


@router.delete("/{look_id}")
def delete_look(
    look_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """ลบลุค"""
    saved = db.query(SavedLook).filter(
        SavedLook.look_id == look_id,
        SavedLook.user_id == current_user.user_id
    ).first()
    if not saved:
        raise HTTPException(status_code=404, detail="ไม่พบลุคนี้")
    db.delete(saved)
    db.commit()
    return {"message": "ลบลุคสำเร็จ"}
