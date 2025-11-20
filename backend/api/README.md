# Ether Clinic REST API

FastAPI REST server for the clinic staff dashboard. Connects to the same Neon PostgreSQL database as the voice agent.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend/api
pip install -r requirements.txt
```

### 2. Configure Environment

The `.env.local` file is already configured with your Neon database credentials.

### 3. Run the Server

```bash
python main.py
```

The API will be available at:
- **Server**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### Patients

- `GET /patients` - List all patients (paginated)
- `GET /patients/{id}` - Get patient by ID
- `POST /patients` - Create new patient
- `PUT /patients/{id}` - Update patient
- `DELETE /patients/{id}` - Delete patient

### Appointments

- `GET /appointments` - List all appointments (with filters)
- `GET /appointments/{id}` - Get appointment by ID
- `POST /appointments` - Create new appointment
- `PUT /appointments/{id}` - Update appointment
- `POST /appointments/{id}/cancel` - Cancel appointment
- `DELETE /appointments/{id}` - Delete appointment
- `POST /appointments/availability` - Check available slots

### Clinic Hours

- `GET /clinic/hours` - Get clinic hours for all days
- `PUT /clinic/hours/{id}` - Update clinic hours
- `POST /clinic/hours` - Create clinic hours

### Dashboard

- `GET /dashboard/stats` - Get statistics (counts, etc.)
- `GET /dashboard/today` - Today's appointments
- `GET /dashboard/upcoming` - Upcoming appointments

## 🔧 Development

### Run with Auto-Reload

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Access Interactive Docs

Visit http://localhost:8000/docs to test all endpoints interactively.

## 🗄️ Database

The API connects to the same Neon PostgreSQL database as the voice agent:
- Database: `neondb`
- Tables: `patients`, `appointments`, `clinic_hours`
- All data is synchronized between voice agent and REST API

## 📝 Notes

- CORS is configured for local frontend development (ports 3000, 5173, 5174)
- All datetime fields use ISO8601 format with timezone
- Pagination defaults: page=1, page_size=50
- Status values: CONFIRMED, CANCELLED, RESCHEDULED, COMPLETED
