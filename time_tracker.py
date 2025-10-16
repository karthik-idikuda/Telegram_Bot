"""
Time Tracker for Tasks
Tracks actual time spent vs estimated time
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

class TimeTracker:
    def __init__(self, data_file="time_tracking.json"):
        self.data_file = Path(data_file)
        self.tracking_data = self._load_data()
        
    def _load_data(self):
        """Load time tracking data from file"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_data(self):
        """Save time tracking data to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.tracking_data, f, indent=2)
    
    def start_tracking(self, user_id, task_id, task_name, estimated_minutes=None):
        """Start tracking time for a task"""
        user_id = str(user_id)
        task_id = str(task_id)
        
        if user_id not in self.tracking_data:
            self.tracking_data[user_id] = {
                'active_task': None,
                'completed_tasks': []
            }
        
        # Stop any active tracking
        if self.tracking_data[user_id]['active_task']:
            return None, f"❌ Already tracking: {self.tracking_data[user_id]['active_task']['task_name']}\n\nStop it first with /stoptrack"
        
        tracking = {
            'task_id': task_id,
            'task_name': task_name,
            'start_time': datetime.now().isoformat(),
            'estimated_minutes': estimated_minutes
        }
        
        self.tracking_data[user_id]['active_task'] = tracking
        self._save_data()
        
        msg = f"⏱️ **Time Tracking Started**\n\n📝 Task: {task_name}\n🕐 Started: {datetime.now().strftime('%I:%M %p')}"
        if estimated_minutes:
            msg += f"\n⏰ Estimated: {estimated_minutes} minutes"
        msg += "\n\n✅ Use /stoptrack when done!"
        
        return tracking, msg
    
    def stop_tracking(self, user_id, notes=None):
        """Stop tracking time for current task"""
        user_id = str(user_id)
        
        if user_id not in self.tracking_data or not self.tracking_data[user_id]['active_task']:
            return None, "❌ No active time tracking session!"
        
        active = self.tracking_data[user_id]['active_task']
        start_time = datetime.fromisoformat(active['start_time'])
        end_time = datetime.now()
        
        actual_minutes = int((end_time - start_time).total_seconds() / 60)
        
        completed = {
            'task_id': active['task_id'],
            'task_name': active['task_name'],
            'start_time': active['start_time'],
            'end_time': end_time.isoformat(),
            'actual_minutes': actual_minutes,
            'estimated_minutes': active.get('estimated_minutes'),
            'notes': notes,
            'date': datetime.now().date().isoformat()
        }
        
        self.tracking_data[user_id]['completed_tasks'].append(completed)
        self.tracking_data[user_id]['active_task'] = None
        self._save_data()
        
        msg = f"✅ **Time Tracking Stopped**\n\n📝 Task: {active['task_name']}\n⏱️ Actual Time: {actual_minutes} minutes"
        
        if active.get('estimated_minutes'):
            diff = actual_minutes - active['estimated_minutes']
            accuracy = (1 - abs(diff) / active['estimated_minutes']) * 100
            
            if diff > 0:
                msg += f"\n⏰ Estimated: {active['estimated_minutes']} minutes\n📊 Overestimated by {diff} minutes ({accuracy:.0f}% accurate)"
            elif diff < 0:
                msg += f"\n⏰ Estimated: {active['estimated_minutes']} minutes\n📊 Underestimated by {abs(diff)} minutes ({accuracy:.0f}% accurate)"
            else:
                msg += f"\n⏰ Estimated: {active['estimated_minutes']} minutes\n🎯 Perfect estimate! 100% accurate!"
        
        return completed, msg
    
    def get_active_tracking(self, user_id):
        """Get current active tracking session"""
        user_id = str(user_id)
        
        if user_id not in self.tracking_data or not self.tracking_data[user_id]['active_task']:
            return None
        
        active = self.tracking_data[user_id]['active_task']
        start_time = datetime.fromisoformat(active['start_time'])
        elapsed = int((datetime.now() - start_time).total_seconds() / 60)
        
        return {
            'task_name': active['task_name'],
            'elapsed_minutes': elapsed,
            'estimated_minutes': active.get('estimated_minutes'),
            'start_time': active['start_time']
        }
    
    def get_insights(self, user_id):
        """Get time tracking insights and analytics"""
        user_id = str(user_id)
        
        if user_id not in self.tracking_data or not self.tracking_data[user_id]['completed_tasks']:
            return "📊 **Time Tracking Insights**\n\nNo completed tasks yet! Start tracking with /starttrack <task>"
        
        tasks = self.tracking_data[user_id]['completed_tasks']
        
        # Overall stats
        total_tasks = len(tasks)
        total_minutes = sum([t['actual_minutes'] for t in tasks])
        avg_duration = total_minutes / total_tasks
        
        # Estimation accuracy (only tasks with estimates)
        estimated_tasks = [t for t in tasks if t.get('estimated_minutes')]
        if estimated_tasks:
            accuracy_scores = []
            for task in estimated_tasks:
                diff = abs(task['actual_minutes'] - task['estimated_minutes'])
                accuracy = max(0, (1 - diff / task['estimated_minutes']) * 100)
                accuracy_scores.append(accuracy)
            avg_accuracy = sum(accuracy_scores) / len(accuracy_scores)
            
            # Determine if user under/overestimates
            total_diff = sum([t['actual_minutes'] - t['estimated_minutes'] for t in estimated_tasks])
            estimation_trend = "underestimate" if total_diff > 0 else "overestimate" if total_diff < 0 else "accurately estimate"
        else:
            avg_accuracy = 0
            estimation_trend = "unknown"
        
        # Today's stats
        today = datetime.now().date().isoformat()
        today_tasks = [t for t in tasks if t.get('date') == today]
        today_minutes = sum([t['actual_minutes'] for t in today_tasks])
        
        # This week's stats
        week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).date().isoformat()
        week_tasks = [t for t in tasks if t.get('date', '') >= week_start]
        week_minutes = sum([t['actual_minutes'] for t in week_tasks])
        
        # Longest task
        longest = max(tasks, key=lambda x: x['actual_minutes'])
        
        msg = f"""📊 **Time Tracking Insights**

**Overall Performance:**
✅ Tasks Completed: {total_tasks}
⏰ Total Time: {total_minutes / 60:.1f} hours
📈 Average Duration: {avg_duration:.0f} minutes/task

**Today:**
🎯 Tasks: {len(today_tasks)}
⏱️ Time: {today_minutes} minutes ({today_minutes / 60:.1f} hours)

**This Week:**
📅 Tasks: {len(week_tasks)}
💪 Time: {week_minutes / 60:.1f} hours

**Estimation Accuracy:**
"""
        
        if estimated_tasks:
            msg += f"🎯 Average Accuracy: {avg_accuracy:.0f}%\n"
            msg += f"📊 You tend to **{estimation_trend}** task duration\n"
            
            if avg_accuracy < 50:
                msg += "\n💡 Tip: Track more tasks to improve estimates!"
            elif avg_accuracy < 75:
                msg += "\n💡 Tip: Getting better! Keep tracking!"
            else:
                msg += "\n🏆 Excellent! You're great at estimating!"
        else:
            msg += "📝 No estimated tasks yet\n💡 Add estimates to track accuracy!"
        
        msg += f"\n\n**Longest Task:**\n🏅 {longest['task_name']} ({longest['actual_minutes']} min)"
        
        return msg
    
    def get_category_insights(self, user_id):
        """Analyze time spent by task patterns"""
        user_id = str(user_id)
        
        if user_id not in self.tracking_data or not self.tracking_data[user_id]['completed_tasks']:
            return None
        
        tasks = self.tracking_data[user_id]['completed_tasks']
        
        # Group by task keywords
        categories = {}
        keywords = ['work', 'study', 'code', 'meeting', 'email', 'exercise', 'read']
        
        for task in tasks:
            task_lower = task['task_name'].lower()
            categorized = False
            
            for keyword in keywords:
                if keyword in task_lower:
                    if keyword not in categories:
                        categories[keyword] = []
                    categories[keyword].append(task['actual_minutes'])
                    categorized = True
            
            if not categorized:
                if 'other' not in categories:
                    categories['other'] = []
                categories['other'].append(task['actual_minutes'])
        
        # Build report
        if not categories:
            return None
        
        msg = "📊 **Time by Category**\n\n"
        sorted_cats = sorted(categories.items(), key=lambda x: sum(x[1]), reverse=True)
        
        for cat, minutes_list in sorted_cats[:5]:
            total = sum(minutes_list)
            avg = total / len(minutes_list)
            msg += f"• **{cat.title()}**: {total / 60:.1f}h ({len(minutes_list)} tasks, avg {avg:.0f} min)\n"
        
        return msg
