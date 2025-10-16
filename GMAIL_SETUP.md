# Gmail App Password Setup Guide

## Why You Need This

**Gmail API Key ≠ Email Sending**
- `GMAIL_API_KEY` is for **reading** emails (Gmail API)
- To **send** emails via SMTP, you need a **Gmail App Password**

## Steps to Get Gmail App Password

### 1. Enable 2-Step Verification
1. Go to: https://myaccount.google.com/security
2. Find **"2-Step Verification"** 
3. Click **"Get Started"** and follow the steps
4. ✅ 2-Step Verification must be ON

### 2. Create App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Sign in if prompted
3. Under **"Select app"**, choose **"Mail"**
4. Under **"Select device"**, choose **"Other (Custom name)"**
5. Enter name: `SycproBot` or `Telegram Bot`
6. Click **"Generate"**
7. **Copy the 16-character password** (looks like: `abcd efgh ijkl mnop`)
   - ⚠️ You can only see this once! Copy it now.

### 3. Add to .env File
1. Open `/Users/karthik/Downloads/All Projects/TELEGRAM/.env`
2. Add this line (replace with your actual App Password):
   ```
   GMAIL_APP_PASSWORD=abcdefghijklmnop
   ```
   **Note:** Remove all spaces from the App Password!

### 4. Restart Your Bot
```bash
# Stop the bot (Ctrl+C in terminal)
# Then start it again:
python bot.py
```

## Testing

After setup, test by saying in Telegram:
```
send hi in mail to karthik.idikuda129259@marwadiuniversity.ac.in
```

You should see:
```
✅ Email sent successfully!
   To: karthik.idikuda129259@marwadiuniversity.ac.in
   Subject: Message from SycproBot
```

And receive the email in your inbox! 📧

## Troubleshooting

### "Gmail authentication failed"
- Double-check the App Password (no spaces!)
- Make sure 2-Step Verification is enabled
- Try generating a new App Password

### "Less secure app access"
- You don't need this! App Passwords work with any security settings
- Old method, ignore it

### Still not working?
- Check `GMAIL_ADDRESS` is correct in `.env`
- Make sure both `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD` are set
- Check terminal output for specific error messages

## Security Notes

✅ **App Passwords are safe:**
- They only work for this specific app
- You can revoke them anytime at: https://myaccount.google.com/apppasswords
- If compromised, just delete it and create a new one

❌ **Never share your App Password:**
- Don't commit `.env` to GitHub
- `.env` is already in `.gitignore` - keep it there!
