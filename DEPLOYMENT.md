# 🚀 Deploy Your Telegram Bot to Railway (FREE & 24/7)

This guide will help you deploy your SycproBot to Railway.app for **free, permanent hosting** with no sleep mode!

---

## 📋 Prerequisites

1. ✅ GitHub account (free)
2. ✅ Railway account (free - sign up with GitHub)
3. ✅ Your bot's API keys ready

---

## 🔧 Step 1: Prepare Your Code

### 1.1 Create a GitHub Repository

```bash
# Navigate to your project folder
cd "/Users/karthik/Downloads/All Projects/TELEGRAM"

# Initialize git (if not already done)
git init

# Create .gitignore to protect secrets
echo ".env
*.pyc
__pycache__/
credentials.json
xerironx-studio-472418-a23db74a64d6.json
tasks.json
gamification_data.json
.DS_Store" > .gitignore

# Add all files
git add .

# Commit
git commit -m "Initial commit - Ready for Railway deployment"

# Create repo on GitHub.com and push
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

---

## 🚂 Step 2: Deploy to Railway

### 2.1 Sign Up & Create Project

1. Go to [railway.app](https://railway.app)
2. Click **"Start a New Project"**
3. Choose **"Deploy from GitHub repo"**
4. Select your repository
5. Railway will auto-detect Python and start deployment

### 2.2 Add Environment Variables

Click on your project → **Variables** tab → Add these:

```
TELEGRAM_BOT_TOKEN=8287894687:AAE-rE8QU8syrP4IS_PcbF_MtY-jB1wjJdM
OPENROUTER_API_KEY=your_actual_key_here
SHEET_ID=your_sheet_id_here
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
BOT_PERSONALITY=coach
```

**⚠️ Important:** Click **"Add"** after each variable!

### 2.3 Deploy

Railway will automatically:
- ✅ Install dependencies from `requirements.txt`
- ✅ Run the bot using `Procfile`
- ✅ Keep it running 24/7!

---

## 🎯 Step 3: Verify Deployment

### Check Logs
1. Go to your Railway project
2. Click **"Deployments"** tab
3. View real-time logs
4. You should see: `✅ Google Sheets connected successfully!`

### Test Your Bot
Open Telegram and message: **@SycproBot**
- Try: `remind me to test deployment in 1 minute`
- Check if reminder arrives!

---

## 📊 Monitor Your Bot

### Railway Dashboard Shows:
- 💰 **Free credits used** ($5/month free)
- 📈 **CPU & Memory usage**
- 📝 **Live logs**
- 🔄 **Restart/Redeploy** buttons

### Typical Usage:
Your bot uses **~30MB RAM** and minimal CPU, so $5 credit = **500+ hours** of runtime!

---

## 🔄 Update Your Bot

When you make code changes:

```bash
# Make your changes locally
# Test them first!

# Commit and push
git add .
git commit -m "Added new feature"
git push

# Railway auto-redeploys! ✨
```

---

## 🆘 Troubleshooting

### Bot Not Starting?
1. Check **Environment Variables** are set correctly
2. View **Logs** for error messages
3. Verify `Procfile` exists and says `worker: python bot.py`

### "Module not found" Error?
- Add missing package to `requirements.txt`
- Push to GitHub (Railway will reinstall)

### Out of Free Credits?
- Railway gives $5/month
- Upgrade to $5/month plan for unlimited
- Or use Render.com (750 hrs/month free)

---

## 🎁 Bonus: Alternative Free Hosts

### If Railway Credits Run Out:

#### **Render.com** (750 hrs/month)
1. Sign up at [render.com](https://render.com)
2. Create "Web Service"
3. Connect GitHub repo
4. Add environment variables
5. Deploy!

**Note:** Sleeps after 15 min inactivity (but free forever)

#### **Fly.io** (3 VMs free)
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Deploy
flyctl launch
```

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] `.gitignore` protecting secrets
- [ ] Railway project created
- [ ] All environment variables added
- [ ] Bot deployed and running
- [ ] Tested with Telegram message
- [ ] Monitoring logs for errors

---

## 🔐 Security Tips

1. **NEVER** commit `.env` file to Git
2. **NEVER** share API keys publicly
3. Use Railway's **Environment Variables** feature
4. Rotate keys if exposed accidentally

---

## 🎉 Success!

Your bot is now running **24/7 for FREE** on Railway! 

**Next Steps:**
- Monitor logs occasionally
- Update bot with new features via Git push
- Share your bot with friends!

---

## 📞 Need Help?

If deployment fails:
1. Check Railway logs
2. Verify all environment variables
3. Test bot locally first (`python bot.py`)
4. Ask for help with error messages

**Your bot is production-ready!** 🚀
