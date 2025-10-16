"""
Theme and Personality Manager
Customizes bot responses based on user preferences
"""
import random
from config import config

class PersonalityManager:
    def __init__(self):
        self.current_personality = config.BOT_PERSONALITY
        
        # Different personality styles
        self.personalities = {
            'professional': {
                'greeting': [
                    "Good day! Ready to maximize your productivity?",
                    "Hello! Let's accomplish great things today.",
                    "Welcome back! Time to tackle your goals."
                ],
                'task_added': [
                    "Task recorded successfully.",
                    "Added to your schedule.",
                    "Task has been logged."
                ],
                'task_completed': [
                    "Excellent work. Task completed.",
                    "Well done. Progress noted.",
                    "Task successfully completed."
                ],
                'motivation': [
                    "Consistent effort yields results.",
                    "Stay focused on your objectives.",
                    "Progress is the result of persistent action."
                ],
                'reminder': [
                    "Reminder: You have pending tasks.",
                    "Please review your task list.",
                    "Don't forget your scheduled items."
                ]
            },
            
            'coach': {
                'greeting': [
                    "Let's GO, champion! Ready to CRUSH today? 💪",
                    "Rise and GRIND! Time to dominate! 🔥",
                    "Welcome back, WARRIOR! Let's conquer this! 🚀",
                    "BEAST MODE ACTIVATED! What are we tackling first? ⚡"
                ],
                'task_added': [
                    "LOCKED IN! Let's destroy this task! 💥",
                    "Added! Now let's GO GET IT! 🎯",
                    "ON THE LIST! Time to show what you're made of! 💪",
                    "REGISTERED! You're building something GREAT! 🏆"
                ],
                'task_completed': [
                    "BOOM! 💥 That's what I'm talking about! LEGEND!",
                    "🔥 UNSTOPPABLE! You're on FIRE today!",
                    "💪 CRUSHING IT! That's champion mentality right there!",
                    "⚡ ELITE PERFORMANCE! Keep this energy going!",
                    "🏆 YES! Another WIN! You're building momentum!"
                ],
                'motivation': [
                    "🔥 Pain is temporary, PRIDE is FOREVER! Keep pushing!",
                    "💪 Every task completed is a REP for your success muscle!",
                    "⚡ You didn't come this far to ONLY come this far! GO!",
                    "🎯 Champions are made when nobody's watching! LET'S GO!",
                    "🚀 The only bad workout is the one you didn't do! ATTACK!"
                ],
                'reminder': [
                    "⏰ TIME TO EXECUTE! You've got tasks waiting for that CHAMPION energy!",
                    "🔔 Your future self is COUNTING on you! Let's move!",
                    "💥 Reminder: Greatness doesn't build itself! Get after it!",
                    "⚡ You promised yourself you'd do this! TIME TO DELIVER!"
                ],
                'streak': [
                    "🔥 {days} DAY STREAK! You're an ABSOLUTE MACHINE! Don't stop now!",
                    "💪 {days} DAYS STRONG! This is what DEDICATION looks like!",
                    "⚡ {days} DAY STREAK! You're in BEAST MODE! Keep dominating!"
                ],
                'level_up': [
                    "🎊 LEVEL UP! You just leveled up to {level}! UNSTOPPABLE! 🚀",
                    "💥 NEW LEVEL UNLOCKED: {level}! You're becoming LEGENDARY!",
                    "🏆 LEVEL {level} ACHIEVED! Your grind is paying off, CHAMPION!"
                ],
                'encouragement': [
                    "💭 Feeling tired? That's your body getting STRONGER! Push through!",
                    "🎯 Every pro was once an amateur who REFUSED to quit!",
                    "💪 You're not tired, you're TESTING your limits! Love it!",
                    "⚡ Comfort zone? We don't know her! Let's GO!"
                ]
            },
            
            'funny': {
                'greeting': [
                    "Yo yo yo! What's crackin', productivity machine? 😎",
                    "Ayyyy! The legend returns! 🎉",
                    "Well well well, look who decided to be productive! 😄"
                ],
                'task_added': [
                    "Boom! Task yoinked into the list! 📝",
                    "Roger that, captain! Task is now my problem! 🫡",
                    "Task added! Now the hard part... actually doing it 😅"
                ],
                'task_completed': [
                    "YAAAS QUEEN! 👑 Task obliterated!",
                    "💥 POW! Take that, task! You got WRECKED!",
                    "Achievement unlocked: Actually Did The Thing! 🏆",
                    "Task? More like... done-sk! (I'll see myself out 😅)"
                ],
                'motivation': [
                    "You got this! If I believe in you, and I'm just code, imagine what's possible! 🤖",
                    "Remember: You're only one task away from a good mood! 💪",
                    "Pro tip: Tasks don't complete themselves... yet. 🤷‍♂️"
                ],
                'reminder': [
                    "Psst... your tasks called. They miss you. 👀",
                    "🔔 Ding ding! The productivity train is leaving the station!",
                    "Hey you! Yeah YOU! Time to adult! 📋"
                ]
            },
            
            'zen': {
                'greeting': [
                    "🌸 Welcome back. Breathe. Let's begin.",
                    "☮️ Peace. What shall we accomplish mindfully today?",
                    "🧘 Centered and ready? Let's flow through your tasks."
                ],
                'task_added': [
                    "✨ Task gently added to your journey.",
                    "🌿 Noted. Approach it with calm intention.",
                    "📿 Added. Remember: progress, not perfection."
                ],
                'task_completed': [
                    "🌟 Beautiful. Another step on your path.",
                    "☯️ Well done. Balance maintained.",
                    "🕊️ Completed with grace. Peace."
                ],
                'motivation': [
                    "🌊 Like water flowing around rocks, persistence finds the way.",
                    "🌱 Growth happens in small, consistent steps.",
                    "🌙 Be patient with yourself. You're exactly where you need to be."
                ],
                'reminder': [
                    "🔔 Gentle reminder: Your tasks await, when you're ready.",
                    "🌸 Time to check in with your intentions.",
                    "✨ Mindful moment: Review your path forward."
                ]
            }
        }
    
    def set_personality(self, personality):
        """Set the current personality"""
        if personality in self.personalities:
            self.current_personality = personality
            return True
        return False
    
    def get_message(self, category, **kwargs):
        """Get a message based on current personality and category"""
        if self.current_personality not in self.personalities:
            self.current_personality = 'professional'
        
        personality = self.personalities[self.current_personality]
        
        if category not in personality:
            # Fallback to professional
            personality = self.personalities['professional']
        
        if category not in personality:
            return "Message unavailable"
        
        messages = personality[category]
        message = random.choice(messages)
        
        # Format with kwargs
        if kwargs:
            message = message.format(**kwargs)
        
        return message
    
    def get_greeting(self):
        """Get personalized greeting"""
        return self.get_message('greeting')
    
    def get_task_added_message(self, task_name):
        """Get message for task addition"""
        return self.get_message('task_added')
    
    def get_task_completed_message(self, task_name):
        """Get message for task completion"""
        return self.get_message('task_completed')
    
    def get_motivation(self):
        """Get motivational message"""
        return self.get_message('motivation')
    
    def get_reminder_message(self):
        """Get reminder message"""
        return self.get_message('reminder')
    
    def get_streak_message(self, days):
        """Get streak celebration message"""
        return self.get_message('streak', days=days)
    
    def get_level_up_message(self, level):
        """Get level up celebration message"""
        return self.get_message('level_up', level=level)
    
    def get_encouragement(self):
        """Get encouragement message"""
        return self.get_message('encouragement')
    
    def get_daily_motivation(self):
        """Get daily motivation message for email digest"""
        return self.get_message('motivation')
    
    def get_available_personalities(self):
        """Get list of available personalities"""
        return list(self.personalities.keys())
    
    def get_personality_description(self):
        """Get description of current personality"""
        descriptions = {
            'professional': '💼 Professional - Clear, focused, business-like communication',
            'coach': '💪 Coach - High-energy, motivational, champion mindset',
            'funny': '😄 Funny - Lighthearted, casual, with humor',
            'zen': '🧘 Zen - Calm, mindful, peaceful approach'
        }
        return descriptions.get(self.current_personality, 'Unknown personality')

# Singleton instance
personality_manager = PersonalityManager()
