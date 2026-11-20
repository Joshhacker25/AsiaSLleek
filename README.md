# AsiaSLleek

AsiaSLleek — fresh start. A fictional, local-first adult video catalogue (adults only). Original product only; a well-known video platform was used only as general inspiration for common video-platform features. No logo, brand, text, images, source code, or page design was copied.

**Not production-ready and not legally compliant as-is.** See Limitations below.

## What it is

- Frontend: plain HTML5, CSS3, vanilla JavaScript only. No framework, no build step. Pages in `frontend/`, shared header/footer/video-card in `frontend/js/app.js`, styles in `frontend/css/main.css`.
- Backend: Python FastAPI + SQLAlchemy + SQLite (local). JSON REST API in `backend/app/`. Config is replaceable for PostgreSQL later via `DATABASE_URL`.
- All sample data is fictional. No real or explicit videos or images — video pages show a neutral placeholder only.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python -m backend.app.seed  # creates asiaslleek.db with fictional data (also runs on startup)
uvicorn backend.app.main:app --reload --port 8000
```

Then open http://localhost:8000/ — the API also serves the frontend. Or serve the frontend separately with `python3 -m http.server 3000 --directory frontend` and open http://localhost:3000/ (API at http://localhost:8000).

## Fictional dev accounts (password: DemoPass123!)

- `demo_viewer` — viewer
- `demo_creator` — creator
- `demo_moderator` — moderator
- `demo_admin` — administrator

These are fictional test accounts only. Change or remove them before any real use. No real credentials are in this repo.

## API

See `docs/api.md`. Highlights: `GET /health`, `GET /api/videos`, `GET /api/categories`, `GET /api/videos/{id}`, `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/videos` (creator submission, stays private until approved), `GET /api/my-submissions`, `POST /api/reports`, `POST /api/removal-requests`, `POST /api/appeals`, `GET /api/library`, playlists and watch history, and `/api/admin/*` (dashboard, review queue, reports, appeals, users, categories, settings, audit log).

## Safety and moderation

- Adults only. An age-access screen is shown, but an "I am over 18" click is **not** legal age verification. Age assurance is **NOT CONFIGURED** — connect a provider via `AGE_ASSURANCE_PROVIDER_URL` / `AGE_ASSURANCE_API_KEY` before any real use.
- Every upload stays private (`status=pending`) until a moderator approves it. Uploaders must confirm every person shown is an adult, consented to recording and distribution, and that they hold the rights.
- Reporting, content-removal requests, and appeals are built in. Prohibited: minors or uncertain age, non-consensual, hidden-camera, impersonation, trafficking, stolen, or other unlawful material.
- Sensitive verification records (`PrivateVerificationRecord`) are kept separate from public creator profiles and are never seeded with real ID documents or personal data.
- Secrets go in environment variables only — see `backend/.env.example` (names only). Never commit `.env` or real secrets.

## Admin roles

- Moderator: review videos and reports. Support: account support. Administrator: users, creators, categories, content. Super administrator: staff roles and site configuration. Permissions are enforced in the backend, not just by hiding buttons. Sensitive admin actions are written to an append-only audit log (`AuditLog`).

## Limitations — still required before any real use

- Age-assurance provider: NOT CONFIGURED.
- Email provider: NOT CONFIGURED (no account emails, no removal-request emails).
- Payment provider: NOT CONFIGURED (no payments are implemented).
- Media storage/CDN: mock only in local dev — no real media is stored or streamed.
- Legal review, content-moderation staffing, privacy review, and security review: NOT DONE. This project must not be presented as production-ready or legally compliant.

## File structure

```
frontend/ index.html search.html category.html video.html creator.html login.html register.html library.html account.html help.html creator-dashboard.html admin/ css/ js/ assets/
backend/ app/ main.py database.py models.py schemas.py auth.py seed.py routes/ services/ requirements.txt .env.example
docs/api.md
```
