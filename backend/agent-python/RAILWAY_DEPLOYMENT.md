# 🚂 Hexaa Clinic Voice Agent - Railway Deployment Guide

## ✅ Your Code is Railway-Ready!

All necessary configuration files have been set up:

| File | Purpose |
|------|---------|
| `railway.json` | Config-as-code for build, deploy, and pre-deploy settings |
| `Dockerfile` | Optimized Docker image for Railway |
| `.dockerignore` | Excludes unnecessary files from Docker build |
| `.env.example` | Environment variable documentation |

---

## 🚀 Deploy to Railway (GitHub Connected)

### Step 1: Create a Railway Account & Project

1. Go to [Railway.app](https://railway.app/) and sign in with GitHub
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your repository: `abdulrehman-11/Docify`

### Step 2: Configure Service (Important!)

When Railway detects your repo, you need to configure the **Root Directory** since your agent is in a subdirectory:

1. After selecting the repo, click on the created service
2. Go to **Settings** tab
3. Under **"Source"** section, set:
   - **Root Directory**: `backend/agent-python`

Railway will automatically detect the `Dockerfile` and `railway.json` config.

### Step 3: Add PostgreSQL Database

1. In your Railway project, click **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Railway will automatically provision a PostgreSQL instance
3. The `DATABASE_URL` will be auto-available as a reference variable

### Step 4: Configure Environment Variables

Go to your service → **Variables** tab and add these:

#### Required Variables:

```plaintext
# Database (Reference from PostgreSQL service)
DATABASE_URL=${{Postgres.DATABASE_URL}}
# ⚠️ IMPORTANT: Append the asyncpg driver prefix! Change the reference to:
# If Railway gives: postgres://user:pass@host:port/db
# You need: postgresql+asyncpg://user:pass@host:port/db

# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret

# AI Services
OPENAI_API_KEY=sk-your_openai_key
ELEVEN_LABS=your_elevenlabs_key
DEEPGRAM_API_KEY=your_deepgram_key

# Google Calendar (paste entire JSON as single line)
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"..."}
GOOGLE_CALENDAR_ID=your_calendar@gmail.com
```

#### ⚠️ DATABASE_URL Format Fix

Railway's PostgreSQL provides a URL like:
```
postgres://user:pass@host:port/db
```

Your app needs the asyncpg driver format:
```
postgresql+asyncpg://user:pass@host:port/db
```

**Solution**: Create a new variable with the correct format:
1. Copy the value from `${{Postgres.DATABASE_URL}}`
2. Replace `postgres://` with `postgresql+asyncpg://`
3. Set it as `DATABASE_URL`

Or use Railway's variable transformation:
```
DATABASE_URL=postgresql+asyncpg://${PGUSER}:${PGPASSWORD}@${PGHOST}:${PGPORT}/${PGDATABASE}
```

### Step 5: Deploy!

1. Railway will automatically deploy when you push to your main branch
2. Or click **"Deploy"** button in the Railway dashboard

---

## 📊 What Happens During Deployment

Railway will:

1. **Build Phase**: 
   - Detect `Dockerfile` in `backend/agent-python`
   - Build Docker image with Python 3.12
   - Install all dependencies from `requirements.txt`

2. **Pre-Deploy Phase** (from `railway.json`):
   - Run `alembic upgrade head` to apply database migrations

3. **Start Phase**:
   - Run `python agent.py start`
   - Your LiveKit voice agent connects to LiveKit Cloud
   - Ready to receive phone calls!

---

## 📝 Deployment Logs

You should see output like:

```
==========================
Using detected Dockerfile!
==========================
...
🔧 Inference executor disabled for deployment environment
======================================================================
🏥 HEXAA CLINIC VOICE AGENT - PRODUCTION
======================================================================
📞 LiveKit SIP Number: +15184006003
🌍 International Calling: ENABLED
🎙️  Voice: ElevenLabs Sarah (Ultra-Realistic)
⚡ Target Latency: <500ms
🎯 Status: READY FOR CALLS
🚀 Production Mode: VAD turn detection (GPU-free)
======================================================================
✅ DATABASE_URL: postgresql+asyncpg://...
✅ LIVEKIT_URL: wss://...
✅ OPENAI_API_KEY: sk-****...
✅ ELEVEN_LABS: ****...
======================================================================
INFO - starting worker
INFO - preloading plugins
INFO - Agent ready for calls!
```

---

## 🔧 Troubleshooting

### Issue: "DATABASE_URL environment variable is required"

**Solution**: Make sure you've added the PostgreSQL database and the `DATABASE_URL` variable is set with the correct format (`postgresql+asyncpg://...`)

### Issue: "Inference executor initialization timeout"

**Solution**: Already handled in code! The agent disables inference executor on Linux automatically.

### Issue: Migrations fail

**Solution**: Check that your DATABASE_URL is correct and the PostgreSQL service is running. You can manually run migrations:
```bash
railway run alembic upgrade head
```

### Issue: Agent starts but no calls work

**Solution**: 
1. Verify LiveKit credentials are correct
2. Check that your SIP trunk is configured in LiveKit Cloud
3. Ensure your phone number is linked to the LiveKit project

### Issue: "No module named 'xyz'"

**Solution**: Check `requirements.txt` includes all dependencies. If missing, add and redeploy.

---

## 🔄 Auto-Deploys with GitHub

Railway automatically deploys when you push to your connected branch:

1. Make code changes locally
2. Commit and push:
   ```bash
   git add .
   git commit -m "Update voice agent"
   git push origin main
   ```
3. Railway detects the push and redeploys automatically

To disable auto-deploys:
- Service → Settings → Deploys → Toggle off "Auto-Deploy"

---

## 📈 Scaling & Monitoring

### View Logs
- Click on your service → **Deployments** → Select latest → **View Logs**

### Monitor Resources
- Railway shows CPU, Memory, and Network usage in the **Metrics** tab

### Scale Up
- Service → Settings → Change instance type if needed
- This agent typically runs fine on the default instance

---

## 🔐 Security Best Practices

1. **Never commit `.env.local`** - It's in `.gitignore`
2. **Use Railway's variable referencing** - For DATABASE_URL connections between services
3. **Rotate API keys periodically** - Update in Railway Variables when you do
4. **Enable Railway's audit logs** - Track who changed what

---

## 📞 Support

- **Railway Docs**: https://docs.railway.com
- **Railway Discord**: https://discord.gg/railway
- **LiveKit Docs**: https://docs.livekit.io

---

**Last Updated**: December 2, 2025
