from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..auth import audit, require_roles
from ..database import get_db
from ..models import Appeal, AuditLog, Category, CreatorProfile, ModerationAction, RemovalRequest, Report, SiteSetting, User, Video
from ..schemas import CategoryIn, ModerationIn
router = APIRouter(prefix="/api/admin", tags=["admin"])
Mod = require_roles("moderator", "administrator", "super_admin")
Admin = require_roles("administrator", "super_admin")
Super = require_roles("super_admin")
@router.get("/dashboard")
def dashboard(user=Depends(Mod), db: Session = Depends(get_db)):
    return {"pending_reviews": db.query(Video).filter_by(status="pending").count(), "open_reports": db.query(Report).filter_by(status="open").count(), "removal_requests": db.query(RemovalRequest).filter_by(status="open").count(), "open_appeals": db.query(Appeal).filter_by(status="open").count(), "total_users": db.query(User).count(), "total_videos": db.query(Video).count()}
@router.get("/queue")
def queue(user=Depends(Mod), db: Session = Depends(get_db)):
    return [{"id": v.id, "title": v.title, "description": v.description, "status": v.status, "creator_id": v.creator_id} for v in db.query(Video).filter_by(status="pending").all()]
@router.post("/videos/{vid}/moderate")
def moderate(vid: int, body: ModerationIn, user=Depends(Mod), db: Session = Depends(get_db)):
    v = db.get(Video, vid)
    if not v: raise HTTPException(404, "Video not found")
    if body.action not in ("approve", "reject", "request-changes", "restrict", "remove"):
        raise HTTPException(400, "Invalid action")
    if body.action in ("reject", "remove") and not body.reason.strip():
        raise HTTPException(400, "A written reason is required for this action")
    mapping = {"approve": "approved", "reject": "rejected", "request-changes": "changes_requested", "restrict": "restricted", "remove": "removed"}
    v.status = mapping[body.action]; v.moderator_feedback = body.reason
    db.add(ModerationAction(video_id=vid, moderator_id=user.id, action=body.action, reason=body.reason)); db.commit()
    audit(db, user.id, f"moderate:{body.action}", "video", vid, body.reason)
    return {"ok": True, "status": v.status}
@router.get("/reports")
def reports(user=Depends(Mod), db: Session = Depends(get_db)):
    return [{"id": r.id, "video_id": r.video_id, "reason": r.reason, "details": r.details, "status": r.status, "priority": r.priority, "notes": r.notes} for r in db.query(Report).all()]
@router.post("/reports/{rid}")
def decide_report(rid: int, body: dict, user=Depends(Mod), db: Session = Depends(get_db)):
    r = db.get(Report, rid)
    if not r: raise HTTPException(404, "Report not found")
    r.status = body.get("status", r.status); r.notes = body.get("notes", r.notes); r.decision_reason = body.get("decision_reason", r.decision_reason); r.reviewer_id = user.id
    db.commit(); audit(db, user.id, "report-decision", "report", rid, r.decision_reason); return {"ok": True, "status": r.status}
@router.get("/appeals")
def appeals(user=Depends(Mod), db: Session = Depends(get_db)):
    return [{"id": a.id, "video_id": a.video_id, "statement": a.statement, "status": a.status} for a in db.query(Appeal).all()]
@router.post("/appeals/{aid}")
def decide_appeal(aid: int, body: dict, user=Depends(Mod), db: Session = Depends(get_db)):
    a = db.get(Appeal, aid)
    if not a: raise HTTPException(404, "Appeal not found")
    a.status = body.get("status", a.status); db.commit(); audit(db, user.id, "appeal-decision", "appeal", aid, a.status); return {"ok": True, "status": a.status}
@router.get("/users")
def users(user=Depends(Admin), db: Session = Depends(get_db)):
    return [{"id": u.id, "username": u.username, "email": u.email, "role": u.role, "is_active": u.is_active} for u in db.query(User).all()]
@router.post("/users/{uid}/role")
def set_role(uid: int, body: dict, user=Depends(Super), db: Session = Depends(get_db)):
    u = db.get(User, uid)
    if not u: raise HTTPException(404, "User not found")
    u.role = body["role"]; db.commit(); audit(db, user.id, "set-role", "user", uid, body["role"]); return {"ok": True, "role": u.role}
@router.post("/categories", status_code=201)
def create_category(body: CategoryIn, user=Depends(Admin), db: Session = Depends(get_db)):
    c = Category(slug=body.slug, name=body.name, description=body.description, is_featured=body.is_featured); db.add(c); db.commit(); audit(db, user.id, "create-category", "category", c.id, body.name); return {"id": c.id, "slug": c.slug}
@router.get("/settings")
def settings(user=Depends(Admin), db: Session = Depends(get_db)):
    return {s.key: s.value for s in db.query(SiteSetting).all()}
@router.post("/settings")
def set_setting(body: dict, user=Depends(Super), db: Session = Depends(get_db)):
    s = db.query(SiteSetting).filter_by(key=body["key"]).first()
    if s: s.value = body["value"]
    else: db.add(SiteSetting(key=body["key"], value=body["value"]))
    db.commit(); audit(db, user.id, "set-setting", "site_setting", None, body["key"]); return {"ok": True}
@router.get("/audit-log")
def audit_log(user=Depends(Admin), db: Session = Depends(get_db)):
    return [{"id": a.id, "actor_id": a.actor_id, "action": a.action, "target_type": a.target_type, "target_id": a.target_id, "detail": a.detail, "created_at": str(a.created_at)} for a in db.query(AuditLog).order_by(AuditLog.id.desc()).limit(200).all()]
