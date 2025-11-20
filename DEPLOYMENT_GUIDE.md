# 🚀 Deployment Guide - Ether Clinic

## Overview
This guide will walk you through deploying:
- **Backend API** → Render (FastAPI/Python)
- **Frontend** → Vercel (React/Vite)

---

## 📋 Pre-Deployment Checklist

### ⚠️ CRITICAL - Security First!

1. **Regenerate ALL API Keys** (they were exposed in the repository):
   - [ ] OpenAI API Key
   - [ ] LiveKit API Secret
   - [ ] Deepgram API Key
   - [ ] AssemblyAI API Key
   - [ ] ElevenLabs API Key
   - [ ] Cartesia API Key

2. **Verify .gitignore**:
   - [ ] Confirm `.env.local` files are NOT in git
   - [ ] Run: `git status` - should NOT show any `.env` files

3. **Database**:
   - [ ] Neon PostgreSQL is already configured ✅
   - [ ] Verify connection string is correct

---

## 🎯 Part 1: Deploy Backend API to Render

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub account
3. Connect your GitHub repository

### Step 2: Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect to your repository: `ether-clinic`
3. Configure the service:

```
Name: ether-clinic-api
Region: Oregon (or closest to you)
Branch: main
Root Directory: backend/api
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
Instance Type: Free (or Starter for production)
```

### Step 3: Set Environment Variables

In Render dashboard, go to **Environment** tab and add:

```bash
# Database (REQUIRED)
DATABASE_URL=postgresql+asyncpg://neondb_owner:YOUR_PASSWORD@ep-purple-paper-a4mvi7w9-pooler.us-east-1.aws.neon.tech/neondb?ssl=require

# CORS - Add your Vercel URL after deployment
ALLOWED_ORIGINS=https://your-app.vercel.app

# Python Version
PYTHON_VERSION=3.11.0
```

**Note:** You'll update `ALLOWED_ORIGINS` after deploying the frontend.

### Step 4: Deploy!
1. Click **"Create Web Service"**
2. Wait for deployment (3-5 minutes)
3. Your API will be live at: `https://ether-clinic-api.onrender.com` (or similar)

### Step 5: Test Your API
```bash
# Health check
curl https://your-api-url.onrender.com/health

# Expected response:
{"status":"healthy","service":"ether-clinic-api"}

# API docs
https://your-api-url.onrender.com/docs
```

**✅ Backend is now deployed!**

**Save your API URL:** `https://your-api-url.onrender.com`

---

## 🌐 Part 2: Deploy Frontend to Vercel

### Step 1: Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub account
3. Import your repository

### Step 2: Configure Project
1. Click **"Add New..."** → **"Project"**
2. Import `ether-clinic` repository
3. Configure:

```
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

### Step 3: Set Environment Variables

In **Environment Variables** section, add:

```bash
# CRITICAL: Your Render API URL
VITE_API_URL=https://ether-clinic-api.onrender.com
```

**⚠️ Replace with YOUR actual Render URL from Part 1!**

### Step 4: Deploy!
1. Click **"Deploy"**
2. Wait for deployment (2-3 minutes)
3. Your frontend will be live at: `https://your-app.vercel.app`

**✅ Frontend is now deployed!**

---

## 🔄 Part 3: Connect Frontend & Backend

### Update Backend CORS

1. Go back to **Render dashboard**
2. Navigate to your API service
3. Go to **Environment** tab
4. Update `ALLOWED_ORIGINS`:

```bash
ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-app-git-main.vercel.app
```

5. Save changes (Render will automatically redeploy)

### Test the Connection

1. Open your Vercel frontend: `https://your-app.vercel.app`
2. Navigate to **Appointments** page
3. Try creating an appointment
4. If successful → **DEPLOYMENT COMPLETE!** 🎉

---

## 📱 Post-Deployment Configuration

### Update Frontend for Production

If you make changes to the frontend:
```bash
git add .
git commit -m "Update frontend"
git push origin main
```
Vercel will automatically redeploy!

### Update Backend for Production

If you make changes to the backend:
```bash
git add .
git commit -m "Update backend API"
git push origin main
```
Render will automatically redeploy!

---

## 🐛 Troubleshooting

### Frontend can't connect to backend

**Problem:** CORS errors in browser console

**Solution:**
1. Check `ALLOWED_ORIGINS` in Render includes your Vercel URL
2. Make sure it starts with `https://` (not `http://`)
3. Include ALL Vercel preview URLs if testing branches

### Backend crashes on Render

**Problem:** Service won't start

**Solutions:**
1. Check **Logs** tab in Render dashboard
2. Verify `DATABASE_URL` is correct
3. Ensure `requirements.txt` includes all dependencies
4. Check Python version matches (3.11)

### Database connection fails

**Problem:** Can't connect to Neon

**Solution:**
1. Verify `DATABASE_URL` has `postgresql+asyncpg://` prefix
2. Check Neon dashboard - database should be active
3. Ensure `?ssl=require` is at the end of the URL

### Frontend shows wrong API URL

**Problem:** Still calling localhost

**Solution:**
1. Check Vercel environment variables
2. Make sure `VITE_API_URL` is set correctly
3. Redeploy frontend after updating env vars

---

## 🔐 Security Recommendations

### For Production:

1. **Upgrade to Paid Plans:**
   - Render: Starter plan ($7/month) - no cold starts
   - Vercel: Pro plan if needed

2. **Add Authentication:**
   - Implement JWT tokens
   - Add login/logout functionality

3. **Rate Limiting:**
   - Add rate limiting middleware to backend
   - Protect against abuse

4. **HTTPS Only:**
   - Both Render and Vercel use HTTPS by default ✅

5. **Environment Variables:**
   - Never commit `.env` files
   - Rotate API keys regularly
   - Use different keys for dev/staging/prod

---

## 📊 Monitoring

### Render Dashboard
- View logs: Real-time backend logs
- Monitor usage: CPU, memory, bandwidth
- Check deployments: History and status

### Vercel Dashboard
- View deployments: History and previews
- Analytics: Visitor stats (Pro plan)
- Performance: Core Web Vitals

---

## 🎯 Quick Reference

### URLs After Deployment

```bash
# Backend API
Production: https://ether-clinic-api.onrender.com
Health Check: https://ether-clinic-api.onrender.com/health
API Docs: https://ether-clinic-api.onrender.com/docs

# Frontend
Production: https://your-app.vercel.app
Preview: https://your-app-git-branch.vercel.app
```

### Environment Variables

**Backend (Render):**
- `DATABASE_URL` - Neon PostgreSQL connection string
- `ALLOWED_ORIGINS` - Frontend URLs (comma-separated)
- `PYTHON_VERSION` - 3.11.0

**Frontend (Vercel):**
- `VITE_API_URL` - Backend API URL

---

## ✅ Final Checklist

After deployment:

- [ ] Backend health check responds with 200 OK
- [ ] Frontend loads without errors
- [ ] Can create appointments from frontend
- [ ] Can view patients list
- [ ] No CORS errors in browser console
- [ ] API docs accessible at `/docs`
- [ ] All environment variables are set correctly
- [ ] `.env.local` files are NOT in git repository
- [ ] Custom domain configured (optional)

---

## 🆘 Need Help?

If you encounter issues:

1. **Check Logs:**
   - Render: Dashboard → Logs tab
   - Vercel: Dashboard → Deployments → View logs

2. **Verify Environment Variables:**
   - Backend: Render → Environment
   - Frontend: Vercel → Settings → Environment Variables

3. **Test Locally First:**
   ```bash
   # Backend
   cd backend/api
   uvicorn main:app --reload
   
   # Frontend
   cd frontend
   npm run dev
   ```

---

## 🎉 Congratulations!

Your Ether Clinic application is now live!

- **Backend API:** Fast, scalable, and secure
- **Frontend:** Optimized and cached globally
- **Database:** Serverless PostgreSQL on Neon

**Next Steps:**
- Add custom domain
- Set up monitoring/alerts
- Implement authentication
- Add more features!

---

**Last Updated:** November 20, 2025  
**Status:** Production Ready ✅
