"""
Gamification System - XP, Levels, Achievements, Streaks
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

class GamificationManager:
    def __init__(self, data_file="gamification_data.json"):
        self.data_file = Path(data_file)
        self.user_data = self._load_data()
        
        # Achievement definitions
        self.achievements = {
            'first_task': {'name': '🎯 First Step', 'description': 'Complete your first task', 'xp': 50},
            'early_bird': {'name': '🌅 Early Bird', 'description': 'Complete a task before 8 AM', 'xp': 100},
            'night_owl': {'name': '🦉 Night Owl', 'description': 'Complete a task after 10 PM', 'xp': 100},
            'streak_7': {'name': '🔥 Week Warrior', 'description': '7-day completion streak', 'xp': 200},
            'streak_30': {'name': '⚡ Month Master', 'description': '30-day completion streak', 'xp': 500},
            'streak_100': {'name': '👑 Century Champion', 'description': '100-day completion streak', 'xp': 1000},
            'tasks_10': {'name': '💪 Getting Started', 'description': 'Complete 10 tasks', 'xp': 150},
            'tasks_50': {'name': '🚀 Productivity Pro', 'description': 'Complete 50 tasks', 'xp': 300},
            'tasks_100': {'name': '🏆 Task Master', 'description': 'Complete 100 tasks', 'xp': 600},
            'tasks_500': {'name': '⭐ Elite Performer', 'description': 'Complete 500 tasks', 'xp': 1500},
            'perfect_day': {'name': '✨ Perfect Day', 'description': 'Complete all tasks in a day', 'xp': 250},
            'speed_demon': {'name': '⚡ Speed Demon', 'description': 'Complete 5 tasks in 1 hour', 'xp': 200},
            'pomodoro_master': {'name': '🍅 Pomodoro Master', 'description': 'Complete 20 Pomodoro sessions', 'xp': 300},
            'focus_warrior': {'name': '🎯 Focus Warrior', 'description': 'Complete 4 Pomodoros in one day', 'xp': 150},
        }
        
        # Level thresholds (XP needed)
        self.level_thresholds = [0, 100, 250, 500, 1000, 2000, 3500, 5500, 8000, 11000, 15000, 20000, 26000, 33000, 41000, 50000]
        
    def _load_data(self):
        """Load gamification data from file"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_data(self):
        """Save gamification data to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.user_data, f, indent=2)
    
    def _init_user(self, user_id):
        """Initialize a new user's gamification data"""
        user_id = str(user_id)
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                'xp': 0,
                'level': 1,
                'total_tasks_completed': 0,
                'achievements': [],
                'current_streak': 0,
                'longest_streak': 0,
                'last_task_date': None,
                'streak_dates': [],
                'daily_tasks': {},
                'task_completion_times': []
            }
            self._save_data()
    
    def add_xp(self, user_id, xp, reason=""):
        """Add XP to user and check for level up"""
        user_id = str(user_id)
        self._init_user(user_id)
        
        old_level = self._get_level(self.user_data[user_id]['xp'])
        self.user_data[user_id]['xp'] += xp
        new_level = self._get_level(self.user_data[user_id]['xp'])
        
        self.user_data[user_id]['level'] = new_level
        self._save_data()
        
        # Check if leveled up
        if new_level > old_level:
            return {
                'leveled_up': True,
                'old_level': old_level,
                'new_level': new_level,
                'xp_gained': xp,
                'total_xp': self.user_data[user_id]['xp'],
                'message': f"🎊 **LEVEL UP!**\n\nYou reached **Level {new_level}**! 🚀\n+{xp} XP ({reason})\n\n💪 Keep crushing it, champion!"
            }
        else:
            next_level_xp = self.level_thresholds[new_level] if new_level < len(self.level_thresholds) else self.level_thresholds[-1] + (new_level - len(self.level_thresholds) + 1) * 10000
            xp_to_next = next_level_xp - self.user_data[user_id]['xp']
            
            return {
                'leveled_up': False,
                'level': new_level,
                'xp_gained': xp,
                'total_xp': self.user_data[user_id]['xp'],
                'xp_to_next_level': xp_to_next,
                'message': f"+{xp} XP ({reason})\n💎 {xp_to_next} XP to Level {new_level + 1}"
            }
    
    def _get_level(self, xp):
        """Calculate level from XP"""
        for level, threshold in enumerate(self.level_thresholds, start=1):
            if xp < threshold:
                return level - 1
        # Beyond max threshold
        return len(self.level_thresholds) + (xp - self.level_thresholds[-1]) // 10000
    
    def task_completed(self, user_id, task_data=None):
        """Handle task completion - update stats, streaks, check achievements"""
        user_id = str(user_id)
        self._init_user(user_id)
        
        data = self.user_data[user_id]
        today = datetime.now().date().isoformat()
        
        # Update task count
        data['total_tasks_completed'] += 1
        
        # Track daily tasks
        if today not in data['daily_tasks']:
            data['daily_tasks'][today] = 0
        data['daily_tasks'][today] += 1
        
        # Track completion time
        current_hour = datetime.now().hour
        data['task_completion_times'].append({
            'time': datetime.now().isoformat(),
            'hour': current_hour
        })
        
        # Update streak
        new_achievements = []
        yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
        
        if data['last_task_date'] == today:
            # Same day, streak continues
            pass
        elif data['last_task_date'] == yesterday:
            # Streak continues
            data['current_streak'] += 1
            data['streak_dates'].append(today)
        else:
            # Streak broken or first task
            data['current_streak'] = 1
            data['streak_dates'] = [today]
        
        data['last_task_date'] = today
        
        if data['current_streak'] > data['longest_streak']:
            data['longest_streak'] = data['current_streak']
        
        # Base XP for completing task
        xp_rewards = []
        base_xp = 10
        xp_rewards.append((base_xp, "Task Completed"))
        
        # Check for new achievements
        new_achievements.extend(self._check_achievements(user_id, task_data))
        
        # Award achievement XP
        for achievement in new_achievements:
            xp_rewards.append((self.achievements[achievement]['xp'], self.achievements[achievement]['name']))
        
        self._save_data()
        
        return {
            'achievements': new_achievements,
            'xp_rewards': xp_rewards,
            'streak': data['current_streak'],
            'total_tasks': data['total_tasks_completed']
        }
    
    def _check_achievements(self, user_id, task_data=None):
        """Check and award new achievements"""
        user_id = str(user_id)
        data = self.user_data[user_id]
        new_achievements = []
        
        current_hour = datetime.now().hour
        today = datetime.now().date().isoformat()
        
        # First task
        if data['total_tasks_completed'] == 1 and 'first_task' not in data['achievements']:
            new_achievements.append('first_task')
            data['achievements'].append('first_task')
        
        # Early bird (before 8 AM)
        if current_hour < 8 and 'early_bird' not in data['achievements']:
            new_achievements.append('early_bird')
            data['achievements'].append('early_bird')
        
        # Night owl (after 10 PM)
        if current_hour >= 22 and 'night_owl' not in data['achievements']:
            new_achievements.append('night_owl')
            data['achievements'].append('night_owl')
        
        # Streak achievements
        if data['current_streak'] >= 7 and 'streak_7' not in data['achievements']:
            new_achievements.append('streak_7')
            data['achievements'].append('streak_7')
        
        if data['current_streak'] >= 30 and 'streak_30' not in data['achievements']:
            new_achievements.append('streak_30')
            data['achievements'].append('streak_30')
        
        if data['current_streak'] >= 100 and 'streak_100' not in data['achievements']:
            new_achievements.append('streak_100')
            data['achievements'].append('streak_100')
        
        # Task count achievements
        total = data['total_tasks_completed']
        if total >= 10 and 'tasks_10' not in data['achievements']:
            new_achievements.append('tasks_10')
            data['achievements'].append('tasks_10')
        
        if total >= 50 and 'tasks_50' not in data['achievements']:
            new_achievements.append('tasks_50')
            data['achievements'].append('tasks_50')
        
        if total >= 100 and 'tasks_100' not in data['achievements']:
            new_achievements.append('tasks_100')
            data['achievements'].append('tasks_100')
        
        if total >= 500 and 'tasks_500' not in data['achievements']:
            new_achievements.append('tasks_500')
            data['achievements'].append('tasks_500')
        
        # Speed demon (5 tasks in 1 hour)
        if 'speed_demon' not in data['achievements']:
            recent_tasks = [t for t in data['task_completion_times'] if 
                          (datetime.now() - datetime.fromisoformat(t['time'])).total_seconds() < 3600]
            if len(recent_tasks) >= 5:
                new_achievements.append('speed_demon')
                data['achievements'].append('speed_demon')
        
        return new_achievements
    
    def get_user_data(self, user_id):
        """Get user's gamification data as a dictionary"""
        user_id = str(user_id)
        self._init_user(user_id)
        
        data = self.user_data[user_id]
        level = data['level']
        xp = data['xp']
        
        # Calculate XP to next level
        next_level_xp = self.level_thresholds[level] if level < len(self.level_thresholds) else self.level_thresholds[-1] + (level - len(self.level_thresholds) + 1) * 10000
        xp_to_next = next_level_xp - xp
        xp_progress = xp - (self.level_thresholds[level - 1] if level > 0 else 0)
        xp_needed = next_level_xp - (self.level_thresholds[level - 1] if level > 0 else 0)
        progress_percent = (xp_progress / xp_needed * 100) if xp_needed > 0 else 100
        
        return {
            'level': level,
            'xp': xp,
            'next_level_xp': next_level_xp,
            'xp_to_next': xp_to_next,
            'xp_progress': xp_progress,
            'xp_needed': xp_needed,
            'progress_percent': progress_percent,
            'total_tasks_completed': data['total_tasks_completed'],
            'current_streak': data['current_streak'],
            'longest_streak': data['longest_streak'],
            'achievements': data['achievements']
        }
    
    def get_profile(self, user_id):
        """Get user's gamification profile"""
        user_id = str(user_id)
        self._init_user(user_id)
        
        data = self.user_data[user_id]
        level = data['level']
        xp = data['xp']
        
        # Calculate XP to next level
        next_level_xp = self.level_thresholds[level] if level < len(self.level_thresholds) else self.level_thresholds[-1] + (level - len(self.level_thresholds) + 1) * 10000
        xp_to_next = next_level_xp - xp
        xp_progress = xp - (self.level_thresholds[level - 1] if level > 0 else 0)
        xp_needed = next_level_xp - (self.level_thresholds[level - 1] if level > 0 else 0)
        progress_percent = (xp_progress / xp_needed * 100) if xp_needed > 0 else 100
        
        # Progress bar
        filled = int(progress_percent / 10)
        bar = "█" * filled + "░" * (10 - filled)
        
        msg = f"""🎮 **Productivity Profile**

**Level {level}** - {self._get_rank_title(level)}
{bar} {progress_percent:.0f}%
💎 {xp} XP ({xp_to_next} to Level {level + 1})

📊 **Stats:**
✅ Tasks Completed: {data['total_tasks_completed']}
🔥 Current Streak: {data['current_streak']} days
🏆 Longest Streak: {data['longest_streak']} days
🎖️ Achievements: {len(data['achievements'])}/{len(self.achievements)}

{self._get_motivation_message(level, data['current_streak'])}"""
        
        return msg
    
    def _get_rank_title(self, level):
        """Get rank title based on level"""
        if level == 1: return "Beginner"
        elif level < 3: return "Apprentice"
        elif level < 5: return "Practitioner"
        elif level < 8: return "Expert"
        elif level < 12: return "Master"
        elif level < 15: return "Champion"
        else: return "Legend"
    
    def _get_motivation_message(self, level, streak):
        """Get personalized motivation message"""
        if streak >= 30:
            return "💪 Unstoppable! You're a productivity machine!"
        elif streak >= 7:
            return "🔥 Amazing streak! Keep the momentum!"
        elif level >= 10:
            return "🏆 You're in the elite league now!"
        elif level >= 5:
            return "🚀 Halfway to mastery! Keep pushing!"
        else:
            return "💡 Every task gets you closer to greatness!"
    
    def get_achievements_list(self, user_id):
        """Get list of all achievements with unlock status"""
        user_id = str(user_id)
        self._init_user(user_id)
        
        data = self.user_data[user_id]
        unlocked = data['achievements']
        
        msg = "🏆 **Achievements**\n\n"
        
        # Group achievements
        categories = {
            'Milestones': ['first_task', 'tasks_10', 'tasks_50', 'tasks_100', 'tasks_500'],
            'Streaks': ['streak_7', 'streak_30', 'streak_100'],
            'Time-Based': ['early_bird', 'night_owl', 'speed_demon'],
            'Special': ['perfect_day', 'pomodoro_master', 'focus_warrior']
        }
        
        for category, achievement_ids in categories.items():
            msg += f"**{category}:**\n"
            for ach_id in achievement_ids:
                if ach_id in self.achievements:
                    ach = self.achievements[ach_id]
                    status = "✅" if ach_id in unlocked else "🔒"
                    msg += f"{status} {ach['name']} - {ach['description']} (+{ach['xp']} XP)\n"
            msg += "\n"
        
        unlocked_count = len(unlocked)
        total_count = len(self.achievements)
        msg += f"📊 Progress: {unlocked_count}/{total_count} unlocked ({unlocked_count/total_count*100:.0f}%)"
        
        return msg
    
    def get_leaderboard_entry(self, user_id, username="Unknown"):
        """Get user's leaderboard entry data"""
        user_id = str(user_id)
        self._init_user(user_id)
        
        data = self.user_data[user_id]
        return {
            'user_id': user_id,
            'username': username,
            'level': data['level'],
            'xp': data['xp'],
            'tasks_completed': data['total_tasks_completed'],
            'current_streak': data['current_streak'],
            'achievements': len(data['achievements'])
        }
