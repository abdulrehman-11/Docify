# Ether Clinic - AI-Powered Clinic Calling Agent System

A complete frontend application for managing clinic operations with an AI-powered calling agent system.

## 🏥 Project Overview

**Ether Clinic** is a comprehensive clinic management system that enables healthcare providers to:
- Manage appointments with a visual calendar interface
- Control staff accounts with custom permissions
- Maintain provider schedules and availability
- Configure clinic information and operating hours
- Define services and their durations
- Build an AI knowledge base for common patient questions

## 🚀 Features

### Admin Dashboard
- **Appointment Management**: Full calendar view with appointment creation, editing, and status tracking
- **Staff Management**: Create and manage staff accounts with granular permissions
- **Provider Management**: Manage doctors with schedules, bios, and contact information
- **Services Configuration**: Define clinic services with durations
- **Clinic Information**: Edit contact details and operating hours
- **Knowledge Base**: Configure AI responses for common questions
- **Audit Logging**: Track all system changes and actions

### Staff Dashboard
- **Limited Appointment Access**: View and manage appointments for assigned doctors only
- **Permission-Based Actions**: Custom permissions control what staff can do

## 🛠️ Tech Stack

- **Frontend Framework**: React 18.3.1 with TypeScript
- **Build Tool**: Vite 5.4.19
- **Styling**: Tailwind CSS with custom glassmorphism effects
- **UI Components**: Radix UI + shadcn/ui
- **Routing**: React Router v6
- **State Management**: React Hooks + localStorage
- **Date Handling**: date-fns
- **Icons**: Lucide React
- **Notifications**: Sonner

## 📦 Installation

```sh
# Clone the repository
git clone https://github.com/KhurramTheHexaa-tech/ether-clinic.git

# Navigate to the project directory
cd ether-clinic

# Install dependencies
npm install

# Start the development server
npm run dev
```

## 🔐 Default Login Credentials

**Admin Account:**
- Email: `admin@clinic.com`
- Password: `Admin123`

## 📁 Project Structure

```
ether-clinic/
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── layout/        # Layout components (Navbar, Sidebar, etc.)
│   │   └── ui/            # shadcn/ui components
│   ├── hooks/             # Custom React hooks
│   ├── lib/               # Utility functions and storage
│   │   ├── auth.ts       # Authentication system
│   │   ├── storage.ts    # localStorage management
│   │   └── mockData.ts   # Type definitions
│   ├── pages/             # Page components
│   │   ├── admin/        # Admin-only pages
│   │   └── staff/        # Staff pages
│   └── App.tsx            # Main application component
├── public/                # Static assets
└── index.html            # HTML entry point
```

## 🎨 Key Features Implemented

### ✅ Secure Authentication
- Role-based access control (Admin/Staff)
- Session management with localStorage
- Protected routes

### ✅ Appointment System
- Interactive calendar with month navigation
- Create, edit, cancel, and complete appointments
- Filter by doctor
- Status badges and tracking

### ✅ Staff Account Management
- Custom permissions system
- Assign specific doctors to staff members
- Create/edit/delete staff accounts

### ✅ Provider Management
- Doctor profiles with bios and specializations
- Weekly schedule editor
- Contact information management

### ✅ Knowledge Base Editor
- Category-based Q&A organization
- Search and filter functionality
- Define exact AI responses

### ✅ Clinic Configuration
- Operating hours for all 7 days
- Contact information (address, phone, email)
- Service catalog with durations

## 🔧 Available Scripts

```sh
npm run dev          # Start development server
npm run build        # Build for production
npm run build:dev    # Build in development mode
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

## 📄 License

This project is private and proprietary.

## 👤 Author

**KhurramTheHexaa-tech**

---

Built with ❤️ for modern healthcare management

