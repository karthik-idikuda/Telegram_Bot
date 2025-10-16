#!/usr/bin/env python3
"""
Enhanced bot startup with automatic notification
Sends you a message when bot is ready!
"""
import logging
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import asyncio
from config import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def send_startup_notification(application):
    """Send notification when bot starts"""
    try:
        bot = application.bot
        me = await bot.get_me()
        
        # Get recent updates to find your chat ID
        updates = await bot.get_updates(limit=10, offset=-1)
        
        chat_ids = set()
        for update in updates:
            if update.message:
                chat_ids.add(update.message.chat.id)
            elif update.effective_chat:
                chat_ids.add(update.effective_chat.id)
        
        startup_message = f"""
🎉 **SYCPROBOT IS LIVE!** 🎉

I'm back online and ready to help! 🤖

✅ **Status:** All systems operational
🎨 **Personality:** Coach mode ACTIVATED 💪
⚡ **Features:** 20+ advanced capabilities

**🚀 Quick Start:**
• Type `/start` for welcome
• Type `/help` for all commands
• Type `/addtask Finish homework` to begin

**💡 Pro Features:**
🧠 Smart AI task parsing
🎤 Voice-to-task conversion
📊 Analytics & insights
🎮 Gamification (XP, levels, achievements)
🍅 Pomodoro timer built-in
⏱️ Automatic time tracking
🔄 Recurring tasks
🔥 Streak tracking

**Just message me naturally - I understand everything!**

Let's CRUSH some goals today! 💪🔥
"""
        
        # Send to all recent chat IDs
        for chat_id in chat_ids:
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=startup_message,
                    parse_mode='Markdown'
                )
                logger.info(f"✅ Startup message sent to {chat_id}")
            except Exception as e:
                logger.error(f"Failed to send to {chat_id}: {e}")
        
        if not chat_ids:
            logger.warning("⚠️ No chat IDs found. Message the bot first!")
            logger.info(f"📱 Bot link: https://t.me/{me.username}")
        
    except Exception as e:
        logger.error(f"Failed to send startup notification: {e}")

async def post_init(application):
    """Called after bot starts"""
    await send_startup_notification(application)

def main():
    """Start bot with auto-notification"""
    logger.info("🚀 Starting SycproBot with auto-notification...")
    
    # Import bot setup
    from bot import main as bot_main
    
    # Run the bot
    bot_main()

if __name__ == "__main__":
    main()
