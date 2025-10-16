"""
SycproBot - AI Productivity Assistant
Enhanced with Phase 1 Features:
- Pomodoro Timer
- Time Tracking  
- Gamification (XP, Levels, Achievements)
- Recurring Tasks
- Theme/Personality System
- Weekly Analytics
- Progress Visualization
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import schedule
import time
import threading
from datetime import datetime
import pytz

from config import validate_config, config
from gpt_helper import GPTHelper
from task_manager import TaskManager
from nlp_helper import NLPHelper
from voice_helper import VoiceHelper
from smart_features import SmartFeatures
from pomodoro_manager import PomodoroManager
from time_tracker import TimeTracker
from gamification_manager import GamificationManager
from recurring_manager import RecurringTaskManager
from interactive_manager import InteractiveManager
from personality_manager import personality_manager
from analytics_manager import AnalyticsManager
from sheets_helper import sheets_manager
from gmail_helper import gmail_manager
from ai_intent_recognizer import ai_intent

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize all managers
gpt = GPTHelper()
task_manager = TaskManager()
nlp = NLPHelper()
voice = VoiceHelper()
smart = SmartFeatures(task_manager, gpt)
pomodoro = PomodoroManager()
time_tracker = TimeTracker()
gamification = GamificationManager()
recurring = RecurringTaskManager()
analytics = AnalyticsManager(task_manager, time_tracker, pomodoro, gamification)

# Store user states
user_states = {}

class EnhancedProductivityBot:
    """Enhanced Telegram Productivity Bot with ALL Phase 1 Features"""
    
    def __init__(self):
        self.gpt = gpt
        self.task_manager = task_manager
        self.nlp = nlp
        self.voice = voice
        self.smart = smart
        self.pomodoro = pomodoro
        self.time_tracker = time_tracker
        self.gamification = gamification
        self.recurring = recurring
        self.personality = personality_manager
        self.analytics = analytics
        self.interactive = InteractiveManager()  # New interactive system
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        user_id = user.id
        
        # Get personalized greeting from personality manager
        greeting = self.personality.get_greeting()
        
        # Get gamification profile
        profile = self.gamification.get_profile(user_id)
        
        welcome_message = f"""
{greeting}

🎮 **{profile.split('**')[1].split('**')[0]}**

**🚀 ALL NEW FEATURES:**
🍅 **Pomodoro Timer** - /pomodoro
⏱️ **Time Tracking** - /starttrack
🏆 **XP & Achievements** - /profile
🔁 **Recurring Tasks** - /recurring
📊 **Weekly Reports** - /weekly
🎨 **Change Personality** - /theme

**📋 Core Commands:**
/addtask - Add new task (with AI parsing!)
/mytasks - View all tasks
/stats - Daily statistics
/goal - Break down big goals
/help - Full command list

💪 Let's conquer today! Type /help for more info.
"""
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def add_task_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced /addtask with gamification"""
        user_id = update.effective_user.id
        
        if context.args:
            task_text = ' '.join(context.args)
            
            # NLP parsing
            parsed = self.nlp.parse_task_with_time(task_text)
            
            # Add task
            task = self.task_manager.add_task(
                task_name=parsed['task'],
                user_id=user_id,
                reminder_time=parsed['reminder_time'],
                priority=parsed['priority'],
                recurring=parsed['recurring']
            )
            
            # Sync to Google Sheets
            if sheets_manager.connected:
                sheets_manager.sync_task(task, username=update.effective_user.username or "Unknown")
            
            # Get personality-based response
            task_added_msg = self.personality.get_task_added_message(parsed['task'])
            
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
            emoji = priority_emoji.get(parsed['priority'], '🟡')
            
            response = f"{task_added_msg}\n\n📝 **{parsed['task']}**\n{emoji} Priority: {parsed['priority'].upper()}"
            
            if parsed['reminder_time']:
                # Format the time nicely for display
                from datetime import datetime
                dt = datetime.fromisoformat(parsed['reminder_time'])
                response += f"\n⏰ Reminder: {dt.strftime('%b %d, %I:%M %p')}"
            
            if parsed['recurring']:
                response += f"\n🔄 Recurring: {parsed['recurring']}"
            
            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                "📝 **Add Task - Smart Natural Language!**\n\n"
                "**Examples:**\n"
                "• `/addtask Study for exam tomorrow at 5 PM`\n"
                "• `/addtask Urgent: Complete report today`\n"
                "• `/addtask Call mom every Sunday`\n"
                "• `/addtask Workout in 3 days at 7 AM`\n\n"
                "I'll auto-detect time, priority & recurrence! 🧠",
                parse_mode='Markdown'
            )
    
    async def my_tasks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced /mytasks with better UX"""
        user_id = update.effective_user.id
        tasks = self.task_manager.get_user_tasks(user_id)
        
        if not tasks:
            msg = self.personality.get_motivation()
            await update.message.reply_text(f"No tasks yet! {msg}\n\nUse /addtask to create one. 📝")
            return
        
        pending = [t for t in tasks if t['status'] == 'pending']
        done = [t for t in tasks if t['status'] == 'done']
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        pending.sort(key=lambda x: priority_order.get(x.get('priority', 'medium'), 1))
        
        priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
        
        message = "📋 **Your Tasks:**\n\n"
        
        if pending:
            message += "⏳ **Pending:**\n"
            for task in pending:
                emoji = priority_emoji.get(task.get('priority', 'medium'), '🟡')
                recurring = ' 🔄' if task.get('recurring') else ''
                message += f"{emoji} {task['task']}{recurring}\n"
            message += "\n"
        
        if done:
            message += f"✅ **Completed Today:** {len(done)}\n\n"
        
        # Proactive reminder
        proactive = self.smart.proactive_reminder(user_id)
        if proactive:
            message += f"💡 {proactive['message']}\n\n"
        
        # Add buttons
        if pending:
            keyboard = []
            for task in pending[:5]:
                keyboard.append([
                    InlineKeyboardButton(f"✅ {task['task'][:28]}", callback_data=f"done_{task['id']}"),
                    InlineKeyboardButton("⏰", callback_data=f"reschedule_{task['id']}")
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text(message, parse_mode='Markdown')
    
    async def pomodoro_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🍅 Start Pomodoro session"""
        user_id = update.effective_user.id
        
        if not context.args:
            # Show current session or stats
            current = self.pomodoro.get_current_session(user_id)
            if current:
                await update.message.reply_text(current['message'], parse_mode='Markdown')
            else:
                stats = self.pomodoro.get_stats(user_id)
                msg = f"{stats}\n\n**Start a session:**\n`/pomodoro <task> [minutes]`\n\nExample: `/pomodoro Study math 25`"
                await update.message.reply_text(msg, parse_mode='Markdown')
            return
        
        # Parse arguments
        args = context.args
        task_name = ' '.join(args[:-1]) if len(args) > 1 and args[-1].isdigit() else ' '.join(args)
        duration = int(args[-1]) if len(args) > 1 and args[-1].isdigit() else 25
        
        # Start session
        session, msg = self.pomodoro.start_session(user_id, task_name, duration)
        
        if session:
            # Add XP for starting focus session
            xp_result = self.gamification.add_xp(user_id, 5, "Focus session started")
            msg += f"\n\n{xp_result['message']}"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    
    async def pomodoro_done_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Complete current Pomodoro"""
        user_id = update.effective_user.id
        
        session, msg = self.pomodoro.complete_session(user_id)
        
        if session:
            # Award XP
            xp_result = self.gamification.add_xp(user_id, 20, "Pomodoro completed")
            msg += f"\n\n{xp_result['message']}"
            
            # Check for achievement
            if user_id in self.gamification.user_data:
                total_sessions = self.pomodoro.sessions[str(user_id)]['total_sessions']
                if total_sessions == 20:
                    self.gamification.user_data[str(user_id)]['achievements'].append('pomodoro_master')
                    self.gamification._save_data()
                    msg += "\n\n🏆 Achievement Unlocked: **Pomodoro Master**! 🍅"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    
    async def pomodoro_cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel current Pomodoro"""
        user_id = update.effective_user.id
        
        _, msg = self.pomodoro.cancel_session(user_id)
        await update.message.reply_text(msg, parse_mode='Markdown')
    
    async def starttrack_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """⏱️ Start time tracking"""
        user_id = update.effective_user.id
        
        if not context.args:
            # Show current tracking or help
            active = self.time_tracker.get_active_tracking(user_id)
            if active:
                msg = f"⏱️ **Currently Tracking:**\n\n📝 {active['task_name']}\n⏰ Elapsed: {active['elapsed_minutes']} minutes"
                if active.get('estimated_minutes'):
                    msg += f"\n📊 Estimated: {active['estimated_minutes']} minutes"
                msg += "\n\n✅ Use /stoptrack when done!"
            else:
                msg = "⏱️ **Time Tracking**\n\nStart tracking:\n`/starttrack <task> [estimated_minutes]`\n\nExample: `/starttrack Code feature 60`"
            
            await update.message.reply_text(msg, parse_mode='Markdown')
            return
        
        # Parse arguments
        args = context.args
        task_name = ' '.join(args[:-1]) if len(args) > 1 and args[-1].isdigit() else ' '.join(args)
        estimated = int(args[-1]) if len(args) > 1 and args[-1].isdigit() else None
        
        # Start tracking
        _, msg = self.time_tracker.start_tracking(user_id, 0, task_name, estimated)
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    
    async def stoptrack_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stop time tracking"""
        user_id = update.effective_user.id
        
        notes = ' '.join(context.args) if context.args else None
        result, msg = self.time_tracker.stop_tracking(user_id, notes)
        
        if result:
            # Award XP
            xp_result = self.gamification.add_xp(user_id, 15, "Time tracked")
            msg += f"\n\n{xp_result['message']}"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    
    async def timeinsights_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get time tracking insights"""
        user_id = update.effective_user.id
        
        insights = self.time_tracker.get_insights(user_id)
        category_insights = self.time_tracker.get_category_insights(user_id)
        
        msg = insights
        if category_insights:
            msg += f"\n\n{category_insights}"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🎮 Show gamification profile"""
        user_id = update.effective_user.id
        
        profile = self.gamification.get_profile(user_id)
        
        # Add current personality
        personality_desc = self.personality.get_personality_description()
        profile += f"\n\n🎨 **Personality:** {personality_desc}"
        
        await update.message.reply_text(profile, parse_mode='Markdown')
    
    async def achievements_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show all achievements"""
        user_id = update.effective_user.id
        
        achievements = self.gamification.get_achievements_list(user_id)
        
        await update.message.reply_text(achievements, parse_mode='Markdown')
    
    async def recurring_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🔁 Show recurring tasks"""
        user_id = update.effective_user.id
        
        msg = self.recurring.format_task_list(user_id)
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    
    async def addrecurring_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add a recurring task"""
        user_id = update.effective_user.id
        
        if not context.args:
            await update.message.reply_text(
                "🔁 **Add Recurring Task**\n\n"
                "**Format:**\n"
                "`/addrecurring <task> <frequency>`\n\n"
                "**Frequencies:**\n"
                "• `daily` - Every day\n"
                "• `weekly` - Every week\n"
                "• `monthly` - Every month\n\n"
                "**Examples:**\n"
                "• `/addrecurring Workout daily`\n"
                "• `/addrecurring Team meeting weekly`\n"
                "• `/addrecurring Pay rent monthly`",
                parse_mode='Markdown'
            )
            return
        
        # Parse arguments
        args = context.args
        if args[-1].lower() in ['daily', 'weekly', 'monthly']:
            frequency = args[-1].lower()
            task_name = ' '.join(args[:-1])
        else:
            await update.message.reply_text("❌ Please specify frequency: daily, weekly, or monthly")
            return
        
        # Add recurring task
        _, msg = self.recurring.add_recurring_task(user_id, task_name, frequency)
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    
    async def delrecurring_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Delete a recurring task"""
        user_id = update.effective_user.id
        
        if not context.args or not context.args[0].isdigit():
            await update.message.reply_text("Usage: `/delrecurring <id>`\n\nUse /recurring to see IDs", parse_mode='Markdown')
            return
        
        task_id = int(context.args[0])
        success, msg = self.recurring.delete_recurring_task(user_id, task_id)
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    
    async def weekly_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """📊 Generate weekly report"""
        user_id = update.effective_user.id
        
        await update.message.reply_text("📊 Generating your weekly report... ⏳")
        
        report = self.analytics.generate_weekly_report(user_id)
        
        # Add productivity score
        score = self.analytics.get_productivity_score(user_id)
        report += f"\n\n**🎯 Productivity Score:** {score}/100"
        
        if score >= 80:
            report += " 🏆 Elite!"
        elif score >= 60:
            report += " 💪 Strong!"
        elif score >= 40:
            report += " 📈 Growing!"
        else:
            report += " 💡 Room to improve!"
        
        # Add motivation
        motivation = self.personality.get_motivation()
        report += f"\n\n{motivation}"
        
        await update.message.reply_text(report, parse_mode='Markdown')
    
    async def timeofday_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """⏰ Analyze best productive hours"""
        user_id = update.effective_user.id
        
        analysis = self.analytics.get_time_of_day_analysis(user_id)
        
        await update.message.reply_text(analysis, parse_mode='Markdown')
    
    async def theme_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🎨 Change bot personality"""
        if not context.args:
            personalities = self.personality.get_available_personalities()
            current = self.personality.current_personality
            
            msg = f"🎨 **Bot Personality**\n\nCurrent: **{current.title()}**\n\n**Available:**\n"
            
            descriptions = {
                'professional': '💼 Professional - Clear, focused',
                'coach': '💪 Coach - HIGH ENERGY, motivational',
                'funny': '😄 Funny - Casual with humor',
                'zen': '🧘 Zen - Calm, mindful'
            }
            
            for p in personalities:
                msg += f"• `{p}` - {descriptions.get(p, p.title())}\n"
            
            msg += "\n**Change:** `/theme <personality>`"
            
            await update.message.reply_text(msg, parse_mode='Markdown')
            return
        
        new_personality = context.args[0].lower()
        
        if self.personality.set_personality(new_personality):
            greeting = self.personality.get_greeting()
            await update.message.reply_text(f"🎨 Personality changed to **{new_personality.title()}**!\n\n{greeting}", parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Invalid personality! Use /theme to see options.")
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced /stats"""
        user_id = update.effective_user.id
        stats = self.task_manager.get_daily_stats(user_id)
        
        summary = self.gpt.daily_summary(stats['done'], stats['pending'], stats['total'])
        
        # Get gamification info
        gam_data = self.gamification.user_data.get(str(user_id), {})
        streak = gam_data.get('current_streak', 0)
        
        message = f"""
📊 **Today's Statistics:**

Total: {stats['total']} | ✅ Done: {stats['done']} | ⏳ Pending: {stats['pending']}
🔥 Streak: {streak} days

{summary}

**Quick Actions:**
• /weekly - Weekly report
• /profile - Your level & XP
• /achievements - View achievements
"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced /help"""
        help_text = f"""
🤖 **SycproBot - Complete Guide**

**🎨 Current Personality:** {self.personality.current_personality.title()}

**📋 Task Management:**
/addtask <task> - Add task with AI parsing
/mytasks - View all tasks
/today - Today's tasks + briefing 🌅
/briefing - Morning briefing
/goal <goal> - Break down big goals

**🍅 Focus & Time:**
/pomodoro <task> [min] - Start focus session
/pomodoro_done - Complete session
/starttrack <task> [est] - Track time
/stoptrack - Stop tracking
/timeinsights - Time analytics

**🎮 Gamification:**
/profile - Your level & XP
/achievements - View achievements
/weekly - Weekly productivity report

**🔁 Recurring Tasks:**
/recurring - View recurring tasks
/addrecurring <task> <freq> - Add recurring
/delrecurring <id> - Remove recurring

**🎨 Customization:**
/theme [personality] - Change bot style
/timeofday - Best productive hours

**📊 Analytics:**
/stats - Today's stats
/moodreport - Weekly mood analysis

**🌐 Cloud Sync:**
/sync - Sync tasks to Google Sheets
/email - Send email digest

**🚀 Smart Features:**
• Interactive reminders with Yes/No/Reschedule
• Auto morning briefing (8 AM daily)
• Procrastination detection
• Quick snooze options
• Context-aware AI responses

**Examples:**
• `/addtask Urgent: Finish report today`
• `/today` - See what's due today
• `/pomodoro Study math 25`
• `/addrecurring Workout daily`
• Just say: "Remind me to call mom tomorrow at 3 PM"

Need help? Just ask me anything! 💬
"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def goal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Break down big goals"""
        user_id = update.effective_user.id
        
        if context.args:
            goal_text = ' '.join(context.args)
            
            await update.message.reply_text("🧠 Breaking down your goal... ⏳")
            
            breakdown = self.smart.decompose_big_goal(goal_text)
            
            await update.message.reply_text(breakdown, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                "🎯 **Goal Decomposition**\n\n"
                "I'll break your big goal into weekly milestones!\n\n"
                "**Usage:** `/goal <your big goal>`\n\n"
                "**Example:** `/goal Learn Python programming`",
                parse_mode='Markdown'
            )
    
    async def moodreport_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Weekly mood report"""
        user_id = update.effective_user.id
        
        await update.message.reply_text("😊 Analyzing your mood patterns... ⏳")
        
        report = self.smart.generate_weekly_mood_report(user_id)
        
        await update.message.reply_text(report, parse_mode='Markdown')
    
    async def today_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """📅 Show today's tasks and daily briefing"""
        user_id = update.effective_user.id
        
        # Get today's tasks
        from datetime import datetime
        today = datetime.now().date()
        all_tasks = self.task_manager.get_all_tasks(user_id)
        
        tasks_today = []
        for task in all_tasks:
            if task.get('done'):
                continue
            
            # Check if task is due today
            if task.get('reminder_time'):
                try:
                    task_time = datetime.fromisoformat(task['reminder_time'].replace('Z', '+00:00'))
                    if task_time.date() == today:
                        tasks_today.append(task)
                except:
                    pass
        
        # Get user profile
        user_profile = self.gamification.get_user_data(user_id)
        
        # Generate morning briefing
        briefing = self.interactive.get_morning_briefing(
            tasks_today,
            user_profile,
            self.personality
        )
        
        # Add interactive buttons
        reply_markup = self.interactive.get_daily_summary_buttons()
        
        await update.message.reply_text(
            briefing,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def briefing_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🌅 Morning briefing - alias for /today"""
        await self.today_command(update, context)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        if data.startswith('done_'):
            task_id = int(data.split('_')[1])
            task = self.task_manager.get_task_by_id(task_id, user_id)
            
            if task:
                # Mark task as done
                self.task_manager.mark_done(task_id, user_id)
                
                # Sync to Google Sheets
                if sheets_manager.connected:
                    updated_task = self.task_manager.get_task_by_id(task_id, user_id)
                    if updated_task:
                        sheets_manager.sync_task(updated_task, username=query.from_user.username or "Unknown")
                
                # Gamification rewards
                completion_result = self.gamification.task_completed(user_id, task)
                
                # Build response
                task_done_msg = self.personality.get_task_completed_message(task['task'])
                response = f"{task_done_msg}\n\n"
                
                # XP rewards
                total_xp = sum([xp for xp, _ in completion_result['xp_rewards']])
                response += f"💎 **+{total_xp} XP** earned!\n"
                
                # Achievements
                if completion_result['achievements']:
                    response += "\n🏆 **Achievements Unlocked:**\n"
                    for ach_id in completion_result['achievements']:
                        ach = self.gamification.achievements[ach_id]
                        response += f"• {ach['name']} (+{ach['xp']} XP)\n"
                
                # Streak
                if completion_result['streak'] >= 3:
                    streak_msg = self.personality.get_streak_message(completion_result['streak'])
                    response += f"\n{streak_msg}"
                
                await query.edit_message_text(response, parse_mode='Markdown')
        
        elif data.startswith('reschedule_'):
            task_id = int(data.split('_')[1])
            task = self.task_manager.get_task_by_id(task_id, user_id)
            
            if task:
                # Show quick reschedule options
                reply_markup = self.interactive.get_reschedule_options(task_id, task['task'])
                await query.edit_message_text(
                    f"⏰ **Reschedule Task**\n\n"
                    f"📝 {task['task']}\n\n"
                    f"Choose a new time:",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
        
        elif data.startswith('snooze_'):
            # Handle snooze: snooze_taskid_minutes
            parts = data.split('_')
            task_id = int(parts[1])
            snooze_minutes = int(parts[2])
            
            task = self.task_manager.get_task_by_id(task_id, user_id)
            
            if task:
                # Calculate new reminder time
                from datetime import datetime, timedelta
                new_time = (datetime.now() + timedelta(minutes=snooze_minutes)).isoformat()
                
                # Update task with new time and clear reminder_sent flag
                self.task_manager.reschedule_task(task_id, user_id, new_time)
                
                # Clear the reminder_sent flag so it can be sent again
                for t in self.task_manager.tasks:
                    if t['id'] == task_id:
                        t['reminder_sent'] = False
                        break
                self.task_manager.save_tasks()
                
                await query.edit_message_text(
                    f"⏰ **Snoozed for {snooze_minutes} minutes**\n\n"
                    f"📝 Task: {task['task']}\n"
                    f"⏰ Next reminder: {new_time[:16].replace('T', ' ')}\n\n"
                    f"💤 I'll remind you again soon!",
                    parse_mode='Markdown'
                )
        
        elif data.startswith('tomorrow_'):
            # Reschedule to tomorrow same time
            task_id = int(data.split('_')[1])
            task = self.task_manager.get_task_by_id(task_id, user_id)
            
            if task:
                from datetime import datetime, timedelta
                # Tomorrow at 9 AM
                tomorrow = (datetime.now() + timedelta(days=1)).replace(hour=9, minute=0, second=0)
                new_time = tomorrow.isoformat()
                
                self.task_manager.reschedule_task(task_id, user_id, new_time)
                
                await query.edit_message_text(
                    f"📅 **Rescheduled to Tomorrow**\n\n"
                    f"📝 Task: {task['task']}\n"
                    f"⏰ New time: Tomorrow 9:00 AM\n\n"
                    f"✅ See you tomorrow!",
                    parse_mode='Markdown'
                )
        
        elif data.startswith('cancel_'):
            # Cancel/delete task
            task_id = int(data.split('_')[1])
            task = self.task_manager.get_task_by_id(task_id, user_id)
            
            if task:
                task_name = task['task']
                self.task_manager.mark_done(task_id, user_id)  # Mark as done to remove
                
                await query.edit_message_text(
                    f"❌ **Task Cancelled**\n\n"
                    f"📝 {task_name}\n\n"
                    f"Task removed from your list.",
                    parse_mode='Markdown'
                )
        
        elif data.startswith('quick_reschedule_'):
            # Handle quick reschedule options
            parts = data.split('_')
            task_id = int(parts[2])
            option = '_'.join(parts[3:])  # e.g., "30m", "1h", "tomorrow_morning"
            
            task = self.task_manager.get_task_by_id(task_id, user_id)
            
            if task:
                # Calculate new time using interactive manager
                new_datetime = self.interactive.calculate_reschedule_time(option)
                new_time = new_datetime.isoformat()
                
                # Track reschedule pattern
                count, should_suggest = self.interactive.track_reschedule(
                    user_id, task_id, task['task']
                )
                
                # Update task
                self.task_manager.reschedule_task(task_id, user_id, new_time)
                
                # Clear reminder_sent flag
                for t in self.task_manager.tasks:
                    if t['id'] == task_id:
                        t['reminder_sent'] = False
                        break
                self.task_manager.save_tasks()
                
                response = f"✅ **Rescheduled!**\n\n"
                response += f"📝 Task: {task['task']}\n"
                response += f"⏰ New time: {new_datetime.strftime('%b %d, %I:%M %p')}\n\n"
                
                # Check for procrastination
                if should_suggest:
                    procrastination_msg = self.interactive.get_procrastination_message(
                        task['task'], count
                    )
                    if procrastination_msg:
                        response += f"\n{procrastination_msg}"
                else:
                    response += f"💪 You got this!"
                
                await query.edit_message_text(response, parse_mode='Markdown')
        
        elif data.startswith('custom_reschedule_'):
            # Start custom reschedule flow
            task_id = int(data.split('_')[2])
            task = self.task_manager.get_task_by_id(task_id, user_id)
            
            if task:
                user_states[user_id] = {'state': 'awaiting_reschedule', 'task_id': task_id}
                await query.edit_message_text(
                    f"📝 **Custom Reschedule**\n\n"
                    f"Task: {task['task']}\n\n"
                    f"Type when you want to be reminded:\n"
                    f"Examples:\n"
                    f"• \"tomorrow at 3 PM\"\n"
                    f"• \"in 2 hours\"\n"
                    f"• \"Friday at 10 AM\"\n"
                    f"• \"next week\"",
                    parse_mode='Markdown'
                )
        
        elif data.startswith('back_to_reminder_'):
            # Go back to reminder buttons
            task_id = int(data.split('_')[3])
            task = self.task_manager.get_task_by_id(task_id, user_id)
            
            if task:
                reminder_text = f"⏰ **REMINDER**\n\n"
                reminder_text += f"📝 **Task:** {task['task']}\n"
                reminder_text += f"⭐ **Priority:** {task.get('priority', 'medium').upper()}\n\n"
                reminder_text += f"💡 *What would you like to do?*"
                
                reply_markup = self.interactive.get_reminder_buttons(
                    task['id'], 
                    task.get('priority', 'medium')
                )
                
                await query.edit_message_text(
                    reminder_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
        
        elif data.startswith('skip_'):
            await query.edit_message_text("⏭️ Skipped!")
    
    async def voice_message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages"""
        user_id = update.effective_user.id
        
        await update.message.reply_text("🎤 Transcribing your voice... ⏳")
        
        # Download voice file
        voice_file = await update.message.voice.get_file()
        file_path = f"voice_{user_id}_{datetime.now().timestamp()}.ogg"
        await voice_file.download_to_drive(file_path)
        
        # Transcribe
        transcription = self.voice.transcribe_voice(file_path)
        
        if transcription:
            # Parse as task
            parsed = self.nlp.parse_task_with_time(transcription)
            
            # Add task
            task = self.task_manager.add_task(
                task_name=parsed['task'],
                user_id=user_id,
                reminder_time=parsed['reminder_time'],
                priority=parsed['priority']
            )
            
            response = f"🎤 **Transcribed:** \"{transcription}\"\n\n"
            response += f"✅ Task added: **{parsed['task']}**"
            
            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Couldn't transcribe voice. Please add OPENAI_API_KEY in .env file for voice support.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        🤖 AI-POWERED MESSAGE HANDLER
        Understands natural language - NO COMMANDS NEEDED!
        Just talk naturally and AI will understand your intent.
        """
        user_id = update.effective_user.id
        message_text = update.message.text
        username = update.effective_user.username or update.effective_user.first_name
        
        # Sentiment analysis
        sentiment = self.nlp.analyze_sentiment(message_text)
        self.smart.track_mood(user_id, sentiment)
        
        # Check user state (for ongoing conversations like rescheduling)
        if user_id in user_states:
            state = user_states[user_id]
            
            if state['state'] == 'awaiting_reschedule':
                task_id = state['task_id']
                task = self.task_manager.get_task_by_id(task_id, user_id)
                
                time_info = self.nlp.extract_datetime(message_text)
                new_time = time_info['time'] if time_info else message_text
                
                self.task_manager.reschedule_task(task_id, user_id, new_time)
                
                confirmation = self.gpt.reschedule_confirmation(task['task'], message_text)
                confirmation = self.smart.adjust_tone_for_mood(user_id, confirmation)
                
                await update.message.reply_text(f"✅ {confirmation}")
                
                del user_states[user_id]
                return
        
        # 🚀 AI INTENT RECOGNITION - Understand what user wants!
        # Removed the "Understanding..." message to make it faster
        
        try:
            intent_result = ai_intent.analyze_intent(message_text)
            intent = intent_result['intent']
            params = intent_result['parameters']
            confidence = intent_result['confidence']
            
            logger.info(f"🤖 AI Intent: {intent} (confidence: {confidence}) | Params: {params}")
        except Exception as e:
            logger.error(f"❌ AI Intent failed: {e}")
            # Fallback to general chat
            response = f"⚠️ I'm having trouble understanding right now. Try commands like:\n/addtask, /mytasks, /stats"
            await update.message.reply_text(response)
            return
        
        # Execute action based on intent
        if intent == 'set_reminder':
            # "set a reminder for 1 min"
            if 'time_amount' in params and 'time_unit' in params:
                reminder_time = ai_intent.calculate_reminder_time(
                    params['time_amount'], 
                    params['time_unit']
                )
                
                task_name = params.get('task_name', f"Reminder in {params['time_amount']} {params['time_unit']}")
                
                task = self.task_manager.add_task(
                    task_name=task_name,
                    user_id=user_id,
                    reminder_time=reminder_time,
                    priority=params.get('priority', 'medium')
                )
                
                # Sync to Google Sheets
                sheets_manager.sync_task(task, username)
                
                response = f"⏰ **Reminder Set!**\n\n"
                response += f"📝 Task: {task_name}\n"
                response += f"🕐 Will remind in: {params['time_amount']} {params['time_unit']}\n"
                response += f"📅 Time: {reminder_time}"
                
                await update.message.reply_text(response, parse_mode='Markdown')
            else:
                await update.message.reply_text("⚠️ Please specify when (e.g., 'set a reminder for 1 min')")
        
        elif intent == 'send_email':
            # "send hi in mail"
            email_content = params.get('email_content', 'Hello!')
            email_subject = params.get('email_subject', 'Message from SycproBot')
            
            # Send email using Gmail manager
            success = gmail_manager.send_email(
                to_email=config.GMAIL_ADDRESS,
                subject=email_subject,
                html_content=f"""
                <html>
                    <body style="font-family: Arial, sans-serif;">
                        <h2>📧 Message from Telegram Bot</h2>
                        <p>{email_content}</p>
                        <hr>
                        <p style="color: #666; font-size: 12px;">
                            Sent via SycproBot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                        </p>
                    </body>
                </html>
                """
            )
            
            if success:
                response = f"📧 **Email Sent!**\n\n"
                response += f"📬 To: {config.GMAIL_ADDRESS}\n"
                response += f"📝 Subject: {email_subject}\n"
                response += f"💌 Content: {email_content}"
            else:
                response = "⚠️ Email prepared! Add GMAIL_APP_PASSWORD to .env to actually send.\n\n"
                response += f"Preview:\n📧 To: {config.GMAIL_ADDRESS}\n📝 {email_content}"
            
            await update.message.reply_text(response, parse_mode='Markdown')
        
        elif intent == 'add_task':
            # "remind me to call mom" or "add task buy groceries"
            task_name = params.get('task_name', message_text)
            
            # Check if AI already extracted reminder_time, otherwise parse from task_name
            if 'reminder_time' in params and params['reminder_time']:
                # Parse the time from AI params (could be "10:53am", "tomorrow", etc.)
                time_info = self.nlp.extract_datetime(params['reminder_time'])
                reminder_time = time_info['datetime'].isoformat() if time_info else None
            else:
                # Fallback: Parse time from task_name
                time_info = self.nlp.extract_datetime(task_name)
                reminder_time = time_info['datetime'].isoformat() if time_info else None
            
            task = self.task_manager.add_task(
                task_name=task_name,
                user_id=user_id,
                reminder_time=reminder_time,
                priority=params.get('priority', 'medium')
            )
            
            # Sync to Google Sheets
            sheets_manager.sync_task(task, username)
            
            # Gamification
            gamification.add_xp(user_id, 10)
            
            response = f"✅ **Task Added!**\n\n"
            response += f"📝 {task_name}\n"
            if reminder_time:
                # Format the time nicely for display
                from datetime import datetime
                dt = datetime.fromisoformat(reminder_time)
                response += f"⏰ Reminder: {dt.strftime('%b %d, %I:%M %p')}\n"
            response += f"⭐ Priority: {task['priority'].upper()}\n"
            
            # Level up notification
            profile = gamification.get_user_data(user_id)
            response += f"\n🎮 +10 XP | Level {profile['level']} ({profile['xp']}/{profile['next_level_xp']} XP)"
            
            await update.message.reply_text(response, parse_mode='Markdown')
        
        elif intent == 'list_tasks':
            # "show my tasks" or "what do I have to do"
            tasks = self.task_manager.get_all_tasks(user_id)
            
            if not tasks:
                await update.message.reply_text("📭 No tasks yet! Add one by saying something like:\n'remind me to call mom tomorrow'")
                return
            
            # Sort by priority
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            tasks.sort(key=lambda x: (x.get('completed', False), priority_order.get(x.get('priority', 'medium'), 1)))
            
            response = "📋 **Your Tasks:**\n\n"
            for i, task in enumerate(tasks[:10], 1):
                status = "✅" if task.get('completed') else "⏳"
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.get('priority', 'medium'), "⚪")
                
                response += f"{status} {priority_emoji} **{i}.** {task['task']}\n"
                if task.get('reminder_time'):
                    response += f"   ⏰ {task['reminder_time']}\n"
            
            await update.message.reply_text(response, parse_mode='Markdown')
        
        elif intent == 'complete_task':
            # "mark task 1 as done" or "completed buy groceries"
            task_id = params.get('task_id')
            
            if task_id:
                task = self.task_manager.get_task_by_id(task_id, user_id)
                if task:
                    self.task_manager.mark_task_completed(task_id, user_id)
                    
                    # Sync to Google Sheets
                    sheets_manager.sync_task(task, username)
                    
                    # Gamification
                    xp = gamification.complete_task(user_id, task)
                    
                    response = f"✅ **Task Completed!**\n\n{task['task']}\n\n🎮 +{xp} XP!"
                    await update.message.reply_text(response, parse_mode='Markdown')
                else:
                    await update.message.reply_text("❌ Task not found. Say 'show my tasks' to see all.")
            else:
                await update.message.reply_text("Please specify which task (e.g., 'mark task 1 as done')")
        
        elif intent == 'get_stats':
            # "show my stats" or "how am I doing"
            stats = gamification.get_user_stats(user_id)
            
            response = f"📊 **Your Stats:**\n\n"
            response += f"🎮 Level: {stats['level']}\n"
            response += f"⭐ XP: {stats['xp']}/{stats['next_level_xp']}\n"
            response += f"✅ Completed: {stats['tasks_completed']}\n"
            response += f"🔥 Streak: {stats['streak']} days\n\n"
            
            if stats['achievements']:
                response += f"🏆 **Achievements:**\n"
                for achievement in stats['achievements'][:5]:
                    response += f"  • {achievement}\n"
            
            await update.message.reply_text(response, parse_mode='Markdown')
        
        elif intent == 'general_chat':
            # General conversation detected by AI
            response = self.gpt.handle_user_message(message_text)
            response = self.smart.adjust_tone_for_mood(user_id, response)
            
            await update.message.reply_text(response)
        
        else:
            # Fallback for unknown intents - use GPT
            response = self.gpt.handle_user_message(message_text)
            response = self.smart.adjust_tone_for_mood(user_id, response)
            
            await update.message.reply_text(response)
    
    async def sync_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Sync all tasks to Google Sheets"""
        if not sheets_manager.connected:
            await update.message.reply_text(
                "⚠️ **Google Sheets not configured!**\n\n"
                "See `GOOGLE_SETUP_GUIDE.md` for setup instructions.\n"
                "Your tasks are safely stored locally in JSON.",
                parse_mode='Markdown'
            )
            return
        
        await update.message.reply_text("🔄 Syncing all tasks to Google Sheets...")
        
        if sheets_manager.sync_all_tasks():
            stats = sheets_manager.get_task_stats()
            await update.message.reply_text(
                f"✅ **Sync Complete!**\n\n"
                f"📊 Total: {stats['total']}\n"
                f"✅ Done: {stats['completed']}\n"
                f"⏳ Pending: {stats['pending']}\n"
                f"📈 Completion: {stats['completion_rate']}%\n\n"
                f"[Open Sheet](https://docs.google.com/spreadsheets/d/{config.SPREADSHEET_ID}/edit)",
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
        else:
            await update.message.reply_text("❌ Sync failed. Check logs for details.")
    
    async def email_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send email digest"""
        user_id = update.effective_user.id
        
        if not gmail_manager.enabled:
            await update.message.reply_text(
                "📧 **Email not configured!**\n\n"
                "Set GMAIL_ADDRESS in .env to enable email notifications.",
                parse_mode='Markdown'
            )
            return
        
        await update.message.reply_text("📧 Preparing your email digest...")
        
        # Get user tasks
        user_tasks = self.task_manager.get_user_tasks(user_id)
        pending = [t for t in user_tasks if t['status'] != 'done']
        completed = [t for t in user_tasks if t['status'] == 'done']
        high_priority = [t for t in pending if t.get('priority') == 'high']
        
        # Get gamification data
        gam_data = self.gamification.user_data.get(str(user_id), {})
        
        # Prepare digest data
        digest_data = {
            'total': len(user_tasks),
            'completed': len(completed),
            'pending': len(pending),
            'high_priority_tasks': high_priority[:5],
            'motivation': self.personality.get_daily_motivation(),
        }
        
        email = config.GMAIL_ADDRESS
        if gmail_manager.send_daily_digest(email, digest_data):
            await update.message.reply_text(
                f"✅ **Email digest prepared!**\n\n"
                f"📧 Ready to send to: {email}\n\n"
                f"*Note: Configure Gmail App Password in .env to actually send emails.*\n"
                f"See GOOGLE_SETUP_GUIDE.md for instructions.",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Failed to prepare email digest.")

def main():
    """Start the enhanced bot"""
    try:
        validate_config()
        
        # Create application
        application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        
        # Initialize bot
        bot = EnhancedProductivityBot()
        
        # Register ALL handlers
        application.add_handler(CommandHandler("start", bot.start_command))
        application.add_handler(CommandHandler("addtask", bot.add_task_command))
        application.add_handler(CommandHandler("mytasks", bot.my_tasks_command))
        application.add_handler(CommandHandler("stats", bot.stats_command))
        application.add_handler(CommandHandler("help", bot.help_command))
        
        # Pomodoro handlers
        application.add_handler(CommandHandler("pomodoro", bot.pomodoro_command))
        application.add_handler(CommandHandler("pomodoro_done", bot.pomodoro_done_command))
        application.add_handler(CommandHandler("pomodoro_cancel", bot.pomodoro_cancel_command))
        
        # Time tracking handlers
        application.add_handler(CommandHandler("starttrack", bot.starttrack_command))
        application.add_handler(CommandHandler("stoptrack", bot.stoptrack_command))
        application.add_handler(CommandHandler("timeinsights", bot.timeinsights_command))
        
        # Gamification handlers
        application.add_handler(CommandHandler("profile", bot.profile_command))
        application.add_handler(CommandHandler("achievements", bot.achievements_command))
        
        # Recurring tasks handlers
        application.add_handler(CommandHandler("recurring", bot.recurring_command))
        application.add_handler(CommandHandler("addrecurring", bot.addrecurring_command))
        application.add_handler(CommandHandler("delrecurring", bot.delrecurring_command))
        
        # Analytics handlers
        application.add_handler(CommandHandler("weekly", bot.weekly_command))
        application.add_handler(CommandHandler("timeofday", bot.timeofday_command))
        
        # Theme/Personality handler
        application.add_handler(CommandHandler("theme", bot.theme_command))
        
        # Advanced features
        application.add_handler(CommandHandler("goal", bot.goal_command))
        application.add_handler(CommandHandler("moodreport", bot.moodreport_command))
        
        # Interactive features - Morning briefing & Today's tasks
        application.add_handler(CommandHandler("today", bot.today_command))
        application.add_handler(CommandHandler("briefing", bot.briefing_command))
        
        # Google Sheets & Gmail integration
        application.add_handler(CommandHandler("sync", bot.sync_command))
        application.add_handler(CommandHandler("email", bot.email_command))
        
        # Message handlers
        application.add_handler(CallbackQueryHandler(bot.button_callback))
        application.add_handler(MessageHandler(filters.VOICE, bot.voice_message_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
        
        # Setup post-init callback for startup notification
        async def post_init(app):
            """Send startup notification to recent users"""
            try:
                me = await app.bot.get_me()
                updates = await app.bot.get_updates(limit=10, offset=-1)
                
                chat_ids = set()
                for upd in updates:
                    if upd.message:
                        chat_ids.add(upd.message.chat.id)
                    elif upd.effective_chat:
                        chat_ids.add(upd.effective_chat.id)
                
                startup_msg = f"""
🎉 **SYCPROBOT IS LIVE!** 🎉

I'm back online and ready to dominate! 🤖💪

✅ **Status:** All systems GO!
🎨 **Mode:** Coach personality ACTIVATED
⚡ **Power:** 20+ features ready

**🚀 Quick Commands:**
• `/start` - Welcome message
• `/help` - Full command list  
• `/addtask Study for exam tomorrow 3 PM`

**💡 What's New:**
🧠 Smart AI parsing
🎤 Voice messages
📊 Analytics & insights
🎮 XP, levels & achievements
🍅 Pomodoro timer
🔄 Recurring tasks
🔥 Streak tracking

Message me anything - I understand natural language!

Let's CRUSH IT! 💪🔥
"""
                
                for chat_id in chat_ids:
                    try:
                        await app.bot.send_message(
                            chat_id=chat_id,
                            text=startup_msg,
                            parse_mode='Markdown'
                        )
                        logger.info(f"✅ Startup notification sent to {chat_id}")
                    except Exception as e:
                        logger.warning(f"Could not send to {chat_id}: {e}")
                
                if not chat_ids:
                    logger.info(f"📱 Bot ready! Open: https://t.me/{me.username}")
                    
            except Exception as e:
                logger.error(f"Startup notification error: {e}")
        
        application.post_init = post_init
        
        # Store bot in application data for background reminders
        application.bot_data['bot'] = bot
        
        # Set up JobQueue for reminder checking (proper async approach)
        async def check_reminders(context: ContextTypes.DEFAULT_TYPE):
            """Check for due reminders and send them"""
            try:
                due_tasks = task_manager.get_due_reminders()
                
                if due_tasks:
                    logger.info(f"⏰ Found {len(due_tasks)} due reminders to send")
                
                for task in due_tasks:
                    # Skip if reminder already sent
                    if task.get('reminder_sent', False):
                        logger.info(f"⏭️ Skipping task {task['id']} - reminder already sent")
                        continue
                        
                    try:
                        reminder_text = f"⏰ **REMINDER**\n\n"
                        reminder_text += f"📝 **Task:** {task['task']}\n"
                        reminder_text += f"📅 **Due:** {task['reminder_time']}\n"
                        reminder_text += f"⭐ **Priority:** {task.get('priority', 'medium').upper()}\n\n"
                        reminder_text += f"💡 *What would you like to do?*"
                        
                        # Use new interactive buttons
                        reply_markup = bot.interactive.get_reminder_buttons(
                            task['id'], 
                            task.get('priority', 'medium')
                        )
                        
                        # Send reminder message using proper async context
                        await context.bot.send_message(
                            chat_id=task['user_id'],
                            text=reminder_text,
                            reply_markup=reply_markup,
                            parse_mode='Markdown'
                        )
                        
                        # Mark reminder as sent
                        task_manager.mark_reminder_sent(task['id'])
                        logger.info(f"⏰ Sent reminder for task: {task['task']} to user {task['user_id']}")
                        
                    except Exception as e:
                        logger.error(f"Error sending reminder for task {task['id']}: {e}")
            
            except Exception as e:
                logger.error(f"Error in reminder checker: {e}")
        
        # Schedule reminder checking every 30 seconds using JobQueue
        job_queue = application.job_queue
        job_queue.run_repeating(check_reminders, interval=30, first=10)
        logger.info("⏰ Background reminder system started using JobQueue!")
        
        # Schedule daily morning briefing at 8:00 AM
        async def send_morning_briefing(context: ContextTypes.DEFAULT_TYPE):
            """Send automated morning briefing to all users"""
            try:
                from datetime import datetime
                # Get all unique user IDs from tasks
                all_tasks = task_manager.tasks
                user_ids = set(task.get('user_id') for task in all_tasks if task.get('user_id'))
                
                for user_id in user_ids:
                    try:
                        # Get today's tasks for this user
                        today = datetime.now().date()
                        user_tasks = [t for t in all_tasks if t.get('user_id') == user_id and not t.get('done')]
                        
                        tasks_today = []
                        for task in user_tasks:
                            if task.get('reminder_time'):
                                try:
                                    task_time = datetime.fromisoformat(task['reminder_time'].replace('Z', '+00:00'))
                                    if task_time.date() == today:
                                        tasks_today.append(task)
                                except:
                                    pass
                        
                        # Get user profile
                        user_profile = gamification.get_user_data(user_id)
                        
                        # Generate briefing
                        briefing = bot.interactive.get_morning_briefing(
                            tasks_today,
                            user_profile,
                            personality_manager
                        )
                        
                        # Add buttons
                        reply_markup = bot.interactive.get_daily_summary_buttons()
                        
                        # Send briefing
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=briefing,
                            reply_markup=reply_markup,
                            parse_mode='Markdown'
                        )
                        
                        logger.info(f"🌅 Sent morning briefing to user {user_id}")
                        
                    except Exception as e:
                        logger.error(f"Error sending morning briefing to user {user_id}: {e}")
                
            except Exception as e:
                logger.error(f"Error in morning briefing job: {e}")
        
        # Schedule daily briefing at 8:00 AM
        from datetime import time
        job_queue.run_daily(send_morning_briefing, time=time(hour=8, minute=0, second=0))
        logger.info("🌅 Morning briefing scheduled for 8:00 AM daily!")
        
        # Start bot
        logger.info("🚀 Enhanced SycproBot starting with ALL Phase 1 features!")
        logger.info(f"🎨 Personality: {personality_manager.current_personality.title()}")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == '__main__':
    main()
