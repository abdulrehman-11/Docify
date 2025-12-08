# Docify - AI-Powered Clinic Management System

A comprehensive full-stack clinic management platform featuring an intelligent AI voice calling agent, web-based dashboard, and seamless Google Calendar integration. Built with React, FastAPI, LiveKit, and OpenAI.

[![React](https://img.shields.io/badge/React-18.3.1-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8.3-blue.svg)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)
[![LiveKit](https://img.shields.io/badge/LiveKit-1.0.19-orange.svg)](https://livekit.io/)

---

## Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [Environment Variables](#-environment-variables)
- [API Documentation](#-api-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## Overview

**Docify** is an enterprise-grade clinic management system designed for healthcare providers. It combines three powerful components:

1. **🎙️ AI Voice Agent** - Intelligent phone receptionist powered by LiveKit and OpenAI that handles appointment bookings, cancellations, rescheduling, and answers patient questions 24/7
2. **💻 Web Dashboard** - Modern React-based interface for clinic staff to manage appointments, patients, providers, and clinic operations
3. **📅 Calendar Sync** - Real-time bi-directional synchronization with Google Calendar for seamless scheduling

### What Makes Docify Special?

- **Voice AI Integration**: Natural language processing for phone conversations using OpenAI GPT-4
- **Real-time Voice Processing**: LiveKit-powered low-latency voice communications with barge-in detection
- **Smart Scheduling**: Automatic appointment slot detection based on clinic hours and existing bookings
- **Calendar Sync**: Two-way sync with Google Calendar - changes reflect instantly
- **Role-Based Access**: Granular permissions for admin and staff users
- **PostgreSQL Backend**: Robust data persistence with SQLAlchemy ORM
- **Modern UI/UX**: Beautiful glassmorphism design with Tailwind CSS and shadcn/ui components

---

## Key Features

### AI Voice Agent (LiveKit + OpenAI)
- **Natural Conversations**: GPT-4 powered voice assistant that understands patient requests
- **Appointment Booking**: Automated scheduling with slot availability checking
- **Appointment Management**: Cancel and reschedule existing appointments via phone
- **Information Queries**: Answer questions about clinic hours, location, and services
- **Voice Activity Detection**: Barge-in support for natural interruptions
- **Google Calendar Integration**: Real-time sync of all phone-booked appointments
- **Database Persistence**: All appointments stored in PostgreSQL

### Web Dashboard (React + TypeScript)

#### Admin Features
- **Dashboard Overview**: Real-time statistics and appointment metrics
- **Appointment Management**: 
  - Visual calendar with month/week/day views
  - Create, edit, cancel, and complete appointments
  - Status tracking (scheduled, confirmed, completed, cancelled)
  - Patient information management
  - Google Calendar sync status
- **Patient Management**: 
  - Complete patient database with contact information
  - Appointment history per patient
  - Add/edit/delete patient records
- **Staff Management**: 
  - Create staff accounts with custom permissions
  - Assign specific providers to staff members
  - Role-based access control
- **Provider Management**: 
  - Doctor profiles with bios and specializations
  - Weekly schedule editor (Monday-Sunday)
  - Contact information and availability
- **Clinic Configuration**: 
  - Operating hours for each day of the week
  - Contact information (address, phone, email)
  - Service catalog with durations

#### Staff Features
- **Limited Dashboard**: View appointments for assigned providers only
- **Permission-Based Access**: Custom permissions control available actions
- **Appointment Management**: Based on assigned permissions

### Calendar Integration
- **Two-Way Sync**: Changes in dashboard or Google Calendar reflect instantly
- **Auto-Sync Service**: Background task syncs every 5 minutes
- **Conflict Detection**: Prevents double-booking
- **Event Formatting**: Professional event titles with patient info

### Security & Authentication
- **Role-Based Access Control (RBAC)**: Admin and Staff roles with different permissions
- **Protected Routes**: Frontend route guards for authorized access
- **Session Management**: Secure authentication with localStorage
- **API Security**: CORS configuration for production deployments

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USERS                                    │
│                                                                   │
│  📞 Phone Callers    👨‍💼 Admin Users    👩‍⚕️ Staff Users          │
└────────┬─────────────────┬─────────────────┬────────────────────┘
         │                 │                 │
         │                 │                 │
         ▼                 ▼                 ▼
┌─────────────────┐  ┌──────────────────────────────────┐
│   AI Voice      │  │    Web Dashboard (React)         │
│   Agent         │  │    - Admin Panel                 │
│   (LiveKit)     │  │    - Staff Panel                 │
│   - OpenAI GPT  │  │    - Appointment Calendar        │
│   - Deepgram    │  │    - Patient Management          │
│   - ElevenLabs  │  │    Deployed on Vercel            │
└────────┬────────┘  └─────────────┬────────────────────┘
         │                         │
         │                         │
         └───────┬─────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │   FastAPI       │
        │   REST API      │
        │   (Backend)     │
        │   Deployed on   │
        │   Render        │
        └────────┬────────┘
                 │
         ┌───────┴────────┬─────────────────┐
         │                │                 │
         ▼                ▼                 ▼
  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
  │ PostgreSQL  │  │   Google    │  │  Alembic    │
  │  Database   │  │  Calendar   │  │ Migrations  │
  │  (Neon)     │  │    API      │  │             │
  └─────────────┘  └─────────────┘  └─────────────┘
```

### Data Flow

1. **Phone Call Flow**: 
   - Patient calls clinic number → LiveKit connects → AI Agent processes → Books appointment → Stores in PostgreSQL → Syncs to Google Calendar → Shows in Web Dashboard

2. **Dashboard Flow**: 
   - Admin/Staff logs in → React Dashboard → FastAPI Backend → PostgreSQL Database → Real-time updates → Syncs to Google Calendar

3. **Calendar Sync Flow**: 
   - Background service runs every 5 minutes → Checks Google Calendar for changes → Updates PostgreSQL → Dashboard reflects changes instantly

---

## Tech Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.3.1 | UI framework |
| TypeScript | 5.8.3 | Type safety |
| Vite | 5.4.19 | Build tool |
| React Router | 6.30.1 | Routing |
| Tailwind CSS | 3.4.17 | Styling |
| shadcn/ui | Latest | UI components |
| Radix UI | Latest | Accessible components |
| Axios | 1.13.2 | HTTP client |
| React Query | 5.83.0 | Data fetching |
| date-fns | 3.6.0 | Date utilities |
| Lucide React | 0.462.0 | Icons |
| Sonner | 1.7.4 | Toast notifications |

### Backend - API Server
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11 | Programming language |
| FastAPI | Latest | Web framework |
| SQLAlchemy | Latest | ORM |
| Alembic | 1.17.1 | Database migrations |
| asyncpg | 0.30.0 | PostgreSQL driver |
| Pydantic | Latest | Data validation |
| python-dateutil | Latest | Date handling |
| Google Calendar API | 2.187.0 | Calendar integration |

### Backend - AI Voice Agent
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11 | Programming language |
| LiveKit | 1.0.19 | Real-time voice |
| LiveKit Agents | 1.3.5 | Agent framework |
| OpenAI | Latest | GPT-4 integration |
| Deepgram | Latest | Speech-to-text |
| ElevenLabs | Latest | Text-to-speech |
| SQLAlchemy | Latest | Database ORM |

### Database & Infrastructure
| Technology | Purpose |
|------------|---------|
| PostgreSQL (Neon) | Primary database |
| Google Calendar API | Appointment sync |
| Render | Backend hosting |
| Vercel | Frontend hosting |

---

## Getting Started

### Prerequisites

- **Node.js** 16+ and npm
- **Python** 3.11/3.12
- **PostgreSQL** database (Neon recommended)
- **Google Cloud** account with Calendar API enabled
- **LiveKit** account and API keys
- **OpenAI** API key
- **Deepgram** API key (optional)
- **ElevenLabs** API key (optional)

### Installation

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/abdulrehman-11/Docify.git
cd Docify
```

#### 2️⃣ Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at **http://localhost:8080**


#### 3️⃣ Backend API Setup

```bash
cd backend/api

# Install dependencies
pip install -r requirements.txt
pip install -r ../agent-python/requirements.txt

# Create .env.local file with your credentials
# (See Environment Variables section below)

# Run the API server
python main.py
```

The API will be available at **http://localhost:8000**
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### 4️⃣ AI Voice Agent Setup

```bash
cd backend/agent-python

# Install dependencies
pip install -r requirements.txt

# Create .env.local file with LiveKit and OpenAI credentials
# (See Environment Variables section below)

# Run the agent
python agent.py
```

---

## Project Structure

```
Docify/
├── frontend/                      # React TypeScript frontend
│   ├── src/
│   │   ├── components/           # Reusable UI components
│   │   │   ├── layout/          # DashboardLayout, Navbar, Sidebar
│   │   │   ├── ui/              # shadcn/ui components
│   │   │   └── ProtectedRoute.tsx
│   │   ├── contexts/            # React context providers
│   │   ├── hooks/               # Custom React hooks
│   │   ├── lib/                 # Utilities and configurations
│   │   │   ├── api/            # API client and types
│   │   │   ├── auth.ts         # Authentication logic
│   │   │   └── utils.ts        # Helper functions
│   │   ├── pages/              # Page components
│   │   │   ├── admin/          # Admin dashboard pages
│   │   │   │   ├── AdminDashboard.tsx
│   │   │   │   ├── Appointments.tsx
│   │   │   │   ├── Patients.tsx
│   │   │   │   ├── Providers.tsx
│   │   │   │   ├── Staff.tsx
│   │   │   │   ├── Clinic.tsx
│   │   │   │   ├── Services.tsx
│   │   │   │   ├── Knowledge.tsx
│   │   │   │   └── Audit.tsx
│   │   │   ├── staff/          # Staff dashboard pages
│   │   │   │   ├── StaffDashboard.tsx
│   │   │   │   └── Appointments.tsx
│   │   │   ├── Landing.tsx
│   │   │   ├── Login.tsx
│   │   │   └── NotFound.tsx
│   │   ├── App.tsx             # Main app component
│   │   └── main.tsx            # Entry point
│   ├── public/                 # Static assets
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── vercel.json            # Vercel deployment config
│
├── backend/
│   ├── api/                    # FastAPI REST API server
│   │   ├── routes/            # API route handlers
│   │   │   ├── appointments.py
│   │   │   ├── patients.py
│   │   │   ├── staff.py
│   │   │   └── clinic.py
│   │   ├── api_services/      # Business logic layer
│   │   │   ├── appointment_service.py
│   │   │   ├── patient_service.py
│   │   │   ├── staff_service.py
│   │   │   ├── clinic_service.py
│   │   │   └── calendar_sync_service.py
│   │   ├── api_schemas/       # Pydantic schemas
│   │   │   ├── appointment.py
│   │   │   ├── patient.py
│   │   │   ├── staff.py
│   │   │   └── clinic.py
│   │   ├── api_database.py    # Database connection
│   │   ├── main.py            # FastAPI app entry
│   │   ├── requirements.txt
│   │   └── README.md
│   │
│   └── agent-python/          # AI Voice Agent (LiveKit)
│       ├── tools/             # Tool handlers for AI agent
│       │   ├── handlers.py    # Appointment booking logic
│       │   ├── router.py      # Tool routing system
│       │   ├── schemas.py     # Input/output schemas
│       │   └── livekit_tools.py
│       ├── services/          # Service layer
│       │   ├── appointment_service.py
│       │   ├── patient_service.py
│       │   └── google_calendar_service.py
│       ├── models/            # SQLAlchemy models
│       │   ├── appointment.py
│       │   ├── patient.py
│       │   ├── staff.py
│       │   └── clinic_hours.py
│       ├── alembic/           # Database migrations
│       ├── utils/             # Utility functions
│       ├── agent.py           # Main agent entry point
│       ├── database.py        # Database connection
│       ├── requirements.txt
│       ├── pyproject.toml
│       └── README.md
│
├── render.yaml                # Render.com deployment config
└── README.md                  # This file
```

---

## Environment Variables

### Frontend
No environment variables required. Authentication uses localStorage.

### Backend API (`backend/api/.env.local`)

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host/database

# CORS
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:8080

# Google Calendar
GOOGLE_SERVICE_ACCOUNT_JSON={"type": "service_account", ...}
GOOGLE_CALENDAR_ID=your-calendar-id@gmail.com
```

### AI Voice Agent (`backend/agent-python/.env.local`)

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host/database

# LiveKit
LIVEKIT_URL=wss://your-livekit-instance.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret

# OpenAI
OPENAI_API_KEY=sk-your-openai-key

# Deepgram (optional)
DEEPGRAM_API_KEY=your_deepgram_key

# ElevenLabs (optional)
ELEVENLABS_API_KEY=your_elevenlabs_key

# Google Calendar
GOOGLE_SERVICE_ACCOUNT_JSON={"type": "service_account", ...}
GOOGLE_CALENDAR_ID=your-calendar-id@gmail.com
```

---

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Appointments
- `GET /appointments` - List all appointments
- `POST /appointments` - Create appointment
- `PUT /appointments/{id}` - Update appointment
- `DELETE /appointments/{id}` - Delete appointment

#### Patients
- `GET /patients` - List all patients
- `POST /patients` - Create patient
- `PUT /patients/{id}` - Update patient
- `DELETE /patients/{id}` - Delete patient

#### Staff
- `GET /staff` - List all staff
- `POST /staff` - Create staff account
- `PUT /staff/{id}` - Update staff
- `DELETE /staff/{id}` - Delete staff

#### Clinic
- `GET /clinic/hours` - Get clinic hours
- `PUT /clinic/hours` - Update clinic hours
- `GET /clinic/info` - Get clinic information
- `PUT /clinic/info` - Update clinic info

#### Calendar Sync
- `POST /calendar/sync` - Manual sync trigger
- `GET /calendar/status` - Check sync status

---

## Contributing

This is a private project by **Abdul Rehman**. For inquiries, please contact the repository owner.

---

## License

Private and Proprietary. All rights reserved.

---

## Author

**Abdul Rehman** ([@abdulrehman-11](https://github.com/abdulrehman-11))

---

## Acknowledgments

- Built with [LiveKit](https://livekit.io/) for real-time voice
- Powered by [OpenAI](https://openai.com/) GPT-4
- Hosted on [Vercel](https://vercel.com/) and [Render](https://render.com/)

---

<div align="center">


⭐ Star this repo if you find it helpful!

</div>

