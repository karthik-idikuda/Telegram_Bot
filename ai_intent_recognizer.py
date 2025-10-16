"""
AI Intent Recognition System
Understands natural language and performs actions automatically
No commands needed - just talk naturally!
"""
import re
from datetime import datetime, timedelta
import json
from gpt_helper import GPTHelper

class AIIntentRecognizer:
    def __init__(self):
        self.gpt = GPTHelper()
        
        # Intent patterns (backup if GPT fails)
        self.intent_patterns = {
            'add_task': [
                r'(?:add|create|make|set|new)\s+(?:a\s+)?task',
                r'remind\s+me\s+(?:to|about)',
                r'i\s+need\s+to',
                r'don\'?t\s+forget',
                r'schedule',
                r'todo',
            ],
            'set_reminder': [
                r'set\s+(?:a\s+)?reminder',
                r'remind\s+me\s+in',
                r'alert\s+me\s+in',
                r'notify\s+me\s+in',
            ],
            'send_email': [
                r'send\s+(?:an?\s+)?(?:email|mail)',
                r'email\s+me',
                r'mail\s+me',
            ],
            'list_tasks': [
                r'(?:show|list|view|what(?:\'?s)?|get)\s+(?:my\s+)?tasks',
                r'what\s+do\s+i\s+have',
                r'my\s+(?:to\s*do|todo)',
            ],
            'complete_task': [
                r'(?:mark|set|done|complete|finish|completed)',
                r'i\s+(?:did|finished|completed)',
            ],
            'get_stats': [
                r'(?:show|get|view)\s+(?:my\s+)?stats',
                r'how\s+am\s+i\s+doing',
                r'my\s+progress',
            ],
        }
    
    def analyze_intent(self, message_text):
        """
        Use pattern matching FIRST (fast & reliable), then GPT if needed
        Returns: {
            'intent': 'add_task' | 'set_reminder' | 'send_email' | etc,
            'parameters': {...},
            'confidence': 0.0-1.0
        }
        """
        
        print(f"🔍 Analyzing message: '{message_text}'")
        
        # 🚀 FIRST: Try pattern-based detection (fast, no API calls!)
        pattern_result = self._fallback_intent_detection(message_text)
        
        print(f"📊 Pattern detection result: {pattern_result['intent']} (confidence: {pattern_result['confidence']})")
        
        # If we got a good match (not general_chat), use it immediately!
        if pattern_result['intent'] != 'general_chat' and pattern_result['confidence'] >= 0.7:
            print(f"✅ Using pattern-based detection: {pattern_result['intent']}")
            return pattern_result
        
        print(f"⚠️ Pattern failed, trying GPT...")
        
        # SECOND: Only use GPT for complex cases or general chat
        # This saves API calls and avoids rate limits!
        prompt = f"""Analyze this user message and extract the intent and parameters.

User message: "{message_text}"

Return ONLY a JSON object with this exact structure:
{{
    "intent": "add_task|set_reminder|send_email|list_tasks|complete_task|get_stats|general_chat",
    "parameters": {{
        "task_name": "extracted task description (if applicable)",
        "time_amount": number (if time mentioned, e.g., "1 min" = 1),
        "time_unit": "minutes|hours|days|weeks" (if time mentioned),
        "reminder_time": "extracted datetime string (if specific time mentioned)",
        "email_recipient": "email address (if mentioned)",
        "email_subject": "subject (if mentioned)",
        "email_content": "message content (if mentioned)",
        "priority": "high|medium|low" (if urgency indicated),
        "task_id": number (if user references a specific task number)
    }},
    "confidence": 0.9,
    "natural_response": "friendly confirmation message"
}}

Examples:
- "set a reminder for 1 min" → {{"intent": "set_reminder", "parameters": {{"time_amount": 1, "time_unit": "minutes"}}, "confidence": 0.95}}
- "send hi in mail" → {{"intent": "send_email", "parameters": {{"email_content": "hi"}}, "confidence": 0.90}}
- "remind me to call mom tomorrow at 3pm" → {{"intent": "add_task", "parameters": {{"task_name": "call mom", "reminder_time": "tomorrow at 3pm"}}, "confidence": 0.95}}
- "mark task 1 as done" → {{"intent": "complete_task", "parameters": {{"task_id": 1}}, "confidence": 0.95}}

IMPORTANT: Return ONLY the JSON, nothing else."""

        try:
            # Get GPT response (don't use max_tokens as ask_gpt doesn't support it)
            gpt_response = self.gpt.ask_gpt(prompt)
            
            # Try to parse JSON from response
            # Sometimes GPT adds extra text, so extract JSON
            json_match = re.search(r'\{.*\}', gpt_response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                # Fallback to pattern matching
                return self._fallback_intent_detection(message_text)
                
        except Exception as e:
            print(f"⚠️ GPT intent analysis failed: {e}")
            return self._fallback_intent_detection(message_text)
    
    def _fallback_intent_detection(self, message_text):
        """Fallback pattern-based intent detection (works without GPT!)"""
        message_lower = message_text.lower()
        
        # EMAIL DETECTION (improved for "send hi in mail", "send email", etc.)
        if any(word in message_lower for word in ['email', 'mail', 'send']):
            # Extract what to send
            email_content = message_text
            # Remove trigger words to get just the content
            for trigger in ['send', 'email', 'mail', 'in', 'to', 'me', 'an', 'a']:
                email_content = re.sub(rf'\b{trigger}\b', '', email_content, flags=re.IGNORECASE)
            email_content = email_content.strip()
            
            return {
                'intent': 'send_email',
                'parameters': {
                    'email_content': email_content if email_content else 'Hello from SycproBot!',
                    'email_subject': 'Message from Telegram'
                },
                'confidence': 0.85,
                'natural_response': f"Sending email with message: {email_content}"
            }
        
        # REMINDER DETECTION (improved for "set reminder for X")
        if re.search(r'(set|create|make).*reminder', message_lower):
            time_match = re.search(r'(\d+)\s*(min(?:ute)?s?|hour?s?|days?|weeks?)', message_text, re.IGNORECASE)
            if time_match:
                return {
                    'intent': 'set_reminder',
                    'parameters': self._extract_basic_parameters(message_text, 'set_reminder'),
                    'confidence': 0.9,
                    'natural_response': 'Setting up your reminder!'
                }
        
        # Check each intent pattern
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    return {
                        'intent': intent,
                        'parameters': self._extract_basic_parameters(message_text, intent),
                        'confidence': 0.7,
                        'natural_response': f"I detected you want to {intent.replace('_', ' ')}!"
                    }
        
        # Default to general chat
        return {
            'intent': 'general_chat',
            'parameters': {},
            'confidence': 0.5,
            'natural_response': None
        }
    
    def _extract_basic_parameters(self, message_text, intent):
        """Extract basic parameters using regex"""
        params = {}
        
        # Extract time amounts (e.g., "1 min", "5 hours", "2 days")
        time_match = re.search(r'(\d+)\s*(min(?:ute)?s?|hour?s?|days?|weeks?)', message_text, re.IGNORECASE)
        if time_match:
            params['time_amount'] = int(time_match.group(1))
            unit = time_match.group(2).lower()
            if 'min' in unit:
                params['time_unit'] = 'minutes'
            elif 'hour' in unit:
                params['time_unit'] = 'hours'
            elif 'day' in unit:
                params['time_unit'] = 'days'
            elif 'week' in unit:
                params['time_unit'] = 'weeks'
        
        # Extract task ID (e.g., "task 1", "task #3")
        task_id_match = re.search(r'task\s*#?(\d+)', message_text, re.IGNORECASE)
        if task_id_match:
            params['task_id'] = int(task_id_match.group(1))
        
        # Extract priority keywords
        if re.search(r'urgent|asap|important|critical|high\s+priority', message_text, re.IGNORECASE):
            params['priority'] = 'high'
        elif re.search(r'low\s+priority|whenever|someday|maybe', message_text, re.IGNORECASE):
            params['priority'] = 'low'
        else:
            params['priority'] = 'medium'
        
        return params
    
    def calculate_reminder_time(self, time_amount, time_unit):
        """Calculate exact reminder datetime from relative time"""
        now = datetime.now()
        
        if time_unit == 'minutes':
            reminder_time = now + timedelta(minutes=time_amount)
        elif time_unit == 'hours':
            reminder_time = now + timedelta(hours=time_amount)
        elif time_unit == 'days':
            reminder_time = now + timedelta(days=time_amount)
        elif time_unit == 'weeks':
            reminder_time = now + timedelta(weeks=time_amount)
        elif time_unit == 'seconds':
            reminder_time = now + timedelta(seconds=time_amount)
        else:
            reminder_time = now + timedelta(minutes=time_amount)  # Default to minutes
        
        # Return ISO format for proper datetime parsing
        return reminder_time.isoformat()

# Global instance
ai_intent = AIIntentRecognizer()
