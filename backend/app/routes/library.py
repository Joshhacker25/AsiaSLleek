from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..auth import get_current_user, rate_limit
from ..database import get_db
from ..models import Playlist, PlaylistVideo, RemovalRequest, Report, User, Video, WatchHistory, Appeal
from ..schemas import PlaylistIn, ReportIn
from .videos import video_dict
router = APIRouter(prefix="/api", tags=["library"])
@router.get("/library")
def library(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hist = db.query(WatchHistory).filter_by(user_id=user.id).order_by(WatchHistory.watched_at.desc()).limit(50).all()
    pls = db.query(Playlist).filter_by(user_id=user.id).all()
    return {"history": [{"video_id": h.video_id, "progress_seconds": h.progress_seconds} for h in hist], "playlists": [{"id": p.id, "name": p.name, "is_public": p.is_public} for p in pls]}
@router.post("/history")
def add_history(body: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.add(WatchHistory(user_id=user.id, video_id=body["video_id"], progress_seconds=body.get("progress_seconds", 0))); db.commit(); return {"ok": True}
@router.post("/playlists", status_code=201)
def create_playlist(body: PlaylistIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    p = Playlist(user_id=user.id, name=body.name, is_public=body.is_public); db.add(p); db.commit(); db.refresh(p); return {"id": p.id, "name": p.name}
@router.post("/playlists/{pid}/videos")
def add_to_playlist(pid: int, body: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    p = db.query(Playlist).filter_by(id=pid, user_id=user.id).first()
    if not p: raise HTTPException(404, "Playlist not found")
    db.add(PlaylistVideo(playlist_id=pid, video_id=body["video_id"])); db.commit(); return {"ok": True}
@router.post("/reports", status_code=201)
def create_report(body: ReportIn, request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rate_limit(f"report:{user.id}", 20, 3600)
    r = Report(video_id=body.video_id, reporter_id=user.id, reason=body.reason, details=body.details)
    db.add(r); db.commit(); db.refresh(r); return {"id": r.id, "status": r.status}
@router.post("/removal-requests", status_code=201)
def removal(body: dict, db: Session = Depends(get_db)):
    r = RemovalRequest(video_id=body["video_id"], requester_email=body["requester_email"], reason=body["reason"])
    db.add(r); db.commit(); return {"ok": True, "message": "Removal request received. It will be reviewed by a moderator."}
@router.post("/appeals", status_code=201)
def appeal(body: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    a = Appeal(video_id=body.get("video_id"), report_id=body.get("report_id"), appellant_id=user.id, statement=body["statement"])
    db.add(a); db.commit(); return {"ok": True, "message": "Appeal submitted."}
