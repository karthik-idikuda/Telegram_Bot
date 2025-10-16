# 🚀 Advanced AI Features Guide

Your SycproBot now has **cutting-edge AI capabilities**! Here's everything you need to know.

---

## ✨ **New Features Overview**

### 🎤 **1. Voice-to-Task Conversion**
**Send voice messages → Automatically creates tasks!**

**How it works:**
1. Record a voice message in Telegram
2. Bot transcribes it using AI
3. Automatically creates a task with NLP parsing

**Example:**
```
🎤 "Remind me to buy groceries tomorrow at 5 PM"
→ ✅ Task created: "Buy groceries"
→ ⏰ Reminder: 17:00
→ 📅 Tomorrow
```

**Note:** For voice transcription to work, add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=your_key_here
```

---

### 🧠 **2. Smart Task Prioritization**
**Auto-detects priority from keywords!**

**Priority Levels:**
- 🔴 **HIGH** - urgent, asap, critical, deadline, today
- 🟡 **MEDIUM** - important, soon, this week
- 🟢 **LOW** - maybe, someday, eventually

**Examples:**
```
/addtask Urgent: Submit report today
→ 🔴 HIGH priority

/addtask Maybe learn guitar someday
→ 🟢 LOW priority
```

---

### 💬 **3. Natural Language Processing**
**Understands complex task descriptions!**

**What it can parse:**
- ⏰ **Time**: "at 5 PM", "6:30", "18:00"
- 📅 **Dates**: "tomorrow", "next week", "in 3 days"
- 🔄 **Recurring**: "every Sunday", "daily", "weekly"
- 🎯 **Priority**: Auto-detected from keywords

**Examples:**
```
/addtask Call mom every Sunday at 6 PM
→ Task: "Call mom"
→ Recurring: Weekly (Sundays)
→ Time: 18:00

/addtask Workout in 3 days at 7 AM
→ Task: "Workout"
→ Reminder: 3 days from now at 07:00

/addtask Important: Review project tomorrow
→ Task: "Review project"
→ Priority: MEDIUM
→ Date: Tomorrow
```

---

### 💡 **4. Context-Aware Suggestions**
**Learns when you're most productive!**

**How it works:**
- Tracks when you complete tasks
- Identifies your peak productivity hours
- Suggests optimal times for new tasks

**Example:**
```
/addtask Study for exam
→ Bot: "I noticed you complete most tasks at 09:00. 
       Would you like me to schedule it then? 📊"
```

**View your patterns:**
```
/stats
→ Shows completion rate, best times, streaks
```

---

### 😊 **5. Sentiment Analysis & Mood Tracking**
**Adapts to your emotional state!**

**What it does:**
- Analyzes your messages for mood
- Adjusts response tone based on energy level
- Tracks mood over time

**Mood States:**
- 🎉 **Positive** → Enthusiastic responses
- 😌 **Neutral** → Friendly, encouraging
- 😔 **Low Energy** → Gentle, supportive

**Example:**
```
You: "I'm so tired today..."
→ Bot (gentle): "That's okay! Rest a bit. 
   How about one small task to start? 💙"

You: "Let's crush it!"
→ Bot (energetic): "YES! Let's GO! 🔥
   Time to dominate your day! 💪"
```

**Weekly Report:**
```
/moodreport
→ "📊 This week: 5 positive days, 2 tough days
   You've been crushing it! Keep the energy up! 🌟"
```

---

### ⏰ **6. Proactive Reminders**
**AI predicts when you'll forget tasks!**

**How it works:**
- Monitors tasks older than 3 days
- Sends gentle reminders automatically
- Appears in `/mytasks` view

**Example:**
```
/mytasks
→ 💡 Reminder: "You haven't worked out in 3 days. 
   Ready to get back? 💪"
```

---

### 🔄 **7. Smart Rescheduling**
**Suggests better times if you keep skipping!**

**How it works:**
- Tracks reschedule count per task
- After 2+ reschedules, suggests optimal time
- Based on your completion patterns

**Example:**
```
You: [Click ❌ on "Workout" for 3rd time]

Bot: "You've rescheduled 'Workout' 3 times. 
     You usually complete tasks at 09:00. 
     Want to try mornings instead? 🌅"
```

---

### 🎯 **8. Goal Decomposition**
**Breaks big goals into weekly milestones!**

**How to use:**
```
/goal Learn Python programming

→ Bot creates:
Week 1: Learn Python basics and syntax
Week 2: Practice with variables and data types
Week 3: Master control flow (if/else, loops)
Week 4: Functions and modules
Week 5: Work on first project
Week 6: Learn libraries (NumPy, Pandas)

✅ Add all as tasks?
```

**Features:**
- AI-powered breakdown using GPT
- Realistic weekly goals
- One-click to add all milestones
- Automatically organized

---

## 📋 **All Commands**

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Welcome message | `/start` |
| `/addtask` | Add task with NLP | `/addtask Urgent: Call boss tomorrow at 3 PM` |
| `/mytasks` | View all tasks | `/mytasks` |
| `/stats` | Progress & patterns | `/stats` |
| `/goal` | Break down big goal | `/goal Learn Web Development` |
| `/moodreport` | Weekly mood analysis | `/moodreport` |
| `/help` | Show help | `/help` |

---

## 🎨 **Visual Indicators**

### Priority Emojis:
- 🔴 **High Priority**
- 🟡 **Medium Priority**
- 🟢 **Low Priority**

### Task Status:
- ✅ **Completed**
- ⏳ **Pending**
- 🔄 **Recurring**

### Time Indicators:
- ⏰ **Reminder time set**
- 📅 **Scheduled for specific date**

---

## 💬 **Smart Conversation Examples**

### Adding Tasks:
```
You: /addtask Call dentist tomorrow
Bot: ✅ Task added: Call dentist
     🟡 Priority: MEDIUM
     ⏰ Reminder: Tomorrow at 09:00
     
     💡 I noticed you complete most tasks in the morning. 
     Perfect timing! 🌞
```

### Voice Messages:
```
You: 🎤 [Voice] "Remind me to buy milk and eggs tomorrow afternoon"

Bot: 🎤 Transcribing your voice message... ⏳

     ✅ Created from voice:
     
     📝 Task: Buy milk and eggs
     ⏰ Reminder: Tomorrow 14:00
     
     💬 You said: "Remind me to buy milk and eggs tomorrow afternoon"
```

### Big Goals:
```
You: /goal Get fit and healthy

Bot: 🧠 Let me break that down into weekly milestones... ⏳

     🎯 Goal: Get fit and healthy
     
     📅 Weekly Breakdown:
     
     Week 1: Start with 15-min daily walks
     Week 2: Add basic stretching routine
     Week 3: Begin strength training 2x/week
     Week 4: Increase cardio to 30 mins
     Week 5: Track nutrition and meals
     Week 6: Establish consistent sleep schedule
     
     💡 Should I add these as individual tasks?
     [✅ Yes, add all] [❌ No thanks]
```

### Mood Tracking:
```
You: I'm feeling overwhelmed with work

Bot: 😔 I understand. It's okay to feel this way. 
     Let's take it one step at a time. 
     
     Would you like me to help prioritize your tasks? 💙
     
     [View Tasks] [Take a Break]
```

---

## 🔧 **Configuration**

### Required in `.env`:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
OPENROUTER_API_KEY=your_openrouter_key
GPT_MODEL=openai/gpt-oss-20b:free
```

### Optional (for voice):
```env
OPENAI_API_KEY=your_openai_key
```

---

## 📊 **How AI Learns About You**

### Pattern Analysis:
- **Completion times** → Suggests best schedule
- **Reschedule frequency** → Detects problematic tasks
- **Task age** → Proactive reminders
- **Mood trends** → Adaptive responses

### Privacy:
- All data stored locally in `tasks.json`
- No external sharing
- Delete anytime with account removal

---

## 🎯 **Pro Tips**

1. **Use natural language** - The bot understands conversational task descriptions
2. **Include time/date** - "tomorrow at 5 PM" works perfectly
3. **Mark priorities** - Use words like "urgent" or "important"
4. **Check mood reports** - Weekly insights help improve productivity
5. **Break big goals** - Use `/goal` for projects that feel overwhelming
6. **Send voice messages** - Fastest way to add tasks on the go

---

## 🆕 **What's Different?**

### Before:
```
/addtask Study
→ Simple task created
```

### Now:
```
/addtask Urgent: Study for exam tomorrow at 8 PM
→ Task: "Study for exam"
→ 🔴 HIGH priority
→ ⏰ Tomorrow at 20:00
→ 💡 "You're 40% more productive in evenings. Great choice! 🌙"
```

---

## 🚀 **Coming Soon**

- ✨ GPT-4 Vision (screenshot to tasks)
- 📊 Web dashboard
- 🏆 Gamification & XP system
- 📧 Email integration
- 📅 Calendar sync
- 🎵 Focus music suggestions

---

## 🐛 **Troubleshooting**

### Voice not working?
→ Add `OPENAI_API_KEY` to `.env` file

### NLP parsing issues?
→ Bot uses patterns - try rephrasing

### Mood seems off?
→ Chat more! AI learns from interactions

### Lost patterns?
→ Stored in memory - persist after restart by upgrading to database

---

## 💡 **Feature Requests?**

Want a specific feature? Just tell the bot what you need! 
The AI adapts and improves based on your usage.

---

**Happy productivity! Your bot just got 10x smarter! 🧠🔥**
