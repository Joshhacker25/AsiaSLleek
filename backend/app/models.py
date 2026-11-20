from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from .database import Base
def now(): return datetime.utcnow()
class Role(Base):
    __tablename__="roles"
    id=Column(Integer,primary_key=True); name=Column(String(50),unique=True,nullable=False)
    description=Column(String(255),default="")
class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True); username=Column(String(50),unique=True,nullable=False)
    email=Column(String(255),unique=True,nullable=False); password_hash=Column(String(255),nullable=False)
    role=Column(String(50),default="viewer"); is_active=Column(Boolean,default=True)
    is_age_assurance_pending=Column(Boolean,default=True); created_at=Column(DateTime,default=now)
    creator=relationship("CreatorProfile",back_populates="user",uselist=False)
class CreatorProfile(Base):
    __tablename__="creator_profiles"
    id=Column(Integer,primary_key=True); user_id=Column(Integer,ForeignKey("users.id"),unique=True)
    display_name=Column(String(100),nullable=False); bio=Column(Text,default="")
    avatar_url=Column(String(500),default=""); is_approved=Column(Boolean,default=False)
    created_at=Column(DateTime,default=now)
    user=relationship("User",back_populates="creator")
    videos=relationship("Video",back_populates="creator")
class Category(Base):
    __tablename__="categories"
    id=Column(Integer,primary_key=True); slug=Column(String(80),unique=True,nullable=False)
    name=Column(String(100),nullable=False); description=Column(Text,default="")
    is_featured=Column(Boolean,default=False); sort_order=Column(Integer,default=0)
class Tag(Base):
    __tablename__="tags"
    id=Column(Integer,primary_key=True); slug=Column(String(80),unique=True,nullable=False)
    name=Column(String(100),nullable=False)
class Video(Base):
    __tablename__="videos"
    id=Column(Integer,primary_key=True); title=Column(String(200),nullable=False)
    description=Column(Text,default=""); language=Column(String(20),default="en")
    category_id=Column(Integer,ForeignKey("categories.id")); creator_id=Column(Integer,ForeignKey("creator_profiles.id"))
    tags=Column(String(500),default=""); duration_seconds=Column(Integer,default=0)
    views=Column(Integer,default=0); status=Column(String(20),default="pending")
    moderator_feedback=Column(Text,default=""); is_featured=Column(Boolean,default=False)
    placeholder_url=Column(String(500),default=""); created_at=Column(DateTime,default=now)
    creator=relationship("CreatorProfile",back_populates="videos")
    category=relationship("Category")
class Playlist(Base):
    __tablename__="playlists"
    id=Column(Integer,primary_key=True); user_id=Column(Integer,ForeignKey("users.id"))
    name=Column(String(100),nullable=False); is_public=Column(Boolean,default=False)
    created_at=Column(DateTime,default=now)
class PlaylistVideo(Base):
    __tablename__="playlist_videos"
    id=Column(Integer,primary_key=True); playlist_id=Column(Integer,ForeignKey("playlists.id"))
    video_id=Column(Integer,ForeignKey("videos.id"))
class WatchHistory(Base):
    __tablename__="watch_history"
    id=Column(Integer,primary_key=True); user_id=Column(Integer,ForeignKey("users.id"))
    video_id=Column(Integer,ForeignKey("videos.id")); watched_at=Column(DateTime,default=now)
    progress_seconds=Column(Integer,default=0)
class Report(Base):
    __tablename__="reports"
    id=Column(Integer,primary_key=True); video_id=Column(Integer,ForeignKey("videos.id"),nullable=True)
    reporter_id=Column(Integer,ForeignKey("users.id"),nullable=True); reason=Column(String(100),nullable=False)
    details=Column(Text,default=""); status=Column(String(20),default="open"); priority=Column(String(20),default="normal")
    reviewer_id=Column(Integer,nullable=True); notes=Column(Text,default=""); decision_reason=Column(Text,default="")
    created_at=Column(DateTime,default=now)
class RemovalRequest(Base):
    __tablename__="removal_requests"
    id=Column(Integer,primary_key=True); video_id=Column(Integer,ForeignKey("videos.id"))
    requester_email=Column(String(255),nullable=False); reason=Column(Text,nullable=False)
    status=Column(String(20),default="open"); created_at=Column(DateTime,default=now)
class Appeal(Base):
    __tablename__="appeals"
    id=Column(Integer,primary_key=True); report_id=Column(Integer,ForeignKey("reports.id"),nullable=True)
    video_id=Column(Integer,ForeignKey("videos.id"),nullable=True); appellant_id=Column(Integer,ForeignKey("users.id"))
    statement=Column(Text,nullable=False); status=Column(String(20),default="open"); created_at=Column(DateTime,default=now)
class ConsentRecord(Base):
    __tablename__="consent_records"
    id=Column(Integer,primary_key=True); video_id=Column(Integer,ForeignKey("videos.id"))
    confirmed_all_adults=Column(Boolean,default=False); confirmed_consent=Column(Boolean,default=False)
    confirmed_rights=Column(Boolean,default=False); created_at=Column(DateTime,default=now)
class PrivateVerificationRecord(Base):
    __tablename__="private_verification_records"
    id=Column(Integer,primary_key=True); user_id=Column(Integer,ForeignKey("users.id"))
    method=Column(String(100),default="age-assurance-provider"); status=Column(String(20),default="pending")
    reference=Column(String(255),default=""); created_at=Column(DateTime,default=now)
    # Never store ID document images or numbers here; only a provider reference.
class ModerationAction(Base):
    __tablename__="moderation_actions"
    id=Column(Integer,primary_key=True); video_id=Column(Integer,ForeignKey("videos.id"),nullable=True)
    moderator_id=Column(Integer,ForeignKey("users.id")); action=Column(String(50),nullable=False)
    reason=Column(Text,nullable=False); created_at=Column(DateTime,default=now)
class AuditLog(Base):
    __tablename__="audit_logs"
    id=Column(Integer,primary_key=True); actor_id=Column(Integer,ForeignKey("users.id"))
    action=Column(String(100),nullable=False); target_type=Column(String(50),default="")
    target_id=Column(Integer,nullable=True); detail=Column(Text,default=""); created_at=Column(DateTime,default=now)
class SiteSetting(Base):
    __tablename__="site_settings"
    id=Column(Integer,primary_key=True); key=Column(String(100),unique=True,nullable=False)
    value=Column(Text,default=""); updated_at=Column(DateTime,default=now)
