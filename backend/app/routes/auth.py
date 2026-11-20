from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..auth import audit, check_password, get_current_user, hash_password, make_token, rate_limit
from ..database import get_db
from ..models import CreatorProfile, User
from ..schemas import LoginIn, RegisterIn, TokenOut, UserOut
router = APIRouter(prefix="/api/auth", tags=["auth"])
@router.post("/register", response_model=TokenOut)
def register(body: RegisterIn, request: Request, db: Session = Depends(get_db)):
    rate_limit(f"reg:{request.client.host}", 10, 3600)
    if db.query(User).filter((User.username == body.username) | (User.email == body.email)).first():
        raise HTTPException(400, "Username or email already in use")
    u = User(username=body.username, email=body.email, password_hash=hash_password(body.password), role="viewer")
    db.add(u); db.commit(); db.refresh(u)
    return TokenOut(access_token=make_token(u.id), user=UserOut.model_validate(u))
@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, request: Request, db: Session = Depends(get_db)):
    rate_limit(f"login:{request.client.host}", 10, 300)
    u = db.query(User).filter(User.username == body.username).first()
    if not u or not check_password(body.password, u.password_hash):
        raise HTTPException(401, "Invalid username or password")
    return TokenOut(access_token=make_token(u.id), user=UserOut.model_validate(u))
@router.post("/logout")
def logout(user: User = Depends(get_current_user)):
    return {"ok": True, "message": "Logged out. Discard the token client-side."}
@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
@router.put("/me", response_model=UserOut)
def update_me(body: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if "email" in body: user.email = body["email"]
    db.commit(); db.refresh(user); return user
@router.post("/creator-profile")
def creator_profile(body: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    p = db.query(CreatorProfile).filter_by(user_id=user.id).first()
    if p:
        p.display_name = body.get("display_name", p.display_name); p.bio = body.get("bio", p.bio)
    else:
        p = CreatorProfile(user_id=user.id, display_name=body.get("display_name", user.username), bio=body.get("bio", ""))
        db.add(p); user.role = "creator"
    db.commit(); return {"ok": True, "display_name": p.display_name, "bio": p.bio, "is_approved": p.is_approved}
