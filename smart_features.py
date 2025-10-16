from datetime import datetime, timedelta
import json
from collections import Counter

class SmartFeatures:
    """Advanced AI-powered productivity features"""
    
    def __init__(self, task_manager, gpt_helper):
        self.task_manager = task_manager
        self.gpt = gpt_helper
        self.user_patterns = {}  # Store learned patterns per user
    
    def analyze_user_patterns(self, user_id):
        """Analyze user's task completion patterns"""
        tasks = self.task_manager.get_user_tasks(user_id)
        
        if not tasks:
            return None
        
        completed_tasks = [t for t in tasks if t['status'] == 'done']
        pending_tasks = [t for t in tasks if t['status'] == 'pending']
        
        patterns = {
            'total_tasks': len(tasks),
            'completion_rate': len(completed_tasks) / len(tasks) * 100 if tasks else 0,
            'most_productive_time': None,
            'skip_patterns': [],
            'average_completion_time': None
        }
        
        # Analyze completion times
        completion_hours = []
        for task in completed_tasks:
            if task.get('last_updated'):
                try:
                    dt = datetime.fromisoformat(task['last_updated'])
                    completion_hours.append(dt.hour)
                except:
                    pass
        
        if completion_hours:
            most_common = Counter(completion_hours).most_common(1)[0][0]
            patterns['most_productive_time'] = f"{most_common:02d}:00"
        
        self.user_patterns[user_id] = patterns
        return patterns
    
    def suggest_best_time(self, user_id, task_name):
        """Suggest best time for a task based on patterns"""
        patterns = self.user_patterns.get(user_id) or self.analyze_user_patterns(user_id)
        
        if not patterns or not patterns['most_productive_time']:
            return "I don't have enough data yet. Complete a few tasks and I'll learn your patterns! 📊"
        
        best_time = patterns['most_productive_time']
        
        # Use GPT to make it conversational
        prompt = f"""User wants to schedule: '{task_name}'
Based on data, they're most productive at {best_time}.
Give a friendly suggestion about scheduling the task at that time (1-2 sentences)."""
        
        return self.gpt.ask_gpt(prompt)
    
    def detect_forgotten_tasks(self, user_id, days_threshold=3):
        """Detect tasks that user might have forgotten"""
        tasks = self.task_manager.get_pending_tasks(user_id)
        forgotten = []
        
        now = datetime.now()
        
        for task in tasks:
            if task.get('created_at'):
                try:
                    created = datetime.fromisoformat(task['created_at'])
                    days_old = (now - created).days
                    
                    if days_old >= days_threshold:
                        forgotten.append({
                            'task': task,
                            'days_old': days_old
                        })
                except:
                    pass
        
        return forgotten
    
    def proactive_reminder(self, user_id):
        """Generate proactive reminder for forgotten tasks"""
        forgotten = self.detect_forgotten_tasks(user_id)
        
        if not forgotten:
            return None
        
        # Pick the oldest task
        oldest = max(forgotten, key=lambda x: x['days_old'])
        task_name = oldest['task']['task']
        days = oldest['days_old']
        
        prompt = f"""User hasn't completed '{task_name}' for {days} days.
Send a gentle, motivating reminder (1-2 sentences). Be encouraging, not pushy."""
        
        message = self.gpt.ask_gpt(prompt)
        return {
            'task': oldest['task'],
            'message': message
        }
    
    def smart_reschedule_suggestion(self, user_id, task_id):
        """Suggest better time if user keeps skipping a task"""
        task = self.task_manager.get_task_by_id(task_id, user_id)
        
        if not task:
            return None
        
        # Check how many times this task was rescheduled
        reschedule_count = task.get('reschedule_count', 0)
        
        if reschedule_count >= 2:
            patterns = self.analyze_user_patterns(user_id)
            best_time = patterns.get('most_productive_time', '09:00') if patterns else '09:00'
            
            prompt = f"""User keeps postponing '{task['task']}' (rescheduled {reschedule_count} times).
Suggest trying their most productive time ({best_time}) instead.
Be empathetic and encouraging (2 sentences)."""
            
            return self.gpt.ask_gpt(prompt)
        
        return None
    
    def decompose_big_goal(self, goal_text):
        """Break down a big goal into weekly milestones using GPT"""
        prompt = f"""Break down this goal into 4-6 weekly milestones:
Goal: "{goal_text}"

Format your response as a numbered list of weekly tasks.
Each milestone should be specific and achievable in one week.
Example format:
Week 1: [specific task]
Week 2: [specific task]
etc.

Keep it practical and motivating."""
        
        breakdown = self.gpt.ask_gpt(prompt)
        
        # Parse the breakdown into structured format
        milestones = []
        lines = breakdown.split('\n')
        
        for line in lines:
            if line.strip() and ('Week' in line or 'week' in line):
                milestones.append(line.strip())
        
        return {
            'goal': goal_text,
            'milestones': milestones,
            'breakdown_text': breakdown
        }
    
    def track_mood(self, user_id, mood_data):
        """Track user mood over time"""
        # Store mood data in user patterns
        if user_id not in self.user_patterns:
            self.user_patterns[user_id] = {}
        
        if 'mood_history' not in self.user_patterns[user_id]:
            self.user_patterns[user_id]['mood_history'] = []
        
        self.user_patterns[user_id]['mood_history'].append({
            'date': datetime.now().isoformat(),
            'mood': mood_data['mood'],
            'energy': mood_data['energy'],
            'polarity': mood_data['polarity']
        })
        
        # Keep only last 30 days
        if len(self.user_patterns[user_id]['mood_history']) > 30:
            self.user_patterns[user_id]['mood_history'] = \
                self.user_patterns[user_id]['mood_history'][-30:]
    
    def generate_weekly_mood_report(self, user_id):
        """Generate weekly mood and productivity report"""
        if user_id not in self.user_patterns or 'mood_history' not in self.user_patterns[user_id]:
            return "Not enough data for a mood report yet. Chat with me more! 😊"
        
        mood_history = self.user_patterns[user_id]['mood_history'][-7:]  # Last 7 days
        
        if not mood_history:
            return "Not enough data for a mood report yet. Chat with me more! 😊"
        
        # Analyze mood trends
        positive_days = len([m for m in mood_history if m['mood'] in ['positive', 'neutral-positive']])
        negative_days = len([m for m in mood_history if m['mood'] in ['negative', 'neutral-negative']])
        
        # Get task stats
        stats = self.task_manager.get_daily_stats(user_id)
        
        prompt = f"""Generate a weekly mood and productivity report:

Mood: {positive_days} positive days, {negative_days} tough days
Tasks: {stats['done']} completed, {stats['pending']} pending

Create an encouraging, insightful summary (3-4 sentences).
Acknowledge struggles, celebrate wins, and motivate for next week."""
        
        return self.gpt.ask_gpt(prompt)
    
    def adjust_tone_for_mood(self, user_id, base_message):
        """Adjust message tone based on recent mood"""
        if user_id not in self.user_patterns or 'mood_history' not in self.user_patterns[user_id]:
            return base_message
        
        recent_moods = self.user_patterns[user_id]['mood_history'][-3:]  # Last 3 interactions
        
        if not recent_moods:
            return base_message
        
        avg_polarity = sum(m['polarity'] for m in recent_moods) / len(recent_moods)
        
        if avg_polarity < -0.2:  # User seems stressed/down
            tone = "gentle and supportive"
        elif avg_polarity > 0.3:  # User is energetic
            tone = "enthusiastic and energetic"
        else:
            tone = "friendly and encouraging"
        
        prompt = f"""Rewrite this message with a {tone} tone:
"{base_message}"

Keep the same information but adjust the tone. 1-2 sentences max."""
        
        return self.gpt.ask_gpt(prompt)
