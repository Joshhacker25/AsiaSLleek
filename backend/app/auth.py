import hashlib, hmac, os, secrets, time
from collections import defaultdict
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import AuditLog, User
SECRET = os.environ.get("SECRET_KEY", "dev-secret-change-me")
_tokens = {}
_attempts = defaultdict(list)
def hash_password(pw, salt=None):
    salt = salt or secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 200000).hex()
    return f"{salt}${h}"
def check_password(pw, stored):
    try:
        salt, h = stored.split("$")
        return hmac.compare_digest(h, hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 200000).hex())
    except Exception:
        return False
def make_token(user_id):
    t = secrets.token_urlsafe(32); _tokens[t] = user_id; return t
def rate_limit(key, limit, window=60):
    now = time.time(); _attempts[key] = [x for x in _attempts[key] if now - x < window]
    if len(_attempts[key]) >= limit:
        raise HTTPException(429, "Too many requests. Please try again later.")
    _attempts[key].append(now)
bearer = HTTPBearer(auto_error=False)
def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    if not creds or creds.credentials not in _tokens:
        raise HTTPException(401, "Authentication required")
    u = db.get(User, _tokens[creds.credentials])
    if not u or not u.is_active:
        raise HTTPException(401, "Authentication required")
    return u
def require_roles(*roles):
    def _check(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(403, "Insufficient permissions")
        return user
    return _check
def audit(db, actor_id, action, target_type="", target_id=None, detail=""):
    db.add(AuditLog(actor_id=actor_id, action=action, target_type=target_type, target_id=target_id, detail=detail)); db.commit()
