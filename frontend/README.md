# Docify Frontend

React-based web dashboard for clinic management with role-based access control for administrators and staff members.

## Overview

The frontend provides a comprehensive interface for managing clinic operations including appointments, patients, providers, staff accounts, and clinic configuration. It connects to the FastAPI backend and displays real-time data synchronized with the AI voice agent.

## Tech Stack

- React 18.3.1 with TypeScript
- Vite 5.4.19 (Build tool)
- Tailwind CSS (Styling)
- shadcn/ui + Radix UI (Components)
- React Router v6 (Routing)
- Axios (HTTP client)
- React Query (Data fetching)
- date-fns (Date utilities)

## Installation

```bash
npm install
```

## Development

```bash
npm run dev
```

The application will be available at `http://localhost:8080`

## Build

```bash
# Production build
npm run build

# Development build
npm run build:dev
```

## Project Structure

```
src/
├── components/
│   ├── layout/          # DashboardLayout, Navbar, Sidebar
│   └── ui/              # shadcn/ui components
├── contexts/            # React context providers
├── hooks/               # Custom React hooks
├── lib/
│   ├── api/            # API client and types
│   ├── auth.ts         # Authentication logic
│   └── utils.ts        # Utility functions
├── pages/
│   ├── admin/          # Admin dashboard pages
│   └── staff/          # Staff dashboard pages
├── App.tsx
└── main.tsx
```

## Features

### Admin Dashboard
- Appointment management with calendar view
- Patient database management
- Provider scheduling and profiles
- Staff account management with permissions
- Clinic configuration (hours, services, contact info)
- Knowledge base editor for AI responses
- Audit logging

### Staff Dashboard
- Limited appointment access (assigned providers only)
- Permission-based action controls
- Appointment creation and management

## Authentication

Default admin credentials:
- Email: `admin@clinic.com`
- Password: `Admin123`

Authentication uses localStorage for session management with role-based access control.

## Environment Configuration

No environment variables required. The application uses localStorage for data persistence and connects to the backend API at the configured endpoint.

## Deployment

The application is configured for deployment on Vercel. See `vercel.json` for configuration.

```bash
vercel deploy
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run build:dev` - Build in development mode
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## License

Private and Proprietary
