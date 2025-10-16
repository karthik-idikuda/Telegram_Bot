"""
Analytics and Insights Generator
Creates detailed productivity reports
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

class AnalyticsManager:
    def __init__(self, task_manager, time_tracker=None, pomodoro_manager=None, gamification=None):
        self.task_manager = task_manager
        self.time_tracker = time_tracker
        self.pomodoro_manager = pomodoro_manager
        self.gamification = gamification
    
    def generate_weekly_report(self, user_id):
        """Generate comprehensive weekly productivity report"""
        user_id = str(user_id)
        
        # Get date range
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = today
        
        # Get tasks from task_manager
        all_tasks = self.task_manager.get_tasks(user_id)
        
        # Filter tasks created/completed this week
        week_tasks = []
        completed_this_week = []
        
        for task in all_tasks:
            created_date = datetime.fromisoformat(task.get('created_at', datetime.now().isoformat()))
            
            if created_date >= week_start:
                week_tasks.append(task)
            
            if task.get('status') == 'done' and task.get('completed_at'):
                completed_date = datetime.fromisoformat(task['completed_at'])
                if completed_date >= week_start:
                    completed_this_week.append(task)
        
        # Calculate stats
        total_created = len(week_tasks)
        total_completed = len(completed_this_week)
        completion_rate = (total_completed / total_created * 100) if total_created > 0 else 0
        
        # Priority breakdown
        priority_stats = {'high': 0, 'medium': 0, 'low': 0}
        for task in completed_this_week:
            priority = task.get('priority', 'medium')
            priority_stats[priority] = priority_stats.get(priority, 0) + 1
        
        # Daily breakdown
        daily_completions = defaultdict(int)
        for task in completed_this_week:
            if task.get('completed_at'):
                day = datetime.fromisoformat(task['completed_at']).strftime('%A')
                daily_completions[day] += 1
        
        # Find best day
        best_day = max(daily_completions.items(), key=lambda x: x[1]) if daily_completions else ("None", 0)
        
        # Build report
        report = f"""📊 **Weekly Productivity Report**
{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}

**📈 Overview:**
✅ Tasks Completed: {total_completed}
📝 Tasks Created: {total_created}
🎯 Completion Rate: {completion_rate:.0f}%

**🎨 Priority Breakdown:**
🔴 High: {priority_stats.get('high', 0)} tasks
🟡 Medium: {priority_stats.get('medium', 0)} tasks
🟢 Low: {priority_stats.get('low', 0)} tasks

**📅 Daily Performance:**
"""
        
        # Add daily breakdown
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in days_order:
            count = daily_completions.get(day, 0)
            bar = "█" * count + "░" * max(0, 5 - count)
            report += f"{day[:3]}: {bar} {count}\n"
        
        report += f"\n🏆 Best Day: **{best_day[0]}** ({best_day[1]} tasks)\n"
        
        # Gamification stats
        if self.gamification:
            gam_data = self.gamification.user_data.get(user_id, {})
            streak = gam_data.get('current_streak', 0)
            level = gam_data.get('level', 1)
            xp = gam_data.get('xp', 0)
            
            report += f"\n**🎮 Gamification:**\n"
            report += f"⚡ Level: {level}\n"
            report += f"💎 XP: {xp}\n"
            report += f"🔥 Streak: {streak} days\n"
        
        # Pomodoro stats
        if self.pomodoro_manager and user_id in self.pomodoro_manager.sessions:
            pom_data = self.pomodoro_manager.sessions[user_id]
            week_sessions = [s for s in pom_data.get('history', []) 
                           if datetime.fromisoformat(s['start_time']) >= week_start]
            
            if week_sessions:
                total_pom_minutes = sum([s['duration'] for s in week_sessions])
                report += f"\n**🍅 Focus Time:**\n"
                report += f"Sessions: {len(week_sessions)}\n"
                report += f"Time: {total_pom_minutes / 60:.1f} hours\n"
        
        # Time tracking insights
        if self.time_tracker and user_id in self.time_tracker.tracking_data:
            time_data = self.time_tracker.tracking_data[user_id]
            week_tracked = [t for t in time_data.get('completed_tasks', [])
                          if datetime.fromisoformat(t['end_time']) >= week_start]
            
            if week_tracked:
                total_tracked_minutes = sum([t['actual_minutes'] for t in week_tracked])
                report += f"\n**⏱️ Time Tracked:**\n"
                report += f"Tasks: {len(week_tracked)}\n"
                report += f"Time: {total_tracked_minutes / 60:.1f} hours\n"
        
        # Add insights and motivation
        report += self._generate_insights(completion_rate, total_completed, best_day[0])
        
        return report
    
    def _generate_insights(self, completion_rate, tasks_completed, best_day):
        """Generate personalized insights based on performance"""
        insights = "\n**💡 Insights:**\n"
        
        if completion_rate >= 80:
            insights += "🌟 Outstanding! You're crushing your goals!\n"
        elif completion_rate >= 60:
            insights += "💪 Great work! You're maintaining strong momentum!\n"
        elif completion_rate >= 40:
            insights += "📈 Good progress! Room for improvement.\n"
        else:
            insights += "🎯 Focus needed. Try breaking tasks into smaller chunks!\n"
        
        if tasks_completed == 0:
            insights += "💡 Tip: Start with just ONE task tomorrow!\n"
        elif tasks_completed < 5:
            insights += "💡 Tip: Aim for 1-2 tasks per day for consistency!\n"
        elif tasks_completed >= 20:
            insights += "🔥 You're a productivity machine! Keep it up!\n"
        
        if best_day != "None":
            insights += f"📊 Your peak performance day is {best_day}. Schedule important tasks then!\n"
        
        return insights
    
    def get_productivity_score(self, user_id):
        """Calculate overall productivity score (0-100)"""
        user_id = str(user_id)
        
        # Get last 30 days of tasks
        thirty_days_ago = datetime.now() - timedelta(days=30)
        all_tasks = self.task_manager.get_tasks(user_id)
        
        recent_tasks = [t for t in all_tasks 
                       if datetime.fromisoformat(t.get('created_at', datetime.now().isoformat())) >= thirty_days_ago]
        
        if not recent_tasks:
            return 0
        
        completed = [t for t in recent_tasks if t.get('status') == 'done']
        
        # Factors for scoring
        completion_rate = len(completed) / len(recent_tasks) if recent_tasks else 0
        
        # Streak bonus
        streak_bonus = 0
        if self.gamification and user_id in self.gamification.user_data:
            streak = self.gamification.user_data[user_id].get('current_streak', 0)
            streak_bonus = min(streak / 30, 0.3)  # Max 30% bonus
        
        # Calculate score
        base_score = completion_rate * 70  # 70% weight on completion
        score = min(100, int(base_score + (streak_bonus * 100)))
        
        return score
    
    def get_time_of_day_analysis(self, user_id):
        """Analyze productivity by time of day"""
        user_id = str(user_id)
        
        all_tasks = self.task_manager.get_tasks(user_id)
        completed = [t for t in all_tasks if t.get('status') == 'done' and t.get('completed_at')]
        
        if len(completed) < 3:
            return "⏰ Not enough data for time analysis. Complete more tasks!"
        
        # Group by hour
        hour_counts = defaultdict(int)
        for task in completed:
            hour = datetime.fromisoformat(task['completed_at']).hour
            hour_counts[hour] += 1
        
        # Find peak hours
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        top_3_hours = sorted_hours[:3]
        
        msg = "⏰ **Peak Productivity Hours**\n\n"
        
        for hour, count in top_3_hours:
            period = "AM" if hour < 12 else "PM"
            display_hour = hour if hour <= 12 else hour - 12
            if display_hour == 0:
                display_hour = 12
            
            msg += f"🕐 {display_hour}:00 {period} - {count} tasks\n"
        
        # Determine if morning/evening person
        morning_tasks = sum([count for hour, count in hour_counts.items() if 5 <= hour < 12])
        evening_tasks = sum([count for hour, count in hour_counts.items() if 17 <= hour < 23])
        
        if morning_tasks > evening_tasks * 1.5:
            msg += "\n☀️ You're a morning person! Schedule important tasks early."
        elif evening_tasks > morning_tasks * 1.5:
            msg += "\n🌙 You're a night owl! Your peak is in the evening."
        else:
            msg += "\n⚖️ You're productive throughout the day!"
        
        return msg
