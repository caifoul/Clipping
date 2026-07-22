# Clipping

Turns a raw YouTube video (or upload, including ended-livestream VODs) into:

1. A reviewable "YouTube-ready" long-form edit — recommended cuts, title, chapters,
   and captions you approve before anything renders.
2. An auto-selected ~60-75s vertical clip for TikTok, captions burned in.
3. An auto-selected ~8s standalone-statement micro-clip cut from that clip.

Background music is detected and muted in every render (a compliance measure —
see `MusicSegment` in the plan, not a copyright-filter-evasion feature).

Full architecture/pipeline/data-model writeup: see the plan this was built from,
or `backend/app/` for the current implementation.

**Status**: M1 (auth + video ingestion) is implemented and working end-to-end.
M2-M6 (transcription, AI analysis, rendering, TikTok/micro clips, deploy) are
not built yet.

## Prerequisites

- Docker + Docker Compose
- An Anthropic API key and an OpenAI API key (needed starting at M2 — not
  required to run M1)

## Local development

```bash
cp .env.example .env
# edit .env: at minimum set POSTGRES_PASSWORD and SECRET_KEY to real values

docker compose up --build
```

This starts Postgres, Redis, the FastAPI API (with autoreload, migrations run
automatically on boot), two Celery workers (`cpu` and `io` queues), and the
Vite dev server. `docker-compose.override.yml` is picked up automatically and
adds the dev conveniences (bind mounts, exposed ports); it also disables the
Caddy service since local dev talks to the containers directly:

- Frontend: http://localhost:5173
- API: http://localhost:8000 (docs at `/docs`)

The frontend dev server proxies `/api` and `/media` to the API container, so
there's no CORS configuration to fight with in dev.

## What works right now (M1)

- Sign up / log in (email + password, session cookie)
- Add a video by pasting a YouTube URL or uploading a file
- Video list + detail page, with live job-status polling while it downloads
- yt-dlp handles ended-livestream VODs the same as any other YouTube URL — no
  special-casing needed

## Production deploy

`docker-compose.yml` (without the override) is the production shape: Caddy
terminates TLS (via `APP_DOMAIN` in `.env`) and reverse-proxies to the API and
a built (nginx-served) frontend image. Point DNS at the VPS, set a real
`APP_DOMAIN` and `SECRET_KEY`/`POSTGRES_PASSWORD` in `.env`, then:

```bash
docker compose -f docker-compose.yml up --build -d
```

No backup/monitoring automation is set up yet (planned for the M6 milestone) —
back up the `postgres_data` volume manually until then.
