"""
Interactive Manager - Advanced Task Interaction System
Handles smart buttons, reschedule logic, and user interaction flows
"""
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging

logger = logging.getLogger(__name__)

class InteractiveManager:
    def __init__(self):
        self.reschedule_patterns = {}  # Track user reschedule habits
        
    def get_reminder_buttons(self, task_id, task_priority='medium'):
        """
        Generate smart reminder buttons based on task priority
        Returns InlineKeyboardMarkup with context-aware options
        """
        # Base buttons - always available
        buttons = [
            [
                InlineKeyboardButton("✅ Done", callback_data=f"done_{task_id}"),
                InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{task_id}")
            ]
        ]
        
        # Quick snooze options - based on priority
        if task_priority == 'high':
            snooze_row = [
                InlineKeyboardButton("⏰ 15min", callback_data=f"snooze_{task_id}_15"),
                InlineKeyboardButton("⏰ 30min", callback_data=f"snooze_{task_id}_30")
            ]
        else:
            snooze_row = [
                InlineKeyboardButton("⏰ 1hr", callback_data=f"snooze_{task_id}_60"),
                InlineKeyboardButton("⏰ 3hrs", callback_data=f"snooze_{task_id}_180")
            ]
        
        buttons.append(snooze_row)
        
        # Reschedule options
        buttons.append([
            InlineKeyboardButton("📅 Tomorrow", callback_data=f"tomorrow_{task_id}"),
            InlineKeyboardButton("🔄 Custom", callback_data=f"reschedule_{task_id}")
        ])
        
        return InlineKeyboardMarkup(buttons)
    
    def get_reschedule_options(self, task_id, task_name=''):
        """
        Generate smart reschedule time options
        """
        buttons = [
            [
                InlineKeyboardButton("⏰ In 30 min", callback_data=f"quick_reschedule_{task_id}_30m"),
                InlineKeyboardButton("⏰ In 1 hour", callback_data=f"quick_reschedule_{task_id}_1h")
            ],
            [
                InlineKeyboardButton("⏰ In 3 hours", callback_data=f"quick_reschedule_{task_id}_3h"),
                InlineKeyboardButton("🌙 Tonight 8PM", callback_data=f"quick_reschedule_{task_id}_tonight")
            ],
            [
                InlineKeyboardButton("🌅 Tomorrow 9AM", callback_data=f"quick_reschedule_{task_id}_tomorrow_morning"),
                InlineKeyboardButton("☀️ Tomorrow 2PM", callback_data=f"quick_reschedule_{task_id}_tomorrow_afternoon")
            ],
            [
                InlineKeyboardButton("📝 Type Custom Time", callback_data=f"custom_reschedule_{task_id}")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data=f"back_to_reminder_{task_id}")
            ]
        ]
        
        return InlineKeyboardMarkup(buttons)
    
    def calculate_reschedule_time(self, option, base_time=None):
        """
        Calculate new reminder time based on quick option
        Returns datetime object
        """
        if base_time is None:
            base_time = datetime.now()
        
        if option == '30m':
            return base_time + timedelta(minutes=30)
        elif option == '1h':
            return base_time + timedelta(hours=1)
        elif option == '3h':
            return base_time + timedelta(hours=3)
        elif option == 'tonight':
            # Set to 8 PM today
            target = base_time.replace(hour=20, minute=0, second=0, microsecond=0)
            if target < base_time:
                target += timedelta(days=1)
            return target
        elif option == 'tomorrow_morning':
            # Tomorrow 9 AM
            target = (base_time + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
            return target
        elif option == 'tomorrow_afternoon':
            # Tomorrow 2 PM
            target = (base_time + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)
            return target
        else:
            return base_time + timedelta(hours=1)  # Default
    
    def track_reschedule(self, user_id, task_id, task_name):
        """
        Track how many times a task has been rescheduled
        Returns: (reschedule_count, should_suggest_breakdown)
        """
        key = f"{user_id}_{task_id}"
        
        if key not in self.reschedule_patterns:
            self.reschedule_patterns[key] = {
                'count': 0,
                'task_name': task_name,
                'first_reschedule': datetime.now().isoformat()
            }
        
        self.reschedule_patterns[key]['count'] += 1
        count = self.reschedule_patterns[key]['count']
        
        # Suggest breaking down task if rescheduled 5+ times
        should_suggest = count >= 5
        
        return count, should_suggest
    
    def get_procrastination_message(self, task_name, reschedule_count):
        """
        Generate helpful message for procrastinated tasks
        """
        if reschedule_count >= 10:
            return f"""🤔 **Procrastination Alert!**

You've rescheduled "{task_name}" {reschedule_count} times.

💡 **Let's make it easier:**
• Break it into 3-5 smaller steps
• Set a timer for just 5 minutes
• Start with the easiest part
• Reward yourself after completing

Would you like me to help break this task down?
[Yes, Break It Down] [No, Keep As Is]"""
        
        elif reschedule_count >= 5:
            return f"""⚠️ **Task Stalling**

"{task_name}" has been rescheduled {reschedule_count} times.

💪 **Quick Tips:**
• Is this task too big? Break it down!
• Set a 10-minute timer and just start
• Remove distractions first

You got this! 🚀"""
        
        return None
    
    def get_morning_briefing(self, tasks_today, user_profile, personality_manager):
        """
        Generate personalized morning briefing
        
        Args:
            tasks_today: List of tasks due today
            user_profile: User's gamification data (from get_user_data())
            personality_manager: PersonalityManager instance
        """
        now = datetime.now()
        greeting = self._get_time_based_greeting(now.hour)
        
        # Build briefing message
        msg = f"{greeting}\n\n"
        msg += f"📅 **{now.strftime('%A, %B %d, %Y')}**\n\n"
        
        # User stats
        msg += f"🎮 **Your Stats:**\n"
        msg += f"Level {user_profile['level']} • {user_profile['xp']} XP\n"
        msg += f"🔥 {user_profile['current_streak']} day streak\n\n"
        
        # Tasks for today
        if not tasks_today:
            msg += "🎉 **No tasks scheduled today!**\n"
            msg += "Enjoy your free day or add some tasks to stay productive! 💪\n"
        else:
            msg += f"📋 **Today's Tasks ({len(tasks_today)}):**\n\n"
            
            # Group by priority
            high_priority = [t for t in tasks_today if t.get('priority') == 'high']
            medium_priority = [t for t in tasks_today if t.get('priority') == 'medium']
            low_priority = [t for t in tasks_today if t.get('priority') == 'low']
            
            # Show high priority first
            if high_priority:
                msg += "⚡ **High Priority:**\n"
                for task in high_priority:
                    time_str = self._format_task_time(task.get('reminder_time', ''))
                    msg += f"  • {task['task']} {time_str}\n"
                msg += "\n"
            
            # Medium priority
            if medium_priority:
                msg += "📌 **Medium Priority:**\n"
                for task in medium_priority:
                    time_str = self._format_task_time(task.get('reminder_time', ''))
                    msg += f"  • {task['task']} {time_str}\n"
                msg += "\n"
            
            # Low priority
            if low_priority:
                msg += "💡 **Low Priority:**\n"
                for task in low_priority:
                    time_str = self._format_task_time(task.get('reminder_time', ''))
                    msg += f"  • {task['task']} {time_str}\n"
                msg += "\n"
        
        # Motivational message
        motivation = personality_manager.get_daily_motivation()
        msg += f"💪 **Daily Motivation:**\n{motivation}\n\n"
        
        # Quick actions
        msg += "🎯 **Quick Actions:**\n"
        msg += "• /add - Add new task\n"
        msg += "• /today - View today's tasks\n"
        msg += "• /profile - Check your progress\n"
        
        return msg
    
    def _get_time_based_greeting(self, hour):
        """Get greeting based on time of day"""
        if hour < 6:
            return "🌙 **You're up early!**"
        elif hour < 12:
            return "🌅 **Good Morning!**"
        elif hour < 17:
            return "☀️ **Good Afternoon!**"
        elif hour < 21:
            return "🌆 **Good Evening!**"
        else:
            return "🌙 **Good Night!**"
    
    def _format_task_time(self, time_str):
        """Format task time for display"""
        if not time_str:
            return ""
        
        try:
            # Parse the time string
            if isinstance(time_str, str):
                task_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            else:
                task_time = time_str
            
            now = datetime.now()
            
            # If today, show time
            if task_time.date() == now.date():
                return f"⏰ {task_time.strftime('%I:%M %p')}"
            else:
                return f"📅 {task_time.strftime('%b %d, %I:%M %p')}"
        except:
            return ""
    
    def get_daily_summary_buttons(self):
        """Buttons for daily briefing"""
        buttons = [
            [
                InlineKeyboardButton("➕ Add Task", callback_data="add_task_flow"),
                InlineKeyboardButton("📊 Full Stats", callback_data="show_profile")
            ],
            [
                InlineKeyboardButton("🎯 Start Pomodoro", callback_data="start_pomodoro"),
                InlineKeyboardButton("⚙️ Settings", callback_data="show_settings")
            ]
        ]
        return InlineKeyboardMarkup(buttons)
