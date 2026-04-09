import re
import time
from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, validator
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from config.database import get_db
from models.blog import BlogCategory, BlogPost
from models.user import User
from routes.auth import get_current_user, require_admin

router = APIRouter(prefix="/blog", tags=["Blog"])


_VIEW_COOLDOWN = 3600  # 1 hour in seconds
_view_timestamps: dict[str, float] = defaultdict(float)


def generate_slug(title: str) -> str:
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = slug.strip("-")
    suffix = hex(int(time.time()))[2:][-6:]
    return f"{slug}-{suffix}" if slug else suffix


# ── Pydantic schemas ──────────────────────────────────────────────────────

def _validate_thumbnail_url(url: Optional[str]) -> Optional[str]:
    if url is not None and url != "" and not url.startswith(("https://", "http://")):
        raise ValueError("thumbnail_url must start with https:// or http://")
    return url or None


class PostCreate(BaseModel):
    title: str
    category_id: Optional[int] = None
    content: str = ""
    thumbnail_url: Optional[str] = None
    is_published: int = 0

    _check_url = validator("thumbnail_url", allow_reuse=True, pre=True)(_validate_thumbnail_url)


class PostUpdate(BaseModel):
    title: Optional[str] = None
    category_id: Optional[int] = None
    content: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_published: Optional[int] = None

    _check_url = validator("thumbnail_url", allow_reuse=True, pre=True)(_validate_thumbnail_url)


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


# ── Serializers ───────────────────────────────────────────────────────────

def serialize_post(post: BlogPost, *, full: bool = False):
    data = {
        "post_id": post.post_id,
        "title": post.title,
        "slug": post.slug,
        "category": {
            "category_id": post.category.category_id,
            "name": post.category.name,
        } if post.category else None,
        "author": post.author.username if post.author else None,
        "thumbnail_url": post.thumbnail_url,
        "views": post.views,
        "is_published": post.is_published,
        "published_at": post.published_at.isoformat() if post.published_at else None,
        "created_at": post.created_at.isoformat() if post.created_at else None,
    }
    if full:
        data["content"] = post.content
        data["category_id"] = post.category_id
        data["updated_at"] = post.updated_at.isoformat() if post.updated_at else None
    else:
        data["excerpt"] = (post.content or "")[:120]
    return data


# ── Public endpoints ──────────────────────────────────────────────────────

@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    cats = db.query(BlogCategory).order_by(BlogCategory.name).all()
    return [
        {
            "category_id": c.category_id,
            "name": c.name,
            "description": c.description,
        }
        for c in cats
    ]


@router.get("/posts")
def list_published_posts(
    category_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
):
    q = (
        db.query(BlogPost)
        .options(joinedload(BlogPost.category), joinedload(BlogPost.author))
        .filter(BlogPost.is_published == 1)
    )
    if category_id:
        q = q.filter(BlogPost.category_id == category_id)

    total = q.count()
    posts = (
        q.order_by(BlogPost.published_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "posts": [serialize_post(p) for p in posts],
        "total": total,
        "page": page,
        "pages": max(1, -(-total // limit)),
    }


@router.get("/posts/{slug}")
def get_post_by_slug(slug: str, db: Session = Depends(get_db)):
    post = (
        db.query(BlogPost)
        .options(joinedload(BlogPost.category), joinedload(BlogPost.author))
        .filter(BlogPost.slug == slug, BlogPost.is_published == 1)
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return serialize_post(post, full=True)


@router.patch("/posts/{slug}/view")
def increment_view(slug: str, request: Request, db: Session = Depends(get_db)):
    post = db.query(BlogPost).filter(BlogPost.slug == slug).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    client_ip = request.client.host if request.client else "unknown"
    key = f"{client_ip}:{slug}"
    now = time.time()
    if now - _view_timestamps[key] < _VIEW_COOLDOWN:
        return {"views": post.views}

    _view_timestamps[key] = now
    post.views = (post.views or 0) + 1
    db.commit()
    return {"views": post.views}


# ── Admin endpoints ───────────────────────────────────────────────────────

@router.get("/admin/posts")
def admin_list_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    q = (
        db.query(BlogPost)
        .options(joinedload(BlogPost.category), joinedload(BlogPost.author))
    )
    total = q.count()
    posts = (
        q.order_by(BlogPost.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return {
        "posts": [serialize_post(p) for p in posts],
        "total": total,
        "page": page,
        "pages": max(1, -(-total // limit)),
    }


@router.post("/admin/posts", status_code=201)
def create_post(
    body: PostCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    from datetime import datetime

    post = BlogPost(
        title=body.title,
        slug=generate_slug(body.title),
        category_id=body.category_id,
        content=body.content,
        thumbnail_url=body.thumbnail_url,
        author_id=admin.user_id,
        is_published=body.is_published,
        published_at=datetime.utcnow() if body.is_published else None,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return serialize_post(post, full=True)


@router.put("/admin/posts/{post_id}")
def update_post(
    post_id: int,
    body: PostUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    from datetime import datetime

    post = db.query(BlogPost).filter(BlogPost.post_id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    update_data = body.dict(exclude_unset=True)
    if "title" in update_data:
        post.title = update_data["title"]
        post.slug = generate_slug(update_data["title"])
    if "category_id" in update_data:
        post.category_id = update_data["category_id"]
    if "content" in update_data:
        post.content = update_data["content"]
    if "thumbnail_url" in update_data:
        post.thumbnail_url = update_data["thumbnail_url"]
    if "is_published" in update_data:
        was_published = post.is_published
        post.is_published = update_data["is_published"]
        if update_data["is_published"] and not was_published:
            post.published_at = datetime.utcnow()

    db.commit()
    db.refresh(post)

    # Reload relationships
    post = (
        db.query(BlogPost)
        .options(joinedload(BlogPost.category), joinedload(BlogPost.author))
        .filter(BlogPost.post_id == post_id)
        .first()
    )
    return serialize_post(post, full=True)


@router.delete("/admin/posts/{post_id}")
def delete_post(
    post_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    post = db.query(BlogPost).filter(BlogPost.post_id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"message": "Post deleted"}


@router.post("/admin/categories", status_code=201)
def create_category(
    body: CategoryCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    cat = BlogCategory(name=body.name, description=body.description)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return {
        "category_id": cat.category_id,
        "name": cat.name,
        "description": cat.description,
    }


@router.put("/admin/categories/{category_id}")
def update_category(
    category_id: int,
    body: CategoryCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    cat = db.query(BlogCategory).filter(BlogCategory.category_id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    cat.name = body.name
    cat.description = body.description
    db.commit()
    db.refresh(cat)
    return {
        "category_id": cat.category_id,
        "name": cat.name,
        "description": cat.description,
    }


@router.delete("/admin/categories/{category_id}")
def delete_category(
    category_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    cat = db.query(BlogCategory).filter(BlogCategory.category_id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
    return {"message": "Category deleted"}
