import requests
import json
from config import OPENROUTER_API_KEY, GPT_MODEL

class GPTHelper:
    """Handle all GPT-related interactions using OpenRouter"""
    
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.model = GPT_MODEL
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
    def ask_gpt(self, prompt, system_message="You are a helpful and motivating productivity assistant."):
        """
        Send a prompt to GPT and get a response
        
        Args:
            prompt (str): The user prompt
            system_message (str): The system role message
            
        Returns:
            str: GPT's response
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ]
            }
            
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            print(f"Error calling GPT: {e}")
            return "I'm having trouble thinking right now. Let me try again in a moment! 🤔"
    
    def celebrate_completion(self, task_name):
        """Generate a celebratory message for task completion"""
        prompt = f"User just completed the task: '{task_name}'. Give them a short, enthusiastic congratulation (1-2 sentences max). Be genuine and motivating."
        return self.ask_gpt(prompt)
    
    def motivate_incomplete(self, task_name):
        """Generate motivation for incomplete task"""
        prompt = f"User hasn't completed '{task_name}' yet. Give them a short, encouraging message (1-2 sentences). Be supportive and understanding."
        return self.ask_gpt(prompt)
    
    def reschedule_confirmation(self, task_name, time):
        """Confirm rescheduling with natural language"""
        prompt = f"User wants to reschedule '{task_name}' to {time}. Give a short, friendly confirmation (1 sentence)."
        return self.ask_gpt(prompt)
    
    def daily_summary(self, completed, pending, total):
        """Generate daily summary"""
        prompt = f"User completed {completed} out of {total} tasks today. {pending} are still pending. Give them a motivating summary (2-3 sentences)."
        return self.ask_gpt(prompt)
    
    def morning_greeting(self, task_count):
        """Generate morning greeting"""
        prompt = f"It's morning and the user has {task_count} tasks for today. Give a short, energetic good morning message (1-2 sentences)."
        return self.ask_gpt(prompt)
    
    def handle_user_message(self, message):
        """Handle general conversation with user"""
        prompt = f"User said: '{message}'. Respond as a productivity assistant. Keep it brief and helpful (1-2 sentences)."
        return self.ask_gpt(prompt)
