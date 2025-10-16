# 🚀 Quick Deployment Guide

## ⚡ Deploy to Railway (Recommended - FREE 24/7)

### Option 1: Automatic (Easy)
```bash
# Run the helper script
./deploy-to-railway.sh

# Then follow the instructions shown
```

### Option 2: Manual

1. **Create GitHub Repo**
   - Go to github.com/new
   - Create a new repository
   - Don't add README or .gitignore

2. **Push Your Code**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git branch -M main
   git push -u origin main
   ```

3. **Deploy to Railway**
   - Go to [railway.app](https://railway.app)
   - Click "Start a New Project"
   - Choose "Deploy from GitHub repo"
   - Select your repository
   - Add environment variables (see below)
   - Deploy! 🎉

---

## 🔐 Environment Variables

Add these in Railway dashboard → Variables:

```
TELEGRAM_BOT_TOKEN=your_bot_token
OPENROUTER_API_KEY=your_openrouter_key
SHEET_ID=your_google_sheet_id
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
BOT_PERSONALITY=coach
```

---

## 📖 Full Documentation

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for:
- Detailed step-by-step instructions
- Troubleshooting guide
- Alternative hosting options
- Security best practices

---

## ✅ Quick Checklist

- [ ] Bot works locally (`python bot.py`)
- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] Environment variables added
- [ ] Bot deployed and running
- [ ] Tested on Telegram

---

## 🎉 That's It!

Your bot will run **24/7 for FREE** on Railway!

**Need help?** Check the logs in Railway dashboard or read DEPLOYMENT.md
