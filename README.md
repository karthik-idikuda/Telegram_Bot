# 🤖 SycproBot - AI Telegram Productivity Assistant

Your personal AI productivity coach that lives in Telegram!

## 🌟 Features

- ✅ **Daily Task Reminders** - Get reminded about your tasks every morning
- 📝 **Smart Task Management** - Add, complete, and reschedule tasks easily
- 🤖 **AI-Powered Responses** - Natural conversations with GPT
- 🔥 **Motivation & Encouragement** - Stay motivated with AI-generated messages
- 📊 **Progress Tracking** - See your daily statistics
- ⏰ **Smart Rescheduling** - Reschedule tasks with natural language

### 🆕 **Advanced AI Features:**
- 🎤 **Voice-to-Task** - Send voice messages to create tasks automatically
- 🧠 **Smart Prioritization** - Auto-detects urgency (🔴 High, 🟡 Medium, 🟢 Low)
- 💬 **NLP Parsing** - Understands "tomorrow at 5 PM", "every Sunday", etc.
- 💡 **Pattern Learning** - Learns your productive hours and suggests times
- 😊 **Mood Tracking** - Analyzes sentiment and adapts tone
- ⏰ **Proactive Reminders** - AI predicts forgotten tasks
- 🔄 **Auto-Rescheduling** - Suggests better times if you keep skipping
- 🎯 **Goal Breakdown** - Decomposes big goals into weekly milestones

[📖 **View Full Features Guide →**](ADVANCED_FEATURES.md)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment Variables

The `.env` file is already configured with your tokens. Make sure it contains:

```env
TELEGRAM_BOT_TOKEN=your_token_here
OPENROUTER_API_KEY=your_key_here
GPT_MODEL=openai/gpt-oss-20b:free
```

### 3. Run the Bot

```bash
python bot.py
```

### 4. Start Using Your Bot

1. Open Telegram
2. Search for `@SycproBot`
3. Send `/start`
4. Start adding tasks!

## 📝 Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and see welcome message |
| `/addtask <task>` | Add a new task (supports NLP!) |
| `/mytasks` | View all your tasks with priorities |
| `/stats` | See your progress statistics |
| `/goal <goal>` | Break down a big goal into milestones |
| `/moodreport` | Get weekly mood & productivity report |
| `/help` | Get help and usage instructions |

## 💡 Usage Examples

### Add a Task (with NLP)
```
/addtask Study for exam tomorrow at 5 PM
→ 🟡 Priority: MEDIUM
→ ⏰ Reminder: Tomorrow 17:00

/addtask Urgent: Submit report today
→ 🔴 Priority: HIGH

/addtask Call mom every Sunday at 6 PM
→ 🔄 Recurring: Weekly
```

### Voice to Task
```
🎤 Record: "Remind me to buy groceries tomorrow"
→ ✅ Task created: "Buy groceries"
→ 📅 Scheduled for tomorrow
```

### Break Down Big Goals
```
/goal Learn Python programming
→ AI creates 6 weekly milestones
→ One-click to add all as tasks
```

### View Tasks
```
/mytasks
```
You'll see interactive buttons to mark tasks as done or skip them.

### Check Progress
```
/stats
```
Get AI-generated summary of your productivity.

## 🏗️ Project Structure

```
TELEGRAM/
├── bot.py              # Main bot logic with AI features
├── gpt_helper.py       # GPT integration
├── task_manager.py     # Task management with priorities
├── nlp_helper.py       # Natural language processing
├── voice_helper.py     # Voice transcription
├── smart_features.py   # Advanced AI features
├── config.py           # Configuration loader
├── .env                # Environment variables (DO NOT SHARE)
├── requirements.txt    # Python dependencies
├── tasks.json          # Task storage (auto-generated)
├── README.md           # This file
└── ADVANCED_FEATURES.md # Detailed features guide
```

## 🔧 Tech Stack

- **Bot Framework**: `python-telegram-bot` v20.7
- **AI Model**: OpenRouter (GPT-OSS-20B Free)
- **NLP**: TextBlob for sentiment analysis
- **Voice**: OpenAI Whisper (optional)
- **Date Parsing**: python-dateutil
- **Storage**: JSON file (can upgrade to Google Sheets)
- **Scheduler**: Python `schedule` module

## 🎯 How It Works

1. **User adds tasks** via `/addtask` command
2. **Tasks stored** in `tasks.json` file
3. **Daily reminders** sent at 8 AM (configurable)
4. **Interactive buttons** allow quick task completion
5. **GPT generates** natural, motivating responses
6. **Progress tracked** and summarized with AI

## 📊 Future Enhancements

- [x] Voice-to-task conversion
- [x] Smart priority detection
- [x] Natural language parsing
- [x] Mood tracking & adaptive responses
- [x] Pattern learning & suggestions
- [x] Goal decomposition
- [ ] Google Sheets integration
- [ ] Web dashboard
- [ ] GPT-4 Vision (screenshot to tasks)
- [ ] Calendar sync
- [ ] Gamification & XP system
- [ ] Email integration
- [ ] Multi-language support

## 🚀 Deployment Options

### Option 1: Replit (Recommended for beginners)
1. Create account at [Replit.com](https://replit.com)
2. Import this project
3. Add environment variables in Secrets
4. Click "Run"
5. Use UptimeRobot to keep it alive 24/7

### Option 2: Local Machine
```bash
python bot.py
```
Keep terminal open for bot to run.

### Option 3: Cloud Server (VPS)
Deploy to any Linux server with Python 3.8+

## 🔐 Security Notes

⚠️ **IMPORTANT**: 
- Never share your `.env` file
- Never commit tokens to GitHub
- Keep your API keys secure

## 🐛 Troubleshooting

### Bot not responding?
- Check if `bot.py` is running
- Verify token in `.env` file
- Check internet connection

### GPT not working?
- Verify OpenRouter API key
- Check API quota/limits
- Try switching to different model

### Tasks not saving?
- Check write permissions
- Verify `tasks.json` is created
- Check file path in `task_manager.py`

## 📞 Support

- Bot: [@SycproBot](https://t.me/SycproBot)
- Issues: Create an issue in the repository

## 📄 License

MIT License - Feel free to modify and use!

## 🎉 Credits

Built with ❤️ using:
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [OpenRouter](https://openrouter.ai/)
- [GPT-OSS-20B](https://openrouter.ai/models/openai/gpt-oss-20b)

---

**Happy Productivity! 🔥**
# Telegram_Bot
