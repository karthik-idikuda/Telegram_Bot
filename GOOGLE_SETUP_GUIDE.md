# 🔐 Google Sheets & Gmail Setup Guide

## 📋 **What You Need**

Your bot is ready to sync tasks to Google Sheets, but needs proper credentials!

### **Current Status:**
- ✅ Sheet ID configured: `16i-wJ7uPAGmpmpHTHUkdkjUZtb0vbLRMJ8aZzOAETaY`
- ✅ Gmail configured: `karthik.idikuda129259@marwadiuniversity.ac.in`
- ⚠️ Missing: Service Account credentials file

---

## 🚀 **Quick Setup (5 Minutes)**

### **Step 1: Create Service Account**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable these APIs:
   - ✅ Google Sheets API
   - ✅ Google Drive API
   - ✅ Gmail API

### **Step 2: Create Credentials**

1. Go to **APIs & Services > Credentials**
2. Click **+ CREATE CREDENTIALS**
3. Select **Service Account**
4. Fill in details:
   - Name: `SycproBot`
   - Description: `Telegram Bot Task Sync`
5. Click **CREATE AND CONTINUE**
6. Skip role assignment (click CONTINUE)
7. Click **DONE**

### **Step 3: Generate Key**

1. Click on the service account you just created
2. Go to **Keys** tab
3. Click **ADD KEY > Create new key**
4. Choose **JSON** format
5. Click **CREATE**
6. **Download the JSON file** 📥

### **Step 4: Rename & Move File**

1. Rename downloaded file to: `credentials.json`
2. Move it to your project folder:
   ```
   /Users/karthik/Downloads/All Projects/TELEGRAM/credentials.json
   ```

### **Step 5: Share Your Google Sheet**

1. Open your [Google Sheet](https://docs.google.com/spreadsheets/d/16i-wJ7uPAGmpmpHTHUkdkjUZtb0vbLRMJ8aZzOAETaY/edit)
2. Click **Share** button
3. Find the email from `credentials.json`:
   - Open the file
   - Look for `"client_email"` field
   - Copy that email (looks like: `sycprobot@xxxxx.iam.gserviceaccount.com`)
4. Add that email as **Editor** to your sheet
5. Click **Send**

---

## 📧 **Gmail App Password (For Email Notifications)**

To actually SEND emails (not just prepare them):

1. Go to your [Google Account](https://myaccount.google.com/)
2. Security > 2-Step Verification (turn it ON if not already)
3. Go back to Security
4. Scroll to **App passwords**
5. Create new app password:
   - App: `Mail`
   - Device: `Other` → Type "SycproBot"
6. Copy the 16-character password
7. Add to `.env`:
   ```
   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
   ```

---

## ✅ **Verify Setup**

Once you have `credentials.json` in place:

1. Restart the bot
2. Send a task in Telegram
3. Check your Google Sheet - it should appear automatically! 📊
4. Check your email for daily digest 📧

---

## 🔒 **Security Notes**

- ⚠️ **NEVER** commit `credentials.json` to GitHub
- ⚠️ It's already in `.gitignore` - keep it there!
- ✅ Service account has limited permissions
- ✅ Only works with sheets you explicitly share

---

## 🆘 **Troubleshooting**

### **"File not found" error**
- Make sure `credentials.json` is in the TELEGRAM folder
- Check the filename is exactly `credentials.json`

### **"Permission denied" error**
- Make sure you shared the sheet with the service account email
- Check the service account has Editor permissions

### **"API not enabled" error**
- Go back to Google Cloud Console
- Enable Google Sheets API and Google Drive API

---

## 📱 **Alternative: Keep Using JSON (No Setup Required)**

If you don't want to set up Google Sheets right now:
- ✅ Bot works perfectly with just JSON storage
- ✅ All features work (tasks, analytics, reports)
- ✅ Data saved locally in `tasks.json`
- 📊 Google Sheets is optional - just for cloud backup!

---

## 🎯 **What Happens After Setup**

Once credentials are in place:

1. **Auto-Sync**: Every task you add syncs to Google Sheet
2. **Real-time Updates**: Mark done in Telegram → Updates in Sheet
3. **Cloud Backup**: Your data is safe in Google Drive
4. **Easy Export**: Download as CSV/Excel anytime
5. **Share with Team**: Anyone can view progress
6. **Email Digests**: Daily summaries sent automatically

---

## 💡 **Quick Test Commands**

After setup, try these:
```
/addtask Test Google Sheets sync
/mytasks
/stats
```

Then check your [Google Sheet](https://docs.google.com/spreadsheets/d/16i-wJ7uPAGmpmpHTHUkdkjUZtb0vbLRMJ8aZzOAETaY/edit) - the task should be there! 🎉

---

Need help? The bot will tell you if credentials are missing!
