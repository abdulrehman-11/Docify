# Deploying the voice agent to Railway

This folder contains the LiveKit/LLM voice agent. The service already runs on Render; this guide mirrors that deployment on Railway using the existing Dockerfile and `railway.json`.

## Prerequisites
- Railway project with a Postgres database (set `DATABASE_URL`).
- LiveKit cloud project and SIP trunk configured for your phone number.
- API keys: `OPENAI_API_KEY`, `ELEVEN_LABS`, `DEEPGRAM_API_KEY`.
- Google Calendar access: provide `GOOGLE_SERVICE_ACCOUNT_JSON` (preferred) or mount `google_service_account.json` and point `GOOGLE_SERVICE_ACCOUNT_FILE`.

## Build & runtime configuration
- Builder: Dockerfile (`python:3.12-slim`).
- Pre-deploy command: `alembic upgrade head` (runs migrations).
- Start command: `python agent.py start` (long-running LiveKit worker).
- Restart policy: on failure, 5 retries.

The `.dockerignore` keeps the build lean by excluding `venv`, caches, and secrets.

## Environment variables (required)
- `DATABASE_URL`
- `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`
- `OPENAI_API_KEY`
- `ELEVEN_LABS`
- `DEEPGRAM_API_KEY`
- `GOOGLE_SERVICE_ACCOUNT_JSON` (JSON string) _or_ `GOOGLE_SERVICE_ACCOUNT_FILE`

## Deploy steps (UI or CLI)
1) Push this repo to GitHub.
2) On Railway, create a new service → “Deploy from repository”.
3) Select `backend/agent-python` as the service root; Railway detects `railway.json`.
4) Add the environment variables above (plus any clinic-specific values).
5) Deploy. Railway will:
   - Build via Dockerfile.
   - Run migrations (`alembic upgrade head`).
   - Start the worker (`python agent.py start`).

## Notes
- No HTTP port is required; the worker stays running via LiveKit’s WebRTC/SIP connections.
- If you use file-based Google credentials, mount the file as a Railway volume and set `GOOGLE_SERVICE_ACCOUNT_FILE` to its path.
- Keep `DATABASE_URL` pointed to the same database used by your API so the agent sees live appointments.

