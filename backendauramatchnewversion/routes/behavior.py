from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from config.database import get_db
from models.behavior import UserBehavior
from routes.auth import get_current_user, require_admin, security
from models.user import User
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/behavior", tags=["Behavior Analytics"])


class BehaviorEvent(BaseModel):
    event_type: str
    event_data: Optional[dict] = None
    page: Optional[str] = None
    session_id: Optional[str] = None


@router.post("/track")
def track_event(
    event: BehaviorEvent,
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    """บันทึกพฤติกรรมผู้ใช้"""
    user_id = None
    if credentials:
        try:
            from jose import jwt
            import os
            payload = jwt.decode(
                credentials.credentials,
                os.getenv("SECRET_KEY", "secret"),
                algorithms=[os.getenv("ALGORITHM", "HS256")]
            )
            user_id = int(payload.get("sub"))
        except Exception:
            pass

    behavior = UserBehavior(
        user_id=user_id,
        session_id=event.session_id,
        event_type=event.event_type,
        event_data=event.event_data,
        page=event.page,
    )
    db.add(behavior)
    db.commit()
    return {"status": "tracked"}


@router.post("/track-batch")
def track_batch(
    events: list[BehaviorEvent],
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    """บันทึกหลาย events พร้อมกัน"""
    user_id = None
    if credentials:
        try:
            from jose import jwt
            import os
            payload = jwt.decode(
                credentials.credentials,
                os.getenv("SECRET_KEY", "secret"),
                algorithms=[os.getenv("ALGORITHM", "HS256")]
            )
            user_id = int(payload.get("sub"))
        except Exception:
            pass

    for event in events:
        behavior = UserBehavior(
            user_id=user_id,
            session_id=event.session_id,
            event_type=event.event_type,
            event_data=event.event_data,
            page=event.page,
        )
        db.add(behavior)
    db.commit()
    return {"status": "tracked", "count": len(events)}


# ═══════════════════════════════════════
# Admin Analytics Endpoints
# ═══════════════════════════════════════

@router.get("/analytics/summary")
def get_analytics_summary(
    days: int = 30,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """สรุปภาพรวม analytics"""
    since = datetime.utcnow() - timedelta(days=days)
    base = db.query(UserBehavior).filter(UserBehavior.created_at >= since)

    total_events = base.count()
    unique_users = base.filter(UserBehavior.user_id.isnot(None)).distinct(UserBehavior.user_id).count()
    unique_sessions = base.filter(UserBehavior.session_id.isnot(None)).distinct(UserBehavior.session_id).count()

    # Event breakdown
    event_counts = (
        base.with_entities(UserBehavior.event_type, func.count().label('count'))
        .group_by(UserBehavior.event_type)
        .order_by(desc('count'))
        .all()
    )

    return {
        "period_days": days,
        "total_events": total_events,
        "unique_users": unique_users,
        "unique_sessions": unique_sessions,
        "event_breakdown": [{"event": e[0], "count": e[1]} for e in event_counts],
    }


@router.get("/analytics/top-products")
def get_top_products(
    days: int = 30,
    limit: int = 10,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """สินค้าที่ถูกดูมากที่สุด"""
    since = datetime.utcnow() - timedelta(days=days)

    results = (
        db.query(UserBehavior)
        .filter(
            UserBehavior.created_at >= since,
            UserBehavior.event_type == 'product_view',
        )
        .with_entities(
            func.json_extract(UserBehavior.event_data, '$.product_id').label('product_id'),
            func.json_extract(UserBehavior.event_data, '$.product_name').label('product_name'),
            func.count().label('views'),
        )
        .group_by('product_id', 'product_name')
        .order_by(desc('views'))
        .limit(limit)
        .all()
    )

    return [{"product_id": r[0], "product_name": r[1], "views": r[2]} for r in results]


@router.get("/analytics/top-searches")
def get_top_searches(
    days: int = 30,
    limit: int = 20,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """คำค้นหายอดนิยม"""
    since = datetime.utcnow() - timedelta(days=days)

    results = (
        db.query(UserBehavior)
        .filter(
            UserBehavior.created_at >= since,
            UserBehavior.event_type == 'search',
        )
        .with_entities(
            func.json_extract(UserBehavior.event_data, '$.query').label('search_query'),
            func.count().label('count'),
        )
        .group_by('search_query')
        .order_by(desc('count'))
        .limit(limit)
        .all()
    )

    return [{"query": r[0], "count": r[1]} for r in results]


@router.get("/analytics/filter-usage")
def get_filter_usage(
    days: int = 30,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """สถิติการใช้ตัวกรอง"""
    since = datetime.utcnow() - timedelta(days=days)

    results = (
        db.query(UserBehavior)
        .filter(
            UserBehavior.created_at >= since,
            UserBehavior.event_type == 'filter',
        )
        .with_entities(
            func.json_extract(UserBehavior.event_data, '$.filter_type').label('filter_type'),
            func.json_extract(UserBehavior.event_data, '$.filter_value').label('filter_value'),
            func.count().label('count'),
        )
        .group_by('filter_type', 'filter_value')
        .order_by(desc('count'))
        .all()
    )

    return [{"filter_type": r[0], "filter_value": r[1], "count": r[2]} for r in results]


@router.get("/analytics/makeup-behavior")
def get_makeup_behavior(
    days: int = 30,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """พฤติกรรมการแต่งหน้า"""
    since = datetime.utcnow() - timedelta(days=days)

    # สีที่เลือกบ่อย
    color_results = (
        db.query(UserBehavior)
        .filter(
            UserBehavior.created_at >= since,
            UserBehavior.event_type == 'makeup_select',
        )
        .with_entities(
            func.json_extract(UserBehavior.event_data, '$.part').label('part'),
            func.json_extract(UserBehavior.event_data, '$.color').label('color'),
            func.count().label('count'),
        )
        .group_by('part', 'color')
        .order_by(desc('count'))
        .limit(20)
        .all()
    )

    # Preset ยอดนิยม
    preset_results = (
        db.query(UserBehavior)
        .filter(
            UserBehavior.created_at >= since,
            UserBehavior.event_type == 'preset_apply',
        )
        .with_entities(
            func.json_extract(UserBehavior.event_data, '$.preset_name').label('preset_name'),
            func.count().label('count'),
        )
        .group_by('preset_name')
        .order_by(desc('count'))
        .all()
    )

    return {
        "popular_colors": [{"part": r[0], "color": r[1], "count": r[2]} for r in color_results],
        "popular_presets": [{"preset": r[0], "count": r[1]} for r in preset_results],
    }


@router.get("/analytics/personal-color-demand")
def get_personal_color_demand(
    days: int = 30,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """ความต้องการตาม personal color"""
    since = datetime.utcnow() - timedelta(days=days)

    results = (
        db.query(UserBehavior)
        .filter(
            UserBehavior.created_at >= since,
            UserBehavior.event_type == 'filter',
            func.json_extract(UserBehavior.event_data, '$.filter_type') == 'personal_color',
        )
        .with_entities(
            func.json_extract(UserBehavior.event_data, '$.filter_value').label('season'),
            func.count().label('count'),
        )
        .group_by('season')
        .order_by(desc('count'))
        .all()
    )

    return [{"season": r[0], "count": r[1]} for r in results]


@router.get("/analytics/click-funnel")
def get_click_funnel(
    days: int = 30,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Conversion funnel: ดูสินค้า → กดลิงก์ซื้อ"""
    since = datetime.utcnow() - timedelta(days=days)
    base = db.query(UserBehavior).filter(UserBehavior.created_at >= since)

    views = base.filter(UserBehavior.event_type == 'product_view').count()
    similar_views = base.filter(UserBehavior.event_type == 'similar_view').count()
    clicks = base.filter(UserBehavior.event_type == 'click').count()

    return {
        "product_views": views,
        "similar_views": similar_views,
        "purchase_clicks": clicks,
        "view_to_click_rate": round(clicks / views * 100, 2) if views > 0 else 0,
    }
