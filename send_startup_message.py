#!/usr/bin/env python3
"""
Quick script to send a startup message to you
This will notify you when the bot is ready
"""
import asyncio
from telegram import Bot
from config import config

async def send_startup_message():
    """Send a message to your Telegram when bot starts"""
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    
    # Get bot info
    me = await bot.get_me()
    print(f"✅ Bot username: @{me.username}")
    print(f"✅ Bot name: {me.first_name}")
    
    # Your user ID (we'll get it from updates)
    # First, let's get recent updates to find your chat ID
    updates = await bot.get_updates(limit=1, offset=-1)
    
    if updates:
        chat_id = updates[0].message.chat.id if updates[0].message else updates[0].effective_chat.id
        
        startup_message = f"""
🚀 **BOT IS NOW LIVE!** 🚀

Hey! I'm **{me.first_name}** (@{me.username})

✅ All systems operational
✅ Coach personality activated
✅ All 20+ features ready

**Quick Start:**
• `/start` - Get welcome message
• `/help` - See all commands
• `/addtask Buy groceries tomorrow` - Add your first task

**Pro Tips:**
💬 Just talk to me naturally!
🎤 Send voice messages to create tasks
🔥 I'll track your streaks automatically

Ready to CRUSH your goals? 💪
Let's GO! 🚀
"""
        
        await bot.send_message(
            chat_id=chat_id,
            text=startup_message,
            parse_mode='Markdown'
        )
        print(f"✅ Startup message sent to chat ID: {chat_id}")
    else:
        print("⚠️ No recent messages found. Send /start to the bot first!")
        print(f"📱 Find your bot: https://t.me/{me.username}")

if __name__ == "__main__":
    asyncio.run(send_startup_message())
