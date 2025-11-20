# 🚀 Quick Deployment Checklist

## Before You Deploy

### Security (CRITICAL!)
- [ ] Regenerated all API keys from agent-python/.env.local
- [ ] Verified `.env.local` is in `.gitignore`
- [ ] Confirmed no sensitive data in git: `git status`

### Code Verification
- [ ] Backend runs locally: `cd backend/api && uvicorn main:app --reload`
- [ ] Frontend runs locally: `cd frontend && npm run dev`
- [ ] Database connection works
- [ ] All tests pass

---

## Deploy Backend to Render

### Setup
- [ ] Created Render account at render.com
- [ ] Connected GitHub repository
- [ ] Created new Web Service

### Configuration
- [ ] Root Directory: `backend/api`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Python Version: 3.11

### Environment Variables
- [ ] `DATABASE_URL` - Set to Neon PostgreSQL URL
- [ ] `ALLOWED_ORIGINS` - Will update after frontend deploy
- [ ] `PYTHON_VERSION=3.11.0`

### Post-Deploy
- [ ] Service deployed successfully
- [ ] Health check works: `curl https://your-api.onrender.com/health`
- [ ] API docs accessible: `https://your-api.onrender.com/docs`
- [ ] **SAVED API URL:** ___________________________________

---

## Deploy Frontend to Vercel

### Setup
- [ ] Created Vercel account at vercel.com
- [ ] Connected GitHub repository
- [ ] Started new project import

### Configuration
- [ ] Framework: Vite
- [ ] Root Directory: `frontend`
- [ ] Build Command: `npm run build`
- [ ] Output Directory: `dist`

### Environment Variables
- [ ] `VITE_API_URL` - Set to Render backend URL
- [ ] Value: `https://your-api.onrender.com` (from above)

### Post-Deploy
- [ ] Deployment successful
- [ ] Frontend loads without errors
- [ ] **SAVED FRONTEND URL:** ___________________________________

---

## Connect Frontend & Backend

### Update CORS
- [ ] Go to Render dashboard → Environment
- [ ] Update `ALLOWED_ORIGINS` with Vercel URL(s)
- [ ] Example: `https://your-app.vercel.app,https://your-app-git-main.vercel.app`
- [ ] Save (triggers automatic redeploy)

### Test Connection
- [ ] Open frontend in browser
- [ ] Check browser console for errors
- [ ] Navigate to Appointments page
- [ ] Try creating a test appointment
- [ ] Verify data appears correctly

---

## Final Verification

### Functionality Tests
- [ ] Can view patients list
- [ ] Can create new appointment
- [ ] Can edit appointment
- [ ] Can cancel appointment
- [ ] Calendar view works
- [ ] No CORS errors in console
- [ ] Times display correctly (no timezone issues)

### Performance
- [ ] Frontend loads in <3 seconds
- [ ] API responds in <1 second
- [ ] No 500 errors in logs

### Security
- [ ] All API keys are regenerated
- [ ] `.env` files not in repository
- [ ] HTTPS enabled (automatic on Render/Vercel)

---

## Optional Enhancements

### Custom Domains
- [ ] Add custom domain to Vercel
- [ ] Add custom domain to Render
- [ ] Update CORS origins accordingly

### Monitoring
- [ ] Set up Render alerts
- [ ] Enable Vercel Analytics
- [ ] Configure error tracking

---

## 🎉 Deployment Complete!

If all checkboxes are marked, your application is live!

**Production URLs:**
- Frontend: https://_________________________.vercel.app
- Backend: https://_________________________.onrender.com

**Next Steps:**
- Share with users
- Monitor logs for first 24 hours
- Plan next features
- Enjoy your deployed app! 🚀

---

**Deployment Date:** __________________  
**Deployed By:** __________________
