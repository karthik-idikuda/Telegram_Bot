"""
Pomodoro Timer Manager
Manages focus sessions with breaks and tracking
"""
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

class PomodoroManager:
    def __init__(self, data_file="pomodoro_data.json"):
        self.data_file = Path(data_file)
        self.sessions = self._load_sessions()
        
    def _load_sessions(self):
        """Load pomodoro sessions from file"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_sessions(self):
        """Save pomodoro sessions to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.sessions, f, indent=2)
    
    def start_session(self, user_id, task_name, duration=25):
        """Start a new Pomodoro session"""
        user_id = str(user_id)
        
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                'total_sessions': 0,
                'total_minutes': 0,
                'current_session': None,
                'history': []
            }
        
        # Check if already in session
        if self.sessions[user_id]['current_session']:
            return None, "❌ You already have an active Pomodoro session!"
        
        start_time = datetime.now().isoformat()
        end_time = (datetime.now() + timedelta(minutes=duration)).isoformat()
        
        session = {
            'task': task_name,
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration,
            'completed': False,
            'break_taken': False
        }
        
        self.sessions[user_id]['current_session'] = session
        self._save_sessions()
        
        return session, f"🍅 **Pomodoro Started!**\n\n📝 Task: {task_name}\n⏱️ Duration: {duration} minutes\n🎯 Focus until: {datetime.fromisoformat(end_time).strftime('%I:%M %p')}\n\n💪 Stay focused, champ! I'll notify you when time's up."
    
    def complete_session(self, user_id):
        """Complete the current Pomodoro session"""
        user_id = str(user_id)
        
        if user_id not in self.sessions or not self.sessions[user_id]['current_session']:
            return None, "❌ No active Pomodoro session found!"
        
        session = self.sessions[user_id]['current_session']
        session['completed'] = True
        session['actual_end_time'] = datetime.now().isoformat()
        
        # Update stats
        self.sessions[user_id]['total_sessions'] += 1
        self.sessions[user_id]['total_minutes'] += session['duration']
        self.sessions[user_id]['history'].append(session)
        self.sessions[user_id]['current_session'] = None
        
        self._save_sessions()
        
        # Determine break duration
        break_duration = 15 if self.sessions[user_id]['total_sessions'] % 4 == 0 else 5
        
        return session, f"🎉 **Pomodoro Complete!**\n\n✅ Task: {session['task']}\n⏱️ Time: {session['duration']} minutes\n\n☕ Take a {break_duration}-minute break!\n{'🎊 Long break earned! (4th session)' if break_duration == 15 else '⚡ Quick break time!'}"
    
    def cancel_session(self, user_id):
        """Cancel the current Pomodoro session"""
        user_id = str(user_id)
        
        if user_id not in self.sessions or not self.sessions[user_id]['current_session']:
            return None, "❌ No active Pomodoro session to cancel!"
        
        task = self.sessions[user_id]['current_session']['task']
        self.sessions[user_id]['current_session'] = None
        self._save_sessions()
        
        return True, f"🛑 Pomodoro session cancelled.\n\n📝 Task: {task}\n\n💡 No worries! Start again when you're ready."
    
    def get_current_session(self, user_id):
        """Get current active session"""
        user_id = str(user_id)
        
        if user_id not in self.sessions or not self.sessions[user_id]['current_session']:
            return None
        
        session = self.sessions[user_id]['current_session']
        end_time = datetime.fromisoformat(session['end_time'])
        remaining = (end_time - datetime.now()).total_seconds() / 60
        
        if remaining <= 0:
            return {
                'task': session['task'],
                'status': 'finished',
                'message': f"⏰ **Time's Up!**\n\n🎯 Task: {session['task']}\n✅ Use /pomodoro_done to complete this session!"
            }
        
        return {
            'task': session['task'],
            'status': 'active',
            'remaining_minutes': int(remaining),
            'message': f"🍅 **Active Pomodoro**\n\n📝 Task: {session['task']}\n⏰ Time left: {int(remaining)} minutes\n\n💪 Keep going!"
        }
    
    def get_stats(self, user_id):
        """Get Pomodoro statistics"""
        user_id = str(user_id)
        
        if user_id not in self.sessions:
            return "📊 **Pomodoro Stats**\n\nNo sessions yet! Start your first Pomodoro with /pomodoro <task>"
        
        data = self.sessions[user_id]
        total_sessions = data['total_sessions']
        total_hours = data['total_minutes'] / 60
        
        # Get today's sessions
        today = datetime.now().date()
        today_sessions = [s for s in data['history'] if datetime.fromisoformat(s['start_time']).date() == today]
        
        # Get this week's sessions
        week_start = datetime.now() - timedelta(days=datetime.now().weekday())
        week_sessions = [s for s in data['history'] if datetime.fromisoformat(s['start_time']) >= week_start]
        
        current_status = "🍅 Active Session" if data['current_session'] else "💤 No Active Session"
        
        return f"""📊 **Pomodoro Statistics**

{current_status}

**All Time:**
🎯 Total Sessions: {total_sessions}
⏰ Total Time: {total_hours:.1f} hours
🔥 Average/Day: {total_sessions / max(1, len(set([datetime.fromisoformat(s['start_time']).date().isoformat() for s in data['history']]))):.1f} sessions

**Today:**
🍅 Sessions: {len(today_sessions)}
⏱️ Minutes: {sum([s['duration'] for s in today_sessions])}

**This Week:**
📅 Sessions: {len(week_sessions)}
💪 Focus Time: {sum([s['duration'] for s in week_sessions]) / 60:.1f} hours

{'🏆 You''re on fire! Keep it up!' if len(today_sessions) >= 4 else '💡 Tip: Try to complete 4 Pomodoros today!'}"""

    def get_recent_tasks(self, user_id, limit=5):
        """Get recently worked on tasks"""
        user_id = str(user_id)
        
        if user_id not in self.sessions or not self.sessions[user_id]['history']:
            return []
        
        history = self.sessions[user_id]['history']
        recent = sorted(history, key=lambda x: x['start_time'], reverse=True)[:limit]
        
        return [s['task'] for s in recent]
