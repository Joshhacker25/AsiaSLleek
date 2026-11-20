import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import Base, engine
from .routes import admin, auth, library, videos
from .seed import seed
app = FastAPI(title="AsiaSLleek API", version="0.1.0", description="Fictional adult video catalogue API. Not production-ready; see README for missing integrations.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router); app.include_router(videos.router); app.include_router(library.router); app.include_router(admin.router)
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine); seed()
@app.get("/health")
def health():
    return {"status": "ok", "service": "asiaslleek", "age_assurance_provider": os.environ.get("AGE_ASSURANCE_PROVIDER_URL", "") or "NOT CONFIGURED", "email_provider": os.environ.get("EMAIL_PROVIDER_URL", "") or "NOT CONFIGURED", "media_storage": "mock (local dev only)"}
@app.get("/api/config")
def config():
    return {"age_gate": True, "age_assurance": "NOT CONFIGURED - connect a provider before any real use", "email": "NOT CONFIGURED", "payments": "NOT CONFIGURED", "storage": "mock"}
if os.path.isdir("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
