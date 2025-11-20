# Ether Clinic - Complete AI Clinic Calling Agent System# Ether Clinic - AI-Powered Clinic Calling Agent System



A full-stack application combining a React frontend with Python AI backend for managing clinic operations with an intelligent calling agent.A complete frontend application for managing clinic operations with an AI-powered calling agent system.



## 📁 Project Structure## 🏥 Project Overview



```**Ether Clinic** is a comprehensive clinic management system that enables healthcare providers to:

ether-clinic/- Manage appointments with a visual calendar interface

├── frontend/          # React + TypeScript frontend application- Control staff accounts with custom permissions

│   ├── src/          # Source code for the web interface- Maintain provider schedules and availability

│   ├── public/       # Static assets- Configure clinic information and operating hours

│   └── package.json  # Frontend dependencies- Define services and their durations

│- Build an AI knowledge base for common patient questions

└── backend/          # Python AI agent backend

    ├── agent-python/ # AI calling agent implementation## 🚀 Features

    └── README.md     # Backend documentation

```### Admin Dashboard

- **Appointment Management**: Full calendar view with appointment creation, editing, and status tracking

## 🚀 Quick Start- **Staff Management**: Create and manage staff accounts with granular permissions

- **Provider Management**: Manage doctors with schedules, bios, and contact information

### Frontend Setup- **Services Configuration**: Define clinic services with durations

- **Clinic Information**: Edit contact details and operating hours

```bash- **Knowledge Base**: Configure AI responses for common questions

cd frontend- **Audit Logging**: Track all system changes and actions

npm install

npm run dev### Staff Dashboard

```- **Limited Appointment Access**: View and manage appointments for assigned doctors only

- **Permission-Based Actions**: Custom permissions control what staff can do

The frontend will be available at `http://localhost:8080`

## 🛠️ Tech Stack

**Default Admin Login:**

- Email: `admin@clinic.com`- **Frontend Framework**: React 18.3.1 with TypeScript

- Password: `Admin123`- **Build Tool**: Vite 5.4.19

- **Styling**: Tailwind CSS with custom glassmorphism effects

### Backend Setup- **UI Components**: Radix UI + shadcn/ui

- **Routing**: React Router v6

```bash- **State Management**: React Hooks + localStorage

cd backend/agent-python- **Date Handling**: date-fns

# Follow backend README.md for setup instructions- **Icons**: Lucide React

```- **Notifications**: Sonner



## 🏥 Features## 📦 Installation



### Frontend (React + TypeScript)```sh

- **Admin Dashboard** - Complete clinic management interface# Clone the repository

- **Appointment Management** - Visual calendar with booking systemgit clone https://github.com/KhurramTheHexaa-tech/ether-clinic.git

- **Staff Management** - User accounts with custom permissions

- **Provider Management** - Doctor profiles and schedules# Navigate to the project directory

- **Services Configuration** - Define clinic services and durationscd ether-clinic

- **Clinic Settings** - Operating hours and contact information

- **Knowledge Base Editor** - Configure AI responses for common questions# Install dependencies

- **Audit Logging** - Track all system changesnpm install



### Backend (Python AI Agent)# Start the development server

- **AI Calling Agent** - Intelligent phone interaction systemnpm run dev

- **Natural Language Processing** - Understand patient requests```

- **Appointment Booking** - Automated scheduling via phone

- **Knowledge Base Integration** - Answer common questions## 🔐 Default Login Credentials

- **Voice Integration** - Text-to-speech and speech-to-text

**Admin Account:**

## 🛠️ Tech Stack- Email: `admin@clinic.com`

- Password: `Admin123`

### Frontend

- **Framework:** React 18.3.1 with TypeScript## 📁 Project Structure

- **Build Tool:** Vite 5.4.19

- **Styling:** Tailwind CSS with glassmorphism effects```

- **UI Components:** Radix UI + shadcn/uiether-clinic/

- **Routing:** React Router v6├── src/

- **State:** React Hooks + localStorage│   ├── components/         # Reusable UI components

- **Icons:** Lucide React│   │   ├── layout/        # Layout components (Navbar, Sidebar, etc.)

│   │   └── ui/            # shadcn/ui components

### Backend│   ├── hooks/             # Custom React hooks

- **Language:** Python│   ├── lib/               # Utility functions and storage

- **AI/ML:** OpenAI, LangChain, ChromaDB│   │   ├── auth.ts       # Authentication system

- **Voice:** Twilio, ElevenLabs│   │   ├── storage.ts    # localStorage management

- **Framework:** FastAPI (API endpoints)│   │   └── mockData.ts   # Type definitions

│   ├── pages/             # Page components

## 📖 Documentation│   │   ├── admin/        # Admin-only pages

│   │   └── staff/        # Staff pages

- [Frontend README](./frontend/README.md) - Detailed frontend documentation│   └── App.tsx            # Main application component

- [Backend README](./backend/README.md) - Backend setup and API docs├── public/                # Static assets

└── index.html            # HTML entry point

## 🔐 Environment Variables```



### Frontend## 🎨 Key Features Implemented

No environment variables required - uses localStorage for data persistence.

### ✅ Secure Authentication

### Backend- Role-based access control (Admin/Staff)

See `backend/agent-python` for required API keys and configuration.- Session management with localStorage

- Protected routes

## 🎯 Key Workflows

### ✅ Appointment System

1. **Patient Calls Clinic** → AI Agent answers → Books appointment → Syncs with frontend- Interactive calendar with month navigation

2. **Staff Logs In** → Views calendar → Manages appointments → Updates knowledge base- Create, edit, cancel, and complete appointments

3. **Admin Manages** → Creates staff accounts → Configures services → Reviews audit logs- Filter by doctor

- Status badges and tracking

## 📦 Deployment

### ✅ Staff Account Management

### Frontend- Custom permissions system

```bash- Assign specific doctors to staff members

cd frontend- Create/edit/delete staff accounts

npm run build

# Deploy dist/ folder to hosting service (Vercel, Netlify, etc.)### ✅ Provider Management

```- Doctor profiles with bios and specializations

- Weekly schedule editor

### Backend- Contact information management

```bash

cd backend/agent-python### ✅ Knowledge Base Editor

# Follow backend deployment instructions- Category-based Q&A organization

```- Search and filter functionality

- Define exact AI responses

## 👥 User Roles

### ✅ Clinic Configuration

- **Admin** - Full access to all features- Operating hours for all 7 days

- **Staff** - Limited access based on assigned permissions- Contact information (address, phone, email)

- Service catalog with durations

## 🔄 Data Flow

## 🔧 Available Scripts

```

Phone Call → AI Agent (Backend) → API → Frontend Dashboard → Staff Action → Database Update → AI Agent Knowledge Base```sh

```npm run dev          # Start development server

npm run build        # Build for production

## 🤝 Contributingnpm run build:dev    # Build in development mode

npm run preview      # Preview production build

This is a private project by **KhurramTheHexaa-tech**.npm run lint         # Run ESLint

```

## 📄 License

## 📄 License

Private and Proprietary

This project is private and proprietary.

## 👤 Author

## 👤 Author

**KhurramTheHexaa-tech**

**KhurramTheHexaa-tech**

---

---

Built with ❤️ for modern healthcare management

Built with ❤️ for modern healthcare management

