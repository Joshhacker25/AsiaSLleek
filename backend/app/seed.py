from .auth import hash_password
from .database import Base, SessionLocal, engine
from .models import Category, CreatorProfile, Role, SiteSetting, User, Video
CATS = [("documentary", "Documentary", "Fictional documentary-style catalogue entries."), ("music", "Music", "Fictional music performance entries."), ("comedy", "Comedy", "Fictional comedy sketches."), ("lifestyle", "Lifestyle", "Fictional lifestyle entries."), ("education", "Education", "Fictional educational entries.")]
VIDEOS = [("Sunrise Over the Harbour", "A fictional sunrise timelapse story.", "documentary", "Mira Chen", 742, 12840), ("Neon Streets After Rain", "A fictional city-night photo essay.", "documentary", "Mira Chen", 615, 9320), ("Acoustic Sessions: Room 12", "A fictional acoustic performance.", "music", "Theo Alvarez", 428, 15410), ("The Market at Dawn", "A fictional market-day story.", "lifestyle", "Priya Nair", 503, 6210), ("How Tides Work", "A fictional explainer about tides.", "education", "Theo Alvarez", 689, 11020), ("Late Night Sketch Show", "A fictional comedy sketch.", "comedy", "Priya Nair", 372, 8740)]
def seed(db=None):
    db = db or SessionLocal()
    Base.metadata.create_all(bind=engine)
    if db.query(User).first():
        return "already seeded"
    for name, desc in [("viewer", "Can watch, save and report."), ("creator", "Can submit videos."), ("moderator", "Reviews videos and reports."), ("support", "Account support."), ("administrator", "Manages users, creators, categories and content."), ("super_admin", "Manages staff, roles and site configuration.")]:
        db.add(Role(name=name, description=desc))
    users = {}
    for uname, email, role in [("demo_viewer", "viewer@example.test", "viewer"), ("demo_creator", "creator@example.test", "creator"), ("demo_moderator", "moderator@example.test", "moderator"), ("demo_admin", "admin@example.test", "administrator")]:
        u = User(username=uname, email=email, password_hash=hash_password("DemoPass123!"), role=role)
        db.add(u); db.flush(); users[uname] = u
    creators = {}
    for uname, name, bio in [("demo_creator", "Mira Chen", "Fictional creator. Documentary stories."), ("demo_viewer", "Theo Alvarez", "Fictional creator. Music and explainers."), ("demo_moderator", "Priya Nair", "Fictional creator. Lifestyle and comedy.")]:
        c = CreatorProfile(user_id=users[uname].id, display_name=name, bio=bio, is_approved=True)
        db.add(c); db.flush(); creators[name] = c
    catmap = {}
    for slug, name, desc in CATS:
        c = Category(slug=slug, name=name, description=desc, is_featured=slug in ("documentary", "music"))
        db.add(c); db.flush(); catmap[slug] = c
    for i, (title, desc, cat, creator, dur, views) in enumerate(VIDEOS):
        db.add(Video(title=title, description=desc, category_id=catmap[cat].id, creator_id=creators[creator].id, tags="fictional, sample", duration_seconds=dur, views=views, status="approved", is_featured=i < 2))
    for k, v in [("age_assurance_provider", "NOT CONFIGURED"), ("regions", "all"), ("max_upload_mb", "500"), ("retention_days", "365"), ("moderation_rules", "All uploads private until moderator approval.")]:
        db.add(SiteSetting(key=k, value=v))
    db.commit(); return "seeded"
if __name__ == "__main__":
    print(seed())
