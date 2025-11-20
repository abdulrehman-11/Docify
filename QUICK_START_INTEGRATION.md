# Quick Start Guide 🚀

## Prerequisites
- Python 3.9+ installed
- Node.js 18+ installed
- Neon PostgreSQL database (already configured)

## Step 1: Install Frontend Dependencies

```powershell
cd frontend
npm install
```

This will install all dependencies including axios.

## Step 2: Install Backend Dependencies

```powershell
cd backend/api
pip install -r requirements.txt
```

## Step 3: Start the Backend Server

```powershell
# Make sure you're in backend/api folder
python main.py
```

✅ Backend should start on http://localhost:8000  
✅ Visit http://localhost:8000/docs to see API documentation

## Step 4: Start the Frontend

Open a NEW terminal window:

```powershell
cd frontend
npm run dev
```

✅ Frontend should start on http://localhost:5173  

## Step 5: Login and Test

1. Open browser to http://localhost:5173
2. Login with:
   - Email: `admin@healthcare.com`
   - Password: `admin123`
3. Explore the dashboard - all data comes from your Neon database!

## Available Features

- ✅ **Dashboard**: Real-time statistics and today's appointments
- ✅ **Patients**: Add, edit, delete, and search patients
- ✅ **Appointments**: View and filter all appointments
- ✅ **Clinic Hours**: View clinic operating hours

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Need Help?

Check `INTEGRATION_COMPLETE.md` for:
- Detailed architecture explanation
- Troubleshooting guide
- Database schema details
- Future enhancement suggestions
