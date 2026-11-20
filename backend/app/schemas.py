from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
class LoginIn(BaseModel):
    username: str; password: str
class UserOut(BaseModel):
    id: int; username: str; email: str; role: str
    class Config: from_attributes = True
class TokenOut(BaseModel):
    access_token: str; token_type: str = "bearer"; user: UserOut
class CategoryIn(BaseModel):
    slug: str; name: str; description: str = ""; is_featured: bool = False
class VideoIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""; language: str = "en"; category_id: int
    tags: str = ""; duration_seconds: int = 0
    confirmed_all_adults: bool; confirmed_consent: bool; confirmed_rights: bool
class VideoOut(BaseModel):
    id: int; title: str; description: str; language: str; category_id: int | None
    creator_id: int | None; tags: str; duration_seconds: int; views: int
    status: str; is_featured: bool; created_at: str | None = None
    class Config: from_attributes = True
class ReportIn(BaseModel):
    video_id: int | None = None; reason: str; details: str = ""
class PlaylistIn(BaseModel):
    name: str = Field(min_length=1, max_length=100); is_public: bool = False
class ModerationIn(BaseModel):
    action: str; reason: str = Field(min_length=1)
