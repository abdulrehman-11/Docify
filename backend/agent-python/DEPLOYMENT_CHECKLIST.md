# 🎯 RENDER DEPLOYMENT CHECKLIST

## ✅ Files Modified (Completed)

- [x] `agent-python/agent.py` - Fixed inference executor for Linux
- [x] `agent-python/render-build.sh` - Build automation script
- [x] `agent-python/render-start.sh` - Start script
- [x] `agent-python/.env.example` - Environment variable template
- [x] `agent-python/RENDER_DEPLOYMENT.md` - Complete deployment guide

---

## 📋 Pre-Deployment Tasks (DO BEFORE DEPLOYING)

### 1. Version Control
- [ ] Initialize git (if not done): `git init`
- [ ] Add files: `git add .`
- [ ] Commit: `git commit -m "Fix: Render deployment - disable inference executor on Linux"`
- [ ] Add remote: `git remote add origin YOUR_REPO_URL`
- [ ] Push: `git push -u origin main`

### 2. Gather API Keys
- [ ] LiveKit URL (wss://...)
- [ ] LiveKit API Key
- [ ] LiveKit API Secret
- [ ] OpenAI API Key
- [ ] ElevenLabs API Key
- [ ] Deepgram API Key

### 3. Render Account
- [ ] Sign up/login to https://dashboard.render.com/
- [ ] Connect GitHub/GitLab account

---

## 🚀 Deployment Steps (IN ORDER)

### Step 1: Create PostgreSQL Database
1. [ ] Render Dashboard → "New +" → "PostgreSQL"
2. [ ] Name: `hexaa-clinic-db`
3. [ ] Select plan (Free tier available)
4. [ ] Click "Create Database"
5. [ ] Copy the internal connection string

### Step 2: Create Web Service
1. [ ] Render Dashboard → "New +" → "Web Service"
2. [ ] Connect your repository
3. [ ] Select repository: `Docify-deployment_code`

### Step 3: Configure Service
Fill in these settings:

| Setting | Value |
|---------|-------|
| Name | `hexaa-clinic-voice-agent` |
| Region | Select closest to you |
| Branch | `main` |
| Root Directory | `agent-python` |
| Runtime | Python 3 |
| Build Command | `bash render-build.sh` |
| Start Command | `python agent.py` |
| Instance Type | Starter ($7/month) or Standard |

### Step 4: Add Environment Variables
Click "Advanced" → Add these variables:

```
DATABASE_URL=postgresql+asyncpg://[from Step 1]
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
OPENAI_API_KEY=sk-...
ELEVEN_LABS=your_elevenlabs_key
DEEPGRAM_API_KEY=your_deepgram_key
```

- [ ] DATABASE_URL
- [ ] LIVEKIT_URL
- [ ] LIVEKIT_API_KEY
- [ ] LIVEKIT_API_SECRET
- [ ] OPENAI_API_KEY
- [ ] ELEVEN_LABS
- [ ] DEEPGRAM_API_KEY

### Step 5: Deploy
1. [ ] Click "Create Web Service"
2. [ ] Wait for build to complete (2-5 minutes)
3. [ ] Check logs for success message

---

## ✅ Post-Deployment Verification

### Check Logs Should Show:
```
🔧 Inference executor disabled for deployment environment
🏥 HEXAA CLINIC VOICE AGENT - PRODUCTION
📞 LiveKit SIP Number: +15184006003
🎯 Status: READY FOR CALLS
🚀 Production Mode: VAD turn detection (GPU-free)
INFO - Agent ready for calls!
```

### Test Functionality:
- [ ] Call +15184006003 to test voice agent
- [ ] Verify agent responds within 500ms
- [ ] Test appointment booking
- [ ] Test appointment cancellation
- [ ] Check database for records

---

## ❌ Troubleshooting

### If build fails:
- [ ] Check `render-build.sh` exists in `agent-python/`
- [ ] Verify `requirements.txt` is complete
- [ ] Check Render build logs for specific error

### If service crashes on start:
- [ ] Verify all environment variables are set
- [ ] Check DATABASE_URL format: `postgresql+asyncpg://...`
- [ ] Ensure PostgreSQL database is running
- [ ] Review Render logs tab

### If "TimeoutError" still occurs:
- [ ] Verify `agent.py` has the fix: `if platform.system() != "Darwin"`
- [ ] Check that code was pushed to repository
- [ ] Ensure Render is pulling latest code

### If agent doesn't respond:
- [ ] Verify LiveKit credentials are correct
- [ ] Check LiveKit dashboard for connection
- [ ] Test API keys individually
- [ ] Review OpenAI/ElevenLabs account status

---

## 📞 Support Resources

- **Render Docs**: https://render.com/docs
- **LiveKit Docs**: https://docs.livekit.io
- **Deployment Guide**: See `RENDER_DEPLOYMENT.md`

---

**Last Updated**: November 20, 2025
**Status**: Ready for Deployment ✅
