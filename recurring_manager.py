"""
Recurring Tasks Manager
Handles daily, weekly, monthly recurring tasks with auto-generation
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

class RecurringTaskManager:
    def __init__(self, data_file="recurring_tasks.json"):
        self.data_file = Path(data_file)
        self.recurring_tasks = self._load_tasks()
        
    def _load_tasks(self):
        """Load recurring tasks from file"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_tasks(self):
        """Save recurring tasks to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.recurring_tasks, f, indent=2)
    
    def add_recurring_task(self, user_id, task_name, frequency, time_of_day=None, days_of_week=None):
        """
        Add a recurring task
        
        Args:
            user_id: User ID
            task_name: Name of the task
            frequency: 'daily', 'weekly', 'monthly'
            time_of_day: Optional time (HH:MM format)
            days_of_week: For weekly - list of days (0=Monday, 6=Sunday)
        """
        user_id = str(user_id)
        
        if user_id not in self.recurring_tasks:
            self.recurring_tasks[user_id] = []
        
        recurring_task = {
            'id': len(self.recurring_tasks[user_id]) + 1,
            'task_name': task_name,
            'frequency': frequency,
            'time_of_day': time_of_day,
            'days_of_week': days_of_week or [],
            'created_at': datetime.now().isoformat(),
            'last_generated': None,
            'active': True
        }
        
        self.recurring_tasks[user_id].append(recurring_task)
        self._save_tasks()
        
        # Build description
        freq_desc = frequency.title()
        if frequency == 'weekly' and days_of_week:
            day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            days_str = ', '.join([day_names[d] for d in sorted(days_of_week)])
            freq_desc = f"Weekly on {days_str}"
        
        time_desc = f" at {time_of_day}" if time_of_day else ""
        
        return recurring_task, f"🔁 **Recurring Task Created!**\n\n📝 Task: {task_name}\n📅 Frequency: {freq_desc}{time_desc}\n✅ Will auto-generate based on schedule!"
    
    def get_user_recurring_tasks(self, user_id):
        """Get all recurring tasks for a user"""
        user_id = str(user_id)
        
        if user_id not in self.recurring_tasks:
            return []
        
        return [task for task in self.recurring_tasks[user_id] if task['active']]
    
    def delete_recurring_task(self, user_id, task_id):
        """Delete/deactivate a recurring task"""
        user_id = str(user_id)
        
        if user_id not in self.recurring_tasks:
            return False, "No recurring tasks found!"
        
        for task in self.recurring_tasks[user_id]:
            if task['id'] == task_id:
                task['active'] = False
                self._save_tasks()
                return True, f"🗑️ Recurring task deleted: {task['task_name']}"
        
        return False, "Task not found!"
    
    def get_tasks_to_generate(self, user_id):
        """Get tasks that should be generated today"""
        user_id = str(user_id)
        
        if user_id not in self.recurring_tasks:
            return []
        
        today = datetime.now().date()
        today_weekday = today.weekday()  # 0 = Monday
        tasks_to_generate = []
        
        for task in self.recurring_tasks[user_id]:
            if not task['active']:
                continue
            
            # Check if already generated today
            last_gen = task.get('last_generated')
            if last_gen:
                last_gen_date = datetime.fromisoformat(last_gen).date()
                if last_gen_date == today:
                    continue  # Already generated today
            
            # Check if should generate today
            should_generate = False
            
            if task['frequency'] == 'daily':
                should_generate = True
            
            elif task['frequency'] == 'weekly':
                days = task.get('days_of_week', [])
                if today_weekday in days:
                    should_generate = True
            
            elif task['frequency'] == 'monthly':
                # Generate on the 1st of every month
                if today.day == 1:
                    should_generate = True
            
            if should_generate:
                tasks_to_generate.append(task)
        
        return tasks_to_generate
    
    def mark_generated(self, user_id, task_id):
        """Mark a recurring task as generated for today"""
        user_id = str(user_id)
        
        if user_id not in self.recurring_tasks:
            return False
        
        for task in self.recurring_tasks[user_id]:
            if task['id'] == task_id:
                task['last_generated'] = datetime.now().isoformat()
                self._save_tasks()
                return True
        
        return False
    
    def format_task_list(self, user_id):
        """Format recurring tasks for display"""
        tasks = self.get_user_recurring_tasks(user_id)
        
        if not tasks:
            return "📋 **Recurring Tasks**\n\nNo recurring tasks yet!\n\nUse /addrecurring to create one."
        
        msg = "🔁 **Your Recurring Tasks**\n\n"
        
        for task in tasks:
            freq = task['frequency'].title()
            if task['frequency'] == 'weekly' and task.get('days_of_week'):
                day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                days_str = ', '.join([day_names[d] for d in sorted(task['days_of_week'])])
                freq = f"Weekly ({days_str})"
            
            time_str = f" at {task['time_of_day']}" if task.get('time_of_day') else ""
            
            msg += f"**{task['id']}.** {task['task_name']}\n"
            msg += f"   📅 {freq}{time_str}\n\n"
        
        msg += "💡 Use /delrecurring <id> to remove a task"
        
        return msg
