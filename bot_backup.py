import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import schedule
import time
import threading
from datetime import datetime
import pytz

from config import TELEGRAM_BOT_TOKEN, DAILY_REMINDER_TIME, TIMEZONE, validate_config
from gpt_helper import GPTHelper
from task_manager import TaskManager
from nlp_helper import NLPHelper
from voice_helper import VoiceHelper
from smart_features import SmartFeatures

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize helpers
gpt = GPTHelper()
task_manager = TaskManager()
nlp = NLPHelper()
voice = VoiceHelper()
smart = SmartFeatures(task_manager, gpt)

# Store user states for conversation flow
user_states = {}

class ProductivityBot:
    """Main Telegram Productivity Bot"""
    
    def __init__(self):
        self.gpt = gpt
        self.task_manager = task_manager
        self.nlp = nlp
        self.voice = voice
        self.smart = smart
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        user_id = user.id
        
        welcome_message = f"""
🌟 **Welcome to SycproBot!** 🌟

Hi {user.first_name}! I'm your personal AI productivity assistant. 

**What I can do for you:**
✅ Track your daily tasks
📝 Send you reminders
🔥 Keep you motivated
🎯 Help you stay productive

**Commands:**
/start - Start the bot
/addtask - Add a new task
/mytasks - View all your tasks
/stats - See your progress
/goal - Break down a big goal
/moodreport - Get weekly mood report
/help - Get help

✨ **New AI Features:**
🎤 Send voice messages to create tasks!
🧠 Smart priority detection
💡 Learns your productive times
😊 Mood tracking & adaptive responses

Let's get started! What would you like to do today? 💪
"""
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def add_task_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /addtask command with NLP parsing"""
        user_id = update.effective_user.id
        
        # Check if task name was provided
        if context.args:
            task_text = ' '.join(context.args)
            
            # Use NLP to parse task with time, priority, etc.
            parsed = self.nlp.parse_task_with_time(task_text)
            
            # Add task with parsed information
            task = self.task_manager.add_task(
                task_name=parsed['task'],
                user_id=user_id,
                reminder_time=parsed['reminder_time'],
                priority=parsed['priority'],
                recurring=parsed['recurring']
            )
            
            # Build response with details
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
            emoji = priority_emoji.get(parsed['priority'], '🟡')
            
            details = f"✅ Task added: **{parsed['task']}**\n{emoji} Priority: {parsed['priority'].upper()}"
            
            if parsed['reminder_time']:
                details += f"\n⏰ Reminder: {parsed['reminder_time']}"
            
            if parsed['recurring']:
                details += f"\n🔄 Recurring: {parsed['recurring']}"
            
            # Get AI suggestion for best time
            suggestion = self.smart.suggest_best_time(user_id, parsed['task'])
            
            response = f"{details}\n\n💡 {suggestion}"
            
            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                "📝 **Add a task with natural language!**\n\n"
                "Examples:\n"
                "• `/addtask Study for exam tomorrow at 5 PM`\n"
                "• `/addtask Call mom every Sunday at 6 PM`\n"
                "• `/addtask Urgent: Complete report today`\n"
                "• `/addtask Workout in 3 days`\n\n"
                "I'll automatically detect time, priority, and recurrence! 🧠",
                parse_mode='Markdown'
            )
    
    async def my_tasks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mytasks command with priority indicators"""
        user_id = update.effective_user.id
        tasks = self.task_manager.get_user_tasks(user_id)
        
        if not tasks:
            await update.message.reply_text("You don't have any tasks yet! Use /addtask to create one. 📝")
            return
        
        pending_tasks = [t for t in tasks if t['status'] == 'pending']
        done_tasks = [t for t in tasks if t['status'] == 'done']
        
        # Sort pending by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        pending_tasks.sort(key=lambda x: priority_order.get(x.get('priority', 'medium'), 1))
        
        priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
        
        message = "📋 **Your Tasks:**\n\n"
        
        if pending_tasks:
            message += "⏳ **Pending:**\n"
            for task in pending_tasks:
                emoji = priority_emoji.get(task.get('priority', 'medium'), '🟡')
                recurring = ' 🔄' if task.get('recurring') else ''
                time_info = f" ⏰ {task.get('reminder_time')}" if task.get('reminder_time') else ''
                message += f"{emoji} {task['task']}{recurring}{time_info}\n"
            message += "\n"
        
        if done_tasks:
            message += "✅ **Completed:**\n"
            for task in done_tasks[:5]:  # Show last 5 completed
                message += f"• ~{task['task']}~\n"
        
        # Check for proactive reminders
        proactive = self.smart.proactive_reminder(user_id)
        if proactive:
            message += f"\n💡 **Reminder:** {proactive['message']}"
        
        # Add interactive buttons for pending tasks
        if pending_tasks:
            keyboard = []
            for task in pending_tasks[:5]:  # Show max 5 tasks
                keyboard.append([
                    InlineKeyboardButton(f"✅ {task['task'][:30]}", callback_data=f"done_{task['id']}"),
                    InlineKeyboardButton("❌", callback_data=f"skip_{task['id']}")
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text(message, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        user_id = update.effective_user.id
        stats = self.task_manager.get_daily_stats(user_id)
        
        summary = self.gpt.daily_summary(stats['done'], stats['pending'], stats['total'])
        
        message = f"""
📊 **Your Statistics:**

Total Tasks: {stats['total']}
✅ Completed: {stats['done']}
⏳ Pending: {stats['pending']}

{summary}
"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🤖 **SycproBot Help**

**Commands:**
/start - Start the bot
/addtask <task> - Add a new task
/mytasks - View all your tasks
/stats - See your progress
/goal <goal> - Break down a big goal
/moodreport - Weekly mood report
/help - Show this help message

**Smart Features:**
🎤 **Voice Tasks** - Send voice message to create tasks
🧠 **NLP Parsing** - "Remind me tomorrow at 5 PM"
🔴🟡🟢 **Auto Priority** - Detects urgent/important tasks
💡 **Pattern Learning** - Suggests best times
😊 **Mood Tracking** - Adapts to your energy
🔄 **Smart Rescheduling** - Learns from your habits

**Examples:**
• `/addtask Urgent: Submit report today`
• `/addtask Call mom every Sunday at 6 PM`
• `/addtask Workout in 3 days at 7 AM`
• Send voice: "Remind me to buy groceries tomorrow"

**Tips:**
• I learn your patterns as you use me
• Check /moodreport every week
• Use /goal for big projects

Need help? Just ask me anything! 💬
"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def goal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /goal command - decompose big goals"""
        user_id = update.effective_user.id
        
        if context.args:
            goal_text = ' '.join(context.args)
            
            await update.message.reply_text("🧠 Let me break that down into weekly milestones... ⏳")
            
            # Use GPT to decompose goal
            breakdown = self.smart.decompose_big_goal(goal_text)
            
            message = f"🎯 **Goal:** {breakdown['goal']}\n\n"
            message += "📅 **Weekly Breakdown:**\n\n"
            message += breakdown['breakdown_text']
            message += "\n\n💡 Should I add these as individual tasks?"
            
            # Add button to confirm
            keyboard = [[
                InlineKeyboardButton("✅ Yes, add all", callback_data=f"add_milestones_{user_id}"),
                InlineKeyboardButton("❌ No thanks", callback_data="dismiss")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Store milestones temporarily
            user_states[user_id] = {
                'state': 'goal_milestones',
                'milestones': breakdown['milestones']
            }
            
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                "🎯 **Break down a big goal!**\n\n"
                "Example: `/goal Learn Python programming`\n\n"
                "I'll create weekly milestones for you! 🚀",
                parse_mode='Markdown'
            )
    
    async def mood_report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /moodreport command"""
        user_id = update.effective_user.id
        
        report = self.smart.generate_weekly_mood_report(user_id)
        
        message = f"📊 **Weekly Mood & Productivity Report**\n\n{report}"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def voice_message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages and convert to tasks"""
        user_id = update.effective_user.id
        
        await update.message.reply_text("🎤 Transcribing your voice message... ⏳")
        
        try:
            # Get voice file
            voice = update.message.voice
            file = await context.bot.get_file(voice.file_id)
            
            # Download file
            file_path = f"voice_{user_id}_{voice.file_id}.ogg"
            await file.download_to_drive(file_path)
            
            # Transcribe
            transcribed_text = self.voice.transcribe_voice(file_path)
            
            if transcribed_text and not transcribed_text.startswith('⚠️'):
                # Parse and create task
                parsed = self.nlp.parse_task_with_time(transcribed_text)
                
                task = self.task_manager.add_task(
                    task_name=parsed['task'],
                    user_id=user_id,
                    reminder_time=parsed['reminder_time'],
                    priority=parsed['priority'],
                    recurring=parsed['recurring']
                )
                
                response = f"✅ **Created from voice:**\n\n"
                response += f"📝 Task: {parsed['task']}\n"
                if parsed['priority'] != 'medium':
                    response += f"🎯 Priority: {parsed['priority'].upper()}\n"
                if parsed['reminder_time']:
                    response += f"⏰ Reminder: {parsed['reminder_time']}\n"
                
                response += f"\n💬 You said: \"{transcribed_text}\""
                
                await update.message.reply_text(response, parse_mode='Markdown')
            else:
                await update.message.reply_text(transcribed_text or "Sorry, I couldn't transcribe that. Please try again! 🎤")
            
            # Clean up file
            import os
            if os.path.exists(file_path):
                os.remove(file_path)
                
        except Exception as e:
            logger.error(f"Error processing voice: {e}")
            await update.message.reply_text(
                "⚠️ Sorry, I had trouble processing your voice message. Please type your task instead! 📝"
            )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        if data.startswith('done_'):
            # Mark task as done
            task_id = int(data.split('_')[1])
            task = self.task_manager.mark_done(task_id, user_id)
            
            if task:
                celebration = self.gpt.celebrate_completion(task['task'])
                await query.edit_message_text(f"✅ **Task completed!**\n\n{celebration}", parse_mode='Markdown')
        
        elif data.startswith('skip_'):
            # Ask when to reschedule
            task_id = int(data.split('_')[1])
            task = self.task_manager.get_task_by_id(task_id, user_id)
            
            if task:
                # Check for smart rescheduling suggestion
                smart_suggestion = self.smart.smart_reschedule_suggestion(user_id, task_id)
                
                user_states[user_id] = {'state': 'awaiting_reschedule', 'task_id': task_id}
                motivation = self.gpt.motivate_incomplete(task['task'])
                
                message = f"{motivation}\n\n⏰ When should I remind you again?\n\n"
                message += f"Reply with time like: '2 PM', '8 PM', 'tomorrow', etc."
                
                if smart_suggestion:
                    message += f"\n\n💡 {smart_suggestion}"
                
                await query.edit_message_text(message, parse_mode='Markdown')
        
        elif data.startswith('add_milestones_'):
            # Add all milestones as tasks
            if user_id in user_states and user_states[user_id].get('state') == 'goal_milestones':
                milestones = user_states[user_id]['milestones']
                
                for milestone in milestones:
                    self.task_manager.add_task(milestone, user_id)
                
                await query.edit_message_text(
                    f"✅ **Added {len(milestones)} milestones!**\n\n"
                    f"Check them with /mytasks. Let's crush this goal! 🔥",
                    parse_mode='Markdown'
                )
                
                del user_states[user_id]
        
        elif data == 'dismiss':
            await query.edit_message_text("👍 Got it!")
            if user_id in user_states:
                del user_states[user_id]
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages with sentiment analysis"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Analyze sentiment
        sentiment = self.nlp.analyze_sentiment(message_text)
        self.smart.track_mood(user_id, sentiment)
        
        # Check if user is in a specific state
        if user_id in user_states:
            state = user_states[user_id]
            
            if state['state'] == 'awaiting_reschedule':
                task_id = state['task_id']
                task = self.task_manager.get_task_by_id(task_id, user_id)
                
                # Parse the time using NLP
                time_info = self.nlp.extract_datetime(message_text)
                new_time = time_info['time'] if time_info else message_text
                
                # Update reminder time
                self.task_manager.reschedule_task(task_id, user_id, new_time)
                
                confirmation = self.gpt.reschedule_confirmation(task['task'], message_text)
                confirmation = self.smart.adjust_tone_for_mood(user_id, confirmation)
                
                await update.message.reply_text(f"✅ {confirmation}")
                
                # Clear state
                del user_states[user_id]
                return
        
        # General conversation with mood-adjusted response
        response = self.gpt.handle_user_message(message_text)
        response = self.smart.adjust_tone_for_mood(user_id, response)
        
        await update.message.reply_text(response)
    
    async def send_daily_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        """Send daily reminder to all users"""
        # Get all unique user IDs
        all_tasks = self.task_manager.tasks
        user_ids = set(task['user_id'] for task in all_tasks)
        
        for user_id in user_ids:
            pending_tasks = self.task_manager.get_pending_tasks(user_id)
            
            if pending_tasks:
                greeting = self.gpt.morning_greeting(len(pending_tasks))
                
                message = f"{greeting}\n\n📋 **Today's Tasks:**\n\n"
                
                keyboard = []
                for i, task in enumerate(pending_tasks[:5], 1):
                    message += f"{i}. {task['task']}\n"
                    keyboard.append([
                        InlineKeyboardButton(f"✅ {task['task'][:30]}", callback_data=f"done_{task['id']}"),
                        InlineKeyboardButton("❌", callback_data=f"skip_{task['id']}")
                    ])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Error sending daily reminder to {user_id}: {e}")

def run_scheduler(application):
    """Run the scheduler in a separate thread"""
    async def send_reminder():
        await application.bot_data['bot'].send_daily_reminder(None)
    
    schedule.every().day.at(DAILY_REMINDER_TIME).do(
        lambda: application.create_task(send_reminder())
    )
    
    while True:
        schedule.run_pending()
        time.sleep(60)

def main():
    """Start the bot"""
    try:
        # Validate configuration
        validate_config()
        
        # Create the Application
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Initialize bot
        bot = ProductivityBot()
        
        # Store bot in application data
        application.bot_data['bot'] = bot
        
        # Register handlers
        application.add_handler(CommandHandler("start", bot.start_command))
        application.add_handler(CommandHandler("addtask", bot.add_task_command))
        application.add_handler(CommandHandler("mytasks", bot.my_tasks_command))
        application.add_handler(CommandHandler("stats", bot.stats_command))
        application.add_handler(CommandHandler("goal", bot.goal_command))
        application.add_handler(CommandHandler("moodreport", bot.mood_report_command))
        application.add_handler(CommandHandler("help", bot.help_command))
        application.add_handler(CallbackQueryHandler(bot.button_callback))
        application.add_handler(MessageHandler(filters.VOICE, bot.voice_message_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
        
        # Start scheduler in separate thread (optional for now)
        # scheduler_thread = threading.Thread(target=run_scheduler, args=(application,), daemon=True)
        # scheduler_thread.start()
        
        # Start the bot
        logger.info("🚀 SycproBot is starting...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == '__main__':
    main()
