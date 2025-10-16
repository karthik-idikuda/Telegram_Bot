import re
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from textblob import TextBlob
import json

class NLPHelper:
    """Advanced NLP for parsing tasks, dates, and sentiment analysis"""
    
    def __init__(self):
        self.urgency_keywords = {
            'high': ['urgent', 'asap', 'immediately', 'critical', 'emergency', 'deadline', 'today', 'now'],
            'medium': ['important', 'soon', 'this week', 'tomorrow', 'needed'],
            'low': ['maybe', 'someday', 'eventually', 'when possible']
        }
    
    def parse_task_with_time(self, text):
        """
        Parse natural language task with time/date
        Examples:
        - "Buy groceries tomorrow at 5 PM"
        - "Call mom every Sunday at 6 PM"
        - "Remind me to workout in 3 days"
        """
        result = {
            'task': text,
            'reminder_time': None,
            'recurring': None,
            'priority': 'medium',
            'parsed_date': None
        }
        
        # Extract priority
        result['priority'] = self.detect_priority(text)
        
        # Check for recurring patterns
        recurring_patterns = {
            r'every (monday|tuesday|wednesday|thursday|friday|saturday|sunday)': 'weekly',
            r'every day|daily': 'daily',
            r'every week|weekly': 'weekly',
            r'every month|monthly': 'monthly'
        }
        
        for pattern, recurrence in recurring_patterns.items():
            if re.search(pattern, text.lower()):
                result['recurring'] = recurrence
                break
        
        # Extract time and date
        time_info = self.extract_datetime(text)
        if time_info:
            # Use ISO format datetime for reminders
            result['reminder_time'] = time_info['datetime'].isoformat()
            result['parsed_date'] = time_info['datetime']
        
        # Clean task text (remove time/date phrases)
        clean_task = self.clean_task_text(text)
        result['task'] = clean_task
        
        return result
    
    def extract_datetime(self, text):
        """Extract date and time from natural language"""
        text_lower = text.lower()
        now = datetime.now()
        
        # Relative dates
        if 'tomorrow' in text_lower:
            target_date = now + timedelta(days=1)
        elif 'today' in text_lower:
            target_date = now
        elif 'next week' in text_lower:
            target_date = now + timedelta(weeks=1)
        elif match := re.search(r'in (\d+) (day|days|hour|hours|week|weeks)', text_lower):
            amount = int(match.group(1))
            unit = match.group(2)
            if 'day' in unit:
                target_date = now + timedelta(days=amount)
            elif 'week' in unit:
                target_date = now + timedelta(weeks=amount)
            elif 'hour' in unit:
                target_date = now + timedelta(hours=amount)
        else:
            target_date = now
        
        # Extract time (e.g., "at 5 PM", "6:30", "18:00")
        time_patterns = [
            r'at (\d{1,2}):?(\d{2})?\s*(am|pm)?',
            r'(\d{1,2}):(\d{2})',
            r'(\d{1,2})\s*(am|pm)'
        ]
        
        extracted_time = None
        for pattern in time_patterns:
            if match := re.search(pattern, text_lower):
                hour = int(match.group(1))
                minute = int(match.group(2)) if len(match.groups()) > 1 and match.group(2) else 0
                
                # Handle AM/PM
                if len(match.groups()) > 2 and match.group(3):
                    if match.group(3) == 'pm' and hour < 12:
                        hour += 12
                    elif match.group(3) == 'am' and hour == 12:
                        hour = 0
                
                extracted_time = f"{hour:02d}:{minute:02d}"
                target_date = target_date.replace(hour=hour, minute=minute, second=0)
                break
        
        if extracted_time:
            return {
                'time': extracted_time,
                'datetime': target_date
            }
        
        return None
    
    def detect_priority(self, text):
        """Detect task priority from keywords"""
        text_lower = text.lower()
        
        for priority, keywords in self.urgency_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return priority
        
        return 'medium'
    
    def clean_task_text(self, text):
        """Remove time/date phrases from task text"""
        # Remove common time phrases
        patterns = [
            r'\s+at \d{1,2}:?\d{0,2}\s*(am|pm)?',
            r'\s+tomorrow',
            r'\s+today',
            r'\s+next week',
            r'\s+in \d+ (day|days|hour|hours|week|weeks)',
            r'\s+every (monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'\s+every day',
            r'\s+daily',
            r'\s+weekly',
            r'\s+monthly'
        ]
        
        clean = text
        for pattern in patterns:
            clean = re.sub(pattern, '', clean, flags=re.IGNORECASE)
        
        return clean.strip()
    
    def analyze_sentiment(self, text):
        """Analyze sentiment and mood from text"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        
        if polarity > 0.3:
            mood = 'positive'
            energy = 'high'
        elif polarity > 0:
            mood = 'neutral-positive'
            energy = 'medium'
        elif polarity > -0.3:
            mood = 'neutral-negative'
            energy = 'medium'
        else:
            mood = 'negative'
            energy = 'low'
        
        return {
            'mood': mood,
            'energy': energy,
            'polarity': polarity,
            'subjectivity': blob.sentiment.subjectivity
        }
    
    def decompose_goal(self, goal):
        """Break down a big goal into weekly milestones (for GPT to enhance)"""
        # This returns a structure for GPT to fill in
        return {
            'goal': goal,
            'type': 'long_term',
            'requires_breakdown': True
        }
    
    def detect_task_patterns(self, task_history):
        """Analyze task completion patterns"""
        if not task_history:
            return None
        
        patterns = {
            'best_time': None,
            'completion_rate': 0,
            'common_skip_time': None,
            'productive_days': []
        }
        
        # Analyze completion times
        completion_times = []
        skip_times = []
        
        for task in task_history:
            if task.get('status') == 'done' and task.get('completed_at'):
                try:
                    completed_dt = datetime.fromisoformat(task['completed_at'])
                    completion_times.append(completed_dt.hour)
                except:
                    pass
            elif task.get('status') == 'pending' and task.get('reminder_time'):
                skip_times.append(task.get('reminder_time'))
        
        # Calculate best time (most common completion hour)
        if completion_times:
            from collections import Counter
            most_common_hour = Counter(completion_times).most_common(1)[0][0]
            patterns['best_time'] = f"{most_common_hour:02d}:00"
        
        # Completion rate
        total = len(task_history)
        done = len([t for t in task_history if t.get('status') == 'done'])
        patterns['completion_rate'] = (done / total * 100) if total > 0 else 0
        
        return patterns
