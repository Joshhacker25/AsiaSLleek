from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from ..auth import audit, get_current_user, rate_limit, require_roles
from ..database import get_db
from ..models import Category, ConsentRecord, CreatorProfile, Playlist, PlaylistVideo, User, Video, WatchHistory
from ..schemas import PlaylistIn, VideoIn, VideoOut
router = APIRouter(prefix="/api", tags=["videos"])
def video_dict(v):
    return {"id": v.id, "title": v.title, "description": v.description, "language": v.language, "category_id": v.category_id, "creator_id": v.creator_id, "tags": v.tags, "duration_seconds": v.duration_seconds, "views": v.views, "status": v.status, "is_featured": v.is_featured, "created_at": str(v.created_at) if v.created_at else None, "creator_name": v.creator.display_name if v.creator else "", "category_slug": v.category.slug if v.category else ""}
@router.get("/videos")
def list_videos(request: Request, q: str = "", category: str = "", sort: str = "recent", page: int = 1, limit: int = 20, db: Session = Depends(get_db)):
    rate_limit(f"search:{request.client.host}", 60, 60)
    query = db.query(Video).filter(Video.status == "approved")
    if q: query = query.filter(Video.title.ilike(f"%{q}%") | Video.description.ilike(f"%{q}%"))
    if category:
        c = db.query(Category).filter_by(slug=category).first()
        if c: query = query.filter(Video.category_id == c.id)
    if sort == "popular": query = query.order_by(Video.views.desc())
    else: query = query.order_by(Video.created_at.desc())
    total = query.count(); items = query.offset((page-1)*limit).limit(limit).all()
    return {"total": total, "page": page, "limit": limit, "items": [video_dict(v) for v in items]}
@router.get("/videos/{video_id}")
def video_detail(video_id: int, db: Session = Depends(get_db)):
    v = db.get(Video, video_id)
    if not v or v.status != "approved": raise HTTPException(404, "Video not found")
    v.views += 1; db.commit()
    related = db.query(Video).filter(Video.status == "approved", Video.id != v.id).limit(6).all()
    d = video_dict(v); d["related"] = [video_dict(r) for r in related]; return d
@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    return [{"id": c.id, "slug": c.slug, "name": c.name, "description": c.description, "is_featured": c.is_featured} for c in db.query(Category).order_by(Category.sort_order, Category.name).all()]
@router.get("/categories/{slug}")
def category_detail(slug: str, db: Session = Depends(get_db)):
    c = db.query(Category).filter_by(slug=slug).first()
    if not c: raise HTTPException(404, "Category not found")
    return {"id": c.id, "slug": c.slug, "name": c.name, "description": c.description}
@router.get("/creators/{creator_id}")
def creator_detail(creator_id: int, db: Session = Depends(get_db)):
    c = db.get(CreatorProfile, creator_id)
    if not c: raise HTTPException(404, "Creator not found")
    vids = db.query(Video).filter(Video.creator_id == c.id, Video.status == "approved").all()
    return {"id": c.id, "display_name": c.display_name, "bio": c.bio, "is_approved": c.is_approved, "videos": [video_dict(v) for v in vids]}
@router.post("/videos", status_code=201)
def submit_video(body: VideoIn, user: User = Depends(require_roles("creator", "administrator", "super_admin")), db: Session = Depends(get_db)):
    rate_limit(f"upload:{user.id}", 10, 3600)
    if not (body.confirmed_all_adults and body.confirmed_consent and body.confirmed_rights):
        raise HTTPException(400, "All three confirmations are required: every person shown is an adult, consented to recording and distribution, and you hold the rights.")
    creator = db.query(CreatorProfile).filter_by(user_id=user.id).first()
    if not creator: raise HTTPException(400, "Create a creator profile first")
    v = Video(title=body.title, description=body.description, language=body.language, category_id=body.category_id, tags=body.tags, duration_seconds=body.duration_seconds, creator_id=creator.id, status="pending")
    db.add(v); db.commit(); db.refresh(v)
    db.add(ConsentRecord(video_id=v.id, confirmed_all_adults=True, confirmed_consent=True, confirmed_rights=True)); db.commit()
    return {"ok": True, "id": v.id, "status": v.status, "message": "Submitted. It stays private until a moderator approves it."}
@router.get("/my-submissions")
def my_submissions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    creator = db.query(CreatorProfile).filter_by(user_id=user.id).first()
    if not creator: return []
    return [{"id": v.id, "title": v.title, "status": v.status, "moderator_feedback": v.moderator_feedback} for v in db.query(Video).filter_by(creator_id=creator.id).all()]
@router.post("/videos/{video_id}/resubmit")
def resubmit(video_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    creator = db.query(CreatorProfile).filter_by(user_id=user.id).first()
    v = db.get(Video, video_id)
    if not v or not creator or v.creator_id != creator.id: raise HTTPException(404, "Video not found")
    if v.status != "rejected": raise HTTPException(400, "Only rejected videos can be resubmitted")
    v.status = "pending"; v.moderator_feedback = ""; db.commit(); return {"ok": True, "status": "pending"}
