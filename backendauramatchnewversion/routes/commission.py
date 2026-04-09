from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from jose import jwt
from config.database import get_db
from models.commission import ClickLog, Commission
from models.product import ProductLink
from routes.auth import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/commission", tags=["Commission"])


@router.post("/click/{link_id}")
def track_click(link_id: int, request: Request, db: Session = Depends(get_db)):
    link = db.query(ProductLink).filter(ProductLink.link_id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    # Extract user_id from auth token (optional — unauthenticated clicks still tracked)
    user_id = None
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        try:
            payload = jwt.decode(auth[7:], SECRET_KEY, algorithms=[ALGORITHM])
            user_id = int(payload.get("sub"))
        except Exception:
            pass

    log = ClickLog(
        link_id=link_id,
        user_id=user_id,
        platform=link.platform,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(log)
    db.commit()
    return {"redirect_url": link.url}


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_clicks = db.query(func.count(ClickLog.log_id)).scalar()

    clicks_rows = db.query(
        ClickLog.platform,
        func.count(ClickLog.log_id).label("clicks")
    ).group_by(ClickLog.platform).all()

    commission_rows = db.query(
        Commission.platform,
        func.sum(Commission.amount).label("total")
    ).group_by(Commission.platform).all()

    commission_map = {r[0]: float(r[1] or 0) for r in commission_rows}

    by_platform = {}
    for platform, clicks in clicks_rows:
        by_platform[platform] = {
            "clicks": clicks,
            "commission": commission_map.get(platform, 0),
        }

    total_commission = db.query(func.sum(Commission.amount)).scalar() or 0
    by_status = db.query(
        Commission.status,
        func.sum(Commission.amount).label("total")
    ).group_by(Commission.status).all()

    return {
        "total_clicks": total_clicks,
        "total_commission": float(total_commission),
        "by_platform": by_platform,
        "commission_by_status": [{"status": r[0], "total": float(r[1] or 0)} for r in by_status],
    }
