from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from config.database import get_db
from models.misc import Banner
from models.user import User
from routes.auth import require_admin
import os, shutil, uuid, math

router = APIRouter(prefix="/banner", tags=["Banner"])

UPLOAD_DIR = os.path.join(os.getenv("UPLOAD_DIR", "uploads"), "banners")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXT = {"jpg", "jpeg", "png", "webp", "gif"}


def serialize_banner(b: Banner):
    return {
        "banner_id": b.banner_id,
        "title": b.title,
        "image_url": b.image_url,
        "link_url": b.link_url,
        "position": b.position,
        "starts_at": b.starts_at.isoformat() if b.starts_at else None,
        "ends_at": b.ends_at.isoformat() if b.ends_at else None,
        "is_active": b.is_active,
        "created_at": b.created_at.isoformat() if b.created_at else None,
    }


def _save_upload(file: UploadFile) -> str:
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail=f"File type .{ext} not allowed")
    filename = f"banner_{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return f"/uploads/banners/{filename}"


def _delete_file(image_url: str):
    if not image_url:
        return
    # image_url is like /uploads/banners/banner_xxx.png
    rel = image_url.lstrip("/")
    try:
        os.remove(rel)
    except OSError:
        pass


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid datetime: {value}")


# ─── Public ───────────────────────────────────────────────

@router.get("/active")
def get_active_banners(
    position: str | None = None,
    db: Session = Depends(get_db),
):
    now = datetime.utcnow()
    q = db.query(Banner).filter(
        Banner.is_active == 1,
        (Banner.starts_at == None) | (Banner.starts_at <= now),
        (Banner.ends_at == None) | (Banner.ends_at >= now),
    )
    if position:
        q = q.filter(Banner.position == position)
    banners = q.order_by(Banner.created_at.desc()).all()
    return [serialize_banner(b) for b in banners]


# ─── Admin ────────────────────────────────────────────────

@router.get("/admin/list")
def admin_list_banners(
    page: int = 1,
    limit: int = 20,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    total = db.query(func.count(Banner.banner_id)).scalar()
    banners = (
        db.query(Banner)
        .order_by(Banner.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return {
        "banners": [serialize_banner(b) for b in banners],
        "total": total,
        "page": page,
        "pages": math.ceil(total / limit) if limit else 1,
    }


@router.post("/admin", status_code=201)
def admin_create_banner(
    file: UploadFile = File(...),
    title: str = Form(None),
    link_url: str = Form(None),
    position: str = Form("home_top"),
    starts_at: str = Form(None),
    ends_at: str = Form(None),
    is_active: int = Form(1),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    image_url = _save_upload(file)
    banner = Banner(
        title=title,
        image_url=image_url,
        link_url=link_url,
        position=position,
        starts_at=_parse_dt(starts_at),
        ends_at=_parse_dt(ends_at),
        is_active=is_active,
    )
    db.add(banner)
    db.commit()
    db.refresh(banner)
    return serialize_banner(banner)


@router.put("/admin/{banner_id}")
def admin_update_banner(
    banner_id: int,
    file: UploadFile = File(None),
    title: str = Form(None),
    link_url: str = Form(None),
    position: str = Form(None),
    starts_at: str = Form(None),
    ends_at: str = Form(None),
    is_active: int = Form(None),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    banner = db.query(Banner).filter(Banner.banner_id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")

    if file:
        _delete_file(banner.image_url)
        banner.image_url = _save_upload(file)
    if title is not None:
        banner.title = title
    if link_url is not None:
        banner.link_url = link_url
    if position is not None:
        banner.position = position
    if starts_at is not None:
        banner.starts_at = _parse_dt(starts_at)
    if ends_at is not None:
        banner.ends_at = _parse_dt(ends_at)
    if is_active is not None:
        banner.is_active = is_active

    db.commit()
    db.refresh(banner)
    return serialize_banner(banner)


@router.delete("/admin/{banner_id}")
def admin_delete_banner(
    banner_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    banner = db.query(Banner).filter(Banner.banner_id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    _delete_file(banner.image_url)
    db.delete(banner)
    db.commit()
    return {"detail": "Banner deleted"}


@router.patch("/admin/{banner_id}/toggle")
def admin_toggle_banner(
    banner_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    banner = db.query(Banner).filter(Banner.banner_id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    banner.is_active = 0 if banner.is_active else 1
    db.commit()
    db.refresh(banner)
    return serialize_banner(banner)
