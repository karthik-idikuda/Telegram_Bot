import json
import os
from datetime import datetime
import pytz

class TaskManager:
    """Manage tasks using JSON file storage (can be replaced with Google Sheets later)"""
    
    def __init__(self, file_path='tasks.json'):
        self.file_path = file_path
        self.tasks = self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from JSON file"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        with open(self.file_path, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def add_task(self, task_name, user_id, reminder_time=None, priority='medium', recurring=None):
        """Add a new task"""
        task = {
            'id': len(self.tasks) + 1,
            'user_id': user_id,
            'task': task_name,
            'status': 'pending',
            'reminder_time': reminder_time,
            'priority': priority,
            'recurring': recurring,
            'reschedule_count': 0,
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'completed_at': None,
            'notes': ''
        }
        self.tasks.append(task)
        self.save_tasks()
        return task
    
    def get_user_tasks(self, user_id, status=None):
        """Get all tasks for a specific user"""
        user_tasks = [t for t in self.tasks if t['user_id'] == user_id]
        
        if status:
            user_tasks = [t for t in user_tasks if t['status'] == status]
        
        return user_tasks
    
    def get_pending_tasks(self, user_id):
        """Get pending tasks for a user"""
        return self.get_user_tasks(user_id, status='pending')
    
    def mark_done(self, task_id, user_id):
        """Mark a task as done"""
        for task in self.tasks:
            if task['id'] == task_id and task['user_id'] == user_id:
                task['status'] = 'done'
                task['last_updated'] = datetime.now().isoformat()
                task['completed_at'] = datetime.now().isoformat()
                self.save_tasks()
                return task
        return None
    
    def reschedule_task(self, task_id, user_id, new_time):
        """Reschedule a task"""
        for task in self.tasks:
            if task['id'] == task_id and task['user_id'] == user_id:
                task['reminder_time'] = new_time
                task['last_updated'] = datetime.now().isoformat()
                task['reschedule_count'] = task.get('reschedule_count', 0) + 1
                self.save_tasks()
                return task
        return None
    
    def update_task(self, task_id, user_id, **kwargs):
        """Update any task field"""
        for task in self.tasks:
            if task['id'] == task_id and task['user_id'] == user_id:
                task.update(kwargs)
                task['last_updated'] = datetime.now().isoformat()
                self.save_tasks()
                return task
        return None
    
    def delete_task(self, task_id, user_id):
        """Delete a task"""
        self.tasks = [t for t in self.tasks if not (t['id'] == task_id and t['user_id'] == user_id)]
        self.save_tasks()
    
    def get_task_by_id(self, task_id, user_id):
        """Get a specific task"""
        for task in self.tasks:
            if task['id'] == task_id and task['user_id'] == user_id:
                return task
        return None
    
    def get_due_reminders(self):
        """Get all tasks with due reminders"""
        due_tasks = []
        now = datetime.now()
        
        for task in self.tasks:
            if task['status'] == 'pending' and task['reminder_time']:
                try:
                    # Handle both ISO format (2025-10-16T10:53:00) and space format (2025-10-16 10:53:00)
                    reminder_str = str(task['reminder_time']).replace(' ', 'T')
                    task_time = datetime.fromisoformat(reminder_str)
                    if task_time <= now:
                        due_tasks.append(task)
                except Exception as e:
                    print(f"⚠️ Error parsing reminder time for task {task['id']}: {task['reminder_time']} - {e}")
        
        return due_tasks
    
    def mark_reminder_sent(self, task_id):
        """Mark that reminder was sent for this task"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['reminder_sent'] = True
                task['last_updated'] = datetime.now().isoformat()
                self.save_tasks()
                return task
        return None
    
    def get_daily_stats(self, user_id):
        """Get daily statistics"""
        all_tasks = self.get_user_tasks(user_id)
        pending = len([t for t in all_tasks if t['status'] == 'pending'])
        done = len([t for t in all_tasks if t['status'] == 'done'])
        
        return {
            'total': len(all_tasks),
            'pending': pending,
            'done': done
        }
