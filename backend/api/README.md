# Docify REST API

FastAPI REST server providing endpoints for the clinic management dashboard. Connects to PostgreSQL database shared with the AI voice agent.

## Installation

```bash
pip install -r requirements.txt
pip install -r ../agent-python/requirements.txt
```

## Configuration

Create `.env.local` file:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host/database
ALLOWED_ORIGINS=http://localhost:8080,https://your-frontend.vercel.app
GOOGLE_SERVICE_ACCOUNT_JSON={"type": "service_account", ...}
GOOGLE_CALENDAR_ID=your-calendar-id@gmail.com
```

## Running the Server

```bash
python main.py
```

The API will be available at:
- Server: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Patients
- `GET /patients` - List all patients (paginated)
- `GET /patients/{id}` - Get patient by ID
- `POST /patients` - Create new patient
- `PUT /patients/{id}` - Update patient
- `DELETE /patients/{id}` - Delete patient

### Appointments
- `GET /appointments` - List appointments with filters (date, status, patient_id)
- `GET /appointments/{id}` - Get appointment details
- `POST /appointments` - Create new appointment
- `PUT /appointments/{id}` - Update appointment
- `DELETE /appointments/{id}` - Delete appointment
- `POST /appointments/availability` - Check available time slots

### Staff
- `GET /staff` - List all staff members
- `GET /staff/{id}` - Get staff details
- `POST /staff` - Create staff account
- `PUT /staff/{id}` - Update staff account
- `DELETE /staff/{id}` - Delete staff account

### Clinic
- `GET /clinic/hours` - Get clinic operating hours
- `PUT /clinic/hours` - Update clinic hours
- `GET /clinic/info` - Get clinic information
- `PUT /clinic/info` - Update clinic information

### Calendar Sync
- `POST /calendar/sync` - Trigger manual calendar synchronization
- `GET /calendar/status` - Get sync status

## Project Structure

```
api/
├── routes/              # API route handlers
│   ├── appointments.py
│   ├── patients.py
│   ├── staff.py
│   └── clinic.py
├── api_services/        # Business logic layer
│   ├── appointment_service.py
│   ├── patient_service.py
│   ├── staff_service.py
│   ├── clinic_service.py
│   └── calendar_sync_service.py
├── api_schemas/         # Pydantic request/response schemas
│   ├── appointment.py
│   ├── patient.py
│   ├── staff.py
│   └── clinic.py
├── api_database.py      # Database session management
└── main.py             # FastAPI application entry point
```

## Database

The API uses the same PostgreSQL database as the voice agent:
- Shared tables: `patients`, `appointments`, `staff`, `clinic_hours`
- Two-way synchronization with Google Calendar
- All datetime fields use ISO8601 format with timezone

## Features

- RESTful API with comprehensive endpoint coverage
- Automatic Google Calendar synchronization (bi-directional)
- Background auto-sync task (runs every 5 minutes)
- CORS configuration for frontend integration
- Request validation with Pydantic schemas
- Comprehensive error handling
- Interactive API documentation (Swagger UI)

## Notes

- Default pagination: page=1, page_size=50
- Appointment statuses: SCHEDULED, CONFIRMED, CANCELLED, COMPLETED
- All times must be in ISO8601 format with timezone
- CORS allows localhost:8080 and configured production origins

## Deployment

Configured for deployment on Render.com. See `render.yaml` in the root directory for deployment configuration.

## License

Private and Proprietary
