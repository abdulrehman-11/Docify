# Quick Reference Guide

## 🚀 Running the Application

### Start Frontend
```bash
cd frontend
npm run dev
```
Access at: http://localhost:8080

### Start Backend
```bash
cd backend/agent-python
# Install dependencies first
pip install -r requirements.txt
# Then run the agent
python agent.py
```

## 📂 Project Structure

```
ether-clinic/
├── README.md                    # Main project documentation
├── .gitignore                   # Root gitignore
│
├── frontend/                    # React Frontend
│   ├── src/                    # Source code
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   ├── lib/                # Utilities & storage
│   │   └── hooks/              # Custom hooks
│   ├── public/                 # Static files
│   ├── package.json            # Dependencies
│   └── vite.config.ts          # Build config
│
└── backend/                    # Python Backend
    ├── agent-python/           # AI Agent
    │   ├── agent.py           # Main agent file
    │   ├── tools/             # Agent tools
    │   ├── src/               # Source modules
    │   ├── requirements.txt   # Python dependencies
    │   └── .env.example       # Environment variables template
    └── README.md              # Backend docs
```

## 🔑 Default Credentials

**Frontend Admin:**
- Email: admin@clinic.com
- Password: Admin123

## 🛠️ Common Commands

### Frontend
```bash
cd frontend
npm install              # Install dependencies
npm run dev             # Start dev server
npm run build           # Build for production
npm run preview         # Preview production build
```

### Backend
```bash
cd backend/agent-python
pip install -r requirements.txt    # Install dependencies
python agent.py                    # Run the agent
```

## 📦 What's Included

### Frontend Features:
✅ Appointment Management with Calendar
✅ Staff Account Management
✅ Provider/Doctor Management
✅ Services Configuration
✅ Clinic Information Editor
✅ Knowledge Base for AI Responses
✅ Audit Logging
✅ Role-based Access Control

### Backend Features:
✅ AI Calling Agent
✅ Voice Integration (Twilio/ElevenLabs)
✅ Natural Language Processing
✅ Appointment Booking Automation
✅ Knowledge Base Integration

## 🐛 Troubleshooting

**Frontend won't start?**
- Make sure you're in the `frontend` folder
- Run `npm install` first
- Check if port 8080 is available

**Backend issues?**
- Ensure Python 3.8+ is installed
- Install dependencies: `pip install -r requirements.txt`
- Copy `.env.example` to `.env` and add your API keys

## 📝 Environment Variables

### Backend (.env file in backend/agent-python/)
```
OPENAI_API_KEY=your_key_here
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
ELEVENLABS_API_KEY=your_key
```

## 🎯 Next Steps

1. ✅ Frontend is ready to use
2. ⚠️ Backend requires API keys setup
3. 📚 Read backend/README.md for detailed setup
4. 🔗 Configure integration between frontend and backend

---
**Author:** KhurramTheHexaa-tech
