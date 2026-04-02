from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from config.database import get_db
from models.commission import ClickLog, Commission
from models.product import ProductLink

router = APIRouter(prefix="/commission", tags=["Commission"])


@router.post("/click/{link_id}")
def track_click(link_id: int, user_id: int = None, request: Request = None, db: Session = Depends(get_db)):
    link = db.query(ProductLink).filter(ProductLink.link_id == link_id).first()
    if not link:
        return {"error": "Link not found"}

    log = ClickLog(
        link_id=link_id,
        user_id=user_id,
        platform=link.platform,
        ip_address=request.client.host if request else None
    )
    db.add(log)
    db.commit()
    return {"redirect_url": link.url}


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_clicks = db.query(func.count(ClickLog.log_id)).scalar()
    by_platform = db.query(
        ClickLog.platform,
        func.count(ClickLog.log_id).label("clicks")
    ).group_by(ClickLog.platform).all()

    total_commission = db.query(func.sum(Commission.amount)).scalar() or 0
    by_status = db.query(
        Commission.status,
        func.sum(Commission.amount).label("total")
    ).group_by(Commission.status).all()

    return {
        "total_clicks": total_clicks,
        "clicks_by_platform": [{"platform": r[0], "clicks": r[1]} for r in by_platform],
        "total_commission": float(total_commission),
        "commission_by_status": [{"status": r[0], "total": float(r[1] or 0)} for r in by_status]
    }
