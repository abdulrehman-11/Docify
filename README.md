# Agent Python (Voice Agent)

This branch contains only the LiveKit/LLM calling agent (Python). It is flattened to the repository root for Railway deployment.

Key files:
- `Dockerfile` + `railway.json`: build and start commands for Railway
- `DEPLOYMENT.md`: step-by-step Railway setup and required environment variables
- `alembic/`: database migrations for the agent service

Local quick start
1) Create a virtualenv and install deps: `pip install -r requirements.txt`
2) Copy `.env.example` to `.env` and fill in keys (`DATABASE_URL`, `LIVEKIT_*`, `OPENAI_API_KEY`, `ELEVEN_LABS`, `DEEPGRAM_API_KEY`, Google creds).
3) Run migrations: `alembic upgrade head`
4) Start the worker: `python agent.py start`

