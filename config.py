import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for easy access"""
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    GPT_MODEL = os.getenv('GPT_MODEL', 'openai/gpt-oss-20b:free')
    
    # OpenAI Configuration (optional)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Google APIs Configuration
    GOOGLE_SHEETS_API_KEY = os.getenv('GOOGLE_SHEETS_API_KEY')
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    GMAIL_API_KEY = os.getenv('GMAIL_API_KEY')
    GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
    GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')  # For SMTP sending
    
    # Bot Personality Configuration
    BOT_PERSONALITY = os.getenv('BOT_PERSONALITY', 'coach').lower()
    BOT_THEME = os.getenv('BOT_THEME', 'professional').lower()
    
    # Schedule Configuration
    DAILY_REMINDER_TIME = os.getenv('DAILY_REMINDER_TIME', '08:00')
    TIMEZONE = os.getenv('TIMEZONE', 'UTC')
    
    @staticmethod
    def validate_config():
        """Validate that all required configuration variables are set"""
        required_vars = {
            'TELEGRAM_BOT_TOKEN': Config.TELEGRAM_BOT_TOKEN,
            'OPENROUTER_API_KEY': Config.OPENROUTER_API_KEY,
        }
        
        missing = [key for key, value in required_vars.items() if not value]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True

# Create singleton instance
config = Config()

# Legacy compatibility
TELEGRAM_BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
OPENROUTER_API_KEY = config.OPENROUTER_API_KEY
GPT_MODEL = config.GPT_MODEL
GOOGLE_SHEETS_API_KEY = config.GOOGLE_SHEETS_API_KEY
SPREADSHEET_ID = config.SPREADSHEET_ID
DAILY_REMINDER_TIME = config.DAILY_REMINDER_TIME
TIMEZONE = config.TIMEZONE

def validate_config():
    """Legacy function for validation"""
    return Config.validate_config()
