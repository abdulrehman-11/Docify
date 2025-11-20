# 🚀 Hexaa Clinic Voice Agent - Render Deployment Guide

## ✅ Files Updated for Deployment

The following files have been optimized for Render deployment:

1. **`agent.py`** - Fixed inference executor for Linux/Windows compatibility
2. **`render-build.sh`** - Build script for Render
3. **`render-start.sh`** - Start script for Render  
4. **`.env.example`** - Environment variable template

## 📋 Pre-Deployment Checklist

Before deploying, ensure you have:

- [ ] PostgreSQL database provisioned on Render
- [ ] LiveKit account and API credentials
- [ ] OpenAI API key
- [ ] ElevenLabs API key
- [ ] Deepgram API key (optional but recommended)

## 🔧 Render Configuration

### Step 1: Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub/GitLab repository
4. Configure the service:

### Step 2: Service Settings

| Setting | Value |
|---------|-------|
| **Name** | `hexaa-clinic-voice-agent` |
| **Region** | Choose closest to your users |
| **Branch** | `main` (or your branch) |
| **Root Directory** | `agent-python` |
| **Runtime** | `Python 3` |
| **Build Command** | `bash render-build.sh` |
| **Start Command** | `python agent.py` |
| **Instance Type** | Standard or higher (recommended) |

### Step 3: Environment Variables

Add these environment variables in Render Dashboard:

```bash
# Database (Render auto-fills this if you link a PostgreSQL database)
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db

# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret

# AI Service Keys
OPENAI_API_KEY=sk-...
ELEVEN_LABS=your_elevenlabs_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
```

### Step 4: Add PostgreSQL Database

1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Name it `hexaa-clinic-db`
3. Choose a plan (Free tier available)
4. After creation, link it to your web service:
   - Go to your web service → **Environment** tab
   - The `DATABASE_URL` should auto-populate

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Install dependencies
   - Run database migrations (`alembic upgrade head`)
   - Start your agent

## 🎯 What Was Fixed

### Problem: Inference Executor Timeout

**Error:** 
```
TimeoutError: inference executor initialization timeout
None of PyTorch, TensorFlow >= 2.0, or Flax have been found
```

**Root Cause:**
- LiveKit's inference executor requires ML libraries (PyTorch/TensorFlow) and GPU access
- Render's Linux environment doesn't have GPU support
- The code only disabled inference executor on Windows, not Linux

**Solution:**
```python
# Before (WRONG - only Windows):
if platform.system() == "Windows":
    os.environ["LIVEKIT_AGENT_INFERENCE_EXECUTOR_DISABLED"] = "1"

# After (CORRECT - all non-macOS):
if platform.system() != "Darwin":  # Disable on Linux (Render) and Windows
    os.environ["LIVEKIT_AGENT_INFERENCE_EXECUTOR_DISABLED"] = "1"
```

### Changes Made:

1. **Conditional Inference Executor**: Disabled on Linux/Windows, enabled only on macOS
2. **VAD Turn Detection**: Uses Voice Activity Detection instead of ML-based turn detection
3. **Platform-Specific Plugins**: Only loads GPU-dependent plugins on macOS
4. **Render Scripts**: Automated build and start processes

## 📊 Expected Deployment Output

After deployment, you should see:

```
==> Deploying...
🔧 Installing Python dependencies...
🗄️ Running database migrations...
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
✅ Build complete!
🚀 Starting Hexaa Clinic Voice Agent...
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
INFO - starting worker
INFO - preloading plugins
INFO - Agent ready for calls!
```

## 🔍 Troubleshooting

### Issue: Database Connection Error

**Solution:** Ensure `DATABASE_URL` is in the correct format:
```
postgresql+asyncpg://username:password@host:port/database
```

### Issue: Missing Environment Variables

**Solution:** Double-check all required variables are set in Render Dashboard

### Issue: Build Fails

**Solution:** Check logs for missing dependencies. Ensure `requirements.txt` is complete.

### Issue: Port Binding Error

**Solution:** This agent doesn't need HTTP ports. It connects to LiveKit via WebSocket. Ignore port binding warnings.

## 🎉 Next Steps After Deployment

1. **Test the Phone Number**: Call `+15184006003` to test
2. **Monitor Logs**: Watch Render logs for any issues
3. **Check Latency**: Monitor response times in logs
4. **Set Up Alerts**: Configure Render alerts for downtime

## 📞 Support

If you encounter issues:
1. Check Render logs: Dashboard → Your Service → Logs
2. Verify all environment variables are set correctly
3. Ensure database migrations ran successfully
4. Test API keys independently (OpenAI, ElevenLabs, etc.)

---

**Last Updated**: November 20, 2025
