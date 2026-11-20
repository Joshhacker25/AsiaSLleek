# AsiaSLleek API

Base URL (local): `http://localhost:8000`. Interactive docs: `http://localhost:8000/docs`. All responses are JSON. Auth: `Authorization: Bearer <token>` from login/register.

## Public

- `GET /health` — `{status: ok, ...}` plus which integrations are NOT CONFIGURED.
- `GET /api/config` — age-gate / email / payment / storage configuration status.
- `GET /api/videos?q=&category=&sort=recent|popular&page=1&limit=20` — approved videos only.
- `GET /api/videos/{id}` — video detail + related videos.
- `GET /api/categories` and `GET /api/categories/{slug}`
- `GET /api/creators/{id}` — creator profile + approved videos.

## Auth

- `POST /api/auth/register` `{username, email, password}` — returns token + user.
- `POST /api/auth/login` `{username, password}` — returns token + user.
- `POST /api/auth/logout`, `GET /api/auth/me`, `PUT /api/auth/me`, `POST /api/auth/creator-profile`

Rate limits: login 10 per 5 min per IP, registration 10 per hour, search 60 per min, reports 20 per hour, uploads 10 per hour.

## Creator (role creator+)

- `POST /api/videos` — submit a video. Requires `confirmed_all_adults`, `confirmed_consent`, `confirmed_rights` all true. Status is `pending` (private) until a moderator approves it.
- `GET /api/my-submissions`, `POST /api/videos/{id}/resubmit` (rejected only).

## Library (signed in)

- `GET /api/library` — watch history + playlists (your records only).
- `POST /api/history`, `POST /api/playlists`, `POST /api/playlists/{id}/videos`

## Reports / removal / appeals

- `POST /api/reports` `{video_id, reason, details}` (signed in)
- `POST /api/removal-requests` `{video_id, requester_email, reason}`
- `POST /api/appeals` `{video_id, report_id, statement}` (signed in)

## Admin (backend-enforced roles)

- `GET /api/admin/dashboard` — pending reviews, open reports, removal requests, appeals, totals.
- `GET /api/admin/queue`, `POST /api/admin/videos/{id}/moderate` `{action: approve|reject|request-changes|restrict|remove, reason}` — a written reason is required for reject/remove.
- `GET /api/admin/reports`, `POST /api/admin/reports/{id}` — status, notes, decision reason.
- `GET /api/admin/appeals`, `POST /api/admin/appeals/{id}`
- `GET /api/admin/users`, `POST /api/admin/users/{id}/role` (super admin only)
- `POST /api/admin/categories`, `GET /api/admin/settings`, `POST /api/admin/settings` (super admin only)
- `GET /api/admin/audit-log` — append-only audit log for sensitive admin actions.
