# Docify Backend

Backend services for the Docify clinic management system, consisting of a REST API server and an AI voice agent for phone interactions.

## Components

### 1. API Server (`api/`)
FastAPI REST server providing endpoints for the web dashboard. Handles appointments, patients, staff, and clinic configuration.

### 2. AI Voice Agent (`agent-python/`)
LiveKit-based voice agent that handles phone calls, processes natural language requests, and manages appointments through voice interactions.

## Project Structure

```
backend/
├── api/                      # REST API Server
│   ├── routes/              # API endpoints
│   ├── api_services/        # Business logic
│   ├── api_schemas/         # Request/response schemas
│   ├── main.py             # FastAPI application
│   └── requirements.txt
│
└── agent-python/            # AI Voice Agent
    ├── tools/              # Agent tool handlers
    ├── services/           # Service layer
    ├── models/             # SQLAlchemy models
    ├── alembic/            # Database migrations
    ├── agent.py            # Agent entry point
    ├── database.py         # Database configuration
    └── requirements.txt
```

## Prerequisites

- Python 3.11+
- PostgreSQL database (Neon recommended)
- Google Cloud account with Calendar API enabled
- LiveKit account and API keys
- OpenAI API key

## Installation

### API Server

```bash
cd api
pip install -r requirements.txt
pip install -r ../agent-python/requirements.txt
```

### Voice Agent

```bash
cd agent-python
pip install -r requirements.txt
```

## Configuration

### API Server Environment Variables

Create `api/.env.local`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host/database
ALLOWED_ORIGINS=http://localhost:8080,https://your-frontend.vercel.app
GOOGLE_SERVICE_ACCOUNT_JSON={"type": "service_account", ...}
GOOGLE_CALENDAR_ID=your-calendar-id@gmail.com
```

### Voice Agent Environment Variables

Create `agent-python/.env.local`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host/database
LIVEKIT_URL=wss://your-livekit-instance.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
OPENAI_API_KEY=sk-your-openai-key
DEEPGRAM_API_KEY=your_deepgram_key
ELEVENLABS_API_KEY=your_elevenlabs_key
GOOGLE_SERVICE_ACCOUNT_JSON={"type": "service_account", ...}
GOOGLE_CALENDAR_ID=your-calendar-id@gmail.com
```

## Running the Services

### API Server

```bash
cd api
python main.py
```

The API will be available at:
- Server: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Voice Agent

```bash
cd agent-python
python agent.py
```

## Database Migrations

The project uses Alembic for database migrations:

```bash
cd agent-python

# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one revision
alembic downgrade -1
```

## Features

### API Server
- RESTful endpoints for appointments, patients, staff, and clinic data
- Google Calendar bi-directional sync
- Auto-sync service (runs every 5 minutes)
- CORS configuration for frontend integration
- Comprehensive error handling and validation

### Voice Agent
- Natural language conversation handling with OpenAI GPT-4
- Real-time voice processing with LiveKit
- Appointment booking, cancellation, and rescheduling
- Availability checking based on clinic hours
- Patient information collection and validation
- Database persistence with PostgreSQL
- Google Calendar integration

## Deployment

### API Server (Render)

The `render.yaml` file in the root directory contains the deployment configuration for Render.com.

```bash
# Deploy using Render Blueprint
render deploy
```

### Voice Agent (Render/Railway)

Deploy as a Python web service with the following configuration:
- Build Command: `pip install -r requirements.txt`
- Start Command: `python agent.py`
- Environment: Python 3.11

## API Documentation

Once the API server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# API Server
cd api
pytest

# Voice Agent
cd agent-python
pytest
```

## License

Private and Proprietary
