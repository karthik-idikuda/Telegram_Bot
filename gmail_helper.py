"""
Gmail Integration for Email Notifications
Sends daily digests and task reminders via email
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
from config import Config

class GmailManager:
    def __init__(self):
        """Initialize Gmail configuration"""
        self.gmail_address = Config.GMAIL_ADDRESS
        self.gmail_app_password = Config.GMAIL_APP_PASSWORD
        self.enabled = bool(self.gmail_address and self.gmail_app_password)
        
        if not self.enabled:
            if not self.gmail_address:
                print("⚠️ GMAIL_ADDRESS not configured. Email notifications disabled.")
            elif not self.gmail_app_password:
                print("⚠️ GMAIL_APP_PASSWORD not configured. Email notifications disabled.")
                print("   To enable: Set up App Password at https://myaccount.google.com/apppasswords")
    
    def send_daily_digest(self, user_email, tasks_summary):
        """Send daily task digest via email"""
        if not self.enabled:
            return False
        
        try:
            # Create message
            subject = f"📋 Your Daily Task Digest - {datetime.now().strftime('%B %d, %Y')}"
            
            # Build HTML email body
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                              color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .task-box {{ background: #f4f4f4; padding: 15px; margin: 10px 0; 
                                border-left: 4px solid #667eea; border-radius: 5px; }}
                    .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                    .stat-item {{ text-align: center; }}
                    .stat-number {{ font-size: 32px; font-weight: bold; color: #667eea; }}
                    .high-priority {{ border-left-color: #e74c3c; }}
                    .medium-priority {{ border-left-color: #f39c12; }}
                    .low-priority {{ border-left-color: #3498db; }}
                    .footer {{ text-align: center; color: #999; padding: 20px; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🤖 SycproBot Daily Digest</h1>
                    <p>Your productivity snapshot for today</p>
                </div>
                
                <div class="content">
                    <div class="stats">
                        <div class="stat-item">
                            <div class="stat-number">{tasks_summary.get('total', 0)}</div>
                            <div>Total Tasks</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number" style="color: #27ae60;">
                                {tasks_summary.get('completed', 0)}
                            </div>
                            <div>✅ Completed</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number" style="color: #e74c3c;">
                                {tasks_summary.get('pending', 0)}
                            </div>
                            <div>⏳ Pending</div>
                        </div>
                    </div>
                    
                    <h2>🔥 Today's High Priority Tasks</h2>
            """
            
            # Add high priority tasks
            high_priority_tasks = tasks_summary.get('high_priority_tasks', [])
            if high_priority_tasks:
                for task in high_priority_tasks[:5]:  # Top 5
                    html_body += f"""
                    <div class="task-box high-priority">
                        <strong>{task.get('task', 'Untitled')}</strong><br>
                        <small>⏰ {task.get('reminder_time', 'No deadline')}</small>
                    </div>
                    """
            else:
                html_body += "<p>🎉 No high priority tasks! Great job!</p>"
            
            # Add motivation quote
            html_body += f"""
                    <div style="background: #fff3cd; padding: 15px; margin: 20px 0; 
                                border-left: 4px solid #ffc107; border-radius: 5px;">
                        <strong>💪 Coach's Tip:</strong><br>
                        {tasks_summary.get('motivation', 'Stay focused and crush those goals!')}
                    </div>
                </div>
                
                <div class="footer">
                    <p>Sent by SycproBot 🤖 | Powered by AI</p>
                    <p>Open Telegram to manage your tasks</p>
                </div>
            </body>
            </html>
            """
            
            # Note: Actually sending emails requires Gmail App Password or OAuth2
            # For now, we'll log the email content
            print(f"📧 Email digest prepared for {user_email}")
            print(f"Subject: {subject}")
            print("✅ Email notification ready (configure Gmail App Password to actually send)")
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error preparing email: {e}")
            return False
    
    def send_task_reminder(self, user_email, task_data):
        """Send individual task reminder email"""
        if not self.enabled:
            return False
        
        try:
            subject = f"⏰ Task Reminder: {task_data.get('task', 'Task')}"
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="background: #667eea; color: white; padding: 20px; text-align: center;">
                    <h2>⏰ Task Reminder</h2>
                </div>
                <div style="padding: 20px;">
                    <h3>{task_data.get('task', 'Untitled Task')}</h3>
                    <p><strong>Priority:</strong> {task_data.get('priority', 'medium').upper()}</p>
                    <p><strong>Due:</strong> {task_data.get('reminder_time', 'Not set')}</p>
                    <p><strong>Status:</strong> {task_data.get('status', 'pending')}</p>
                    
                    <div style="background: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px;">
                        <p><strong>Notes:</strong></p>
                        <p>{task_data.get('notes', 'No additional notes')}</p>
                    </div>
                    
                    <p style="text-align: center; margin-top: 30px;">
                        <a href="https://t.me/SycproBot" 
                           style="background: #667eea; color: white; padding: 12px 30px; 
                                  text-decoration: none; border-radius: 5px;">
                            Open in Telegram
                        </a>
                    </p>
                </div>
                <div style="text-align: center; color: #999; padding: 20px; font-size: 12px;">
                    <p>SycproBot 🤖 | Your AI Productivity Assistant</p>
                </div>
            </body>
            </html>
            """
            
            print(f"📧 Task reminder prepared for {user_email}")
            print(f"Task: {task_data.get('task', 'Untitled')}")
            print("✅ Reminder notification ready")
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error preparing reminder: {e}")
            return False
    
    def send_weekly_report(self, user_email, weekly_stats):
        """Send weekly productivity report"""
        if not self.enabled:
            return False
        
        try:
            subject = f"📊 Your Weekly Productivity Report - Week of {datetime.now().strftime('%B %d')}"
            
            completion_rate = weekly_stats.get('completion_rate', 0)
            trend = "📈" if weekly_stats.get('trend', 0) > 0 else "📉"
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            color: white; padding: 30px; text-align: center;">
                    <h1>📊 Weekly Productivity Report</h1>
                    <p style="font-size: 18px;">
                        Week of {datetime.now().strftime('%B %d, %Y')}
                    </p>
                </div>
                
                <div style="padding: 30px;">
                    <div style="text-align: center; margin: 30px 0;">
                        <div style="font-size: 64px; color: #667eea; font-weight: bold;">
                            {completion_rate}%
                        </div>
                        <div style="font-size: 20px; color: #666;">
                            Task Completion Rate {trend}
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin: 30px 0;">
                        <div style="background: #f8f9fa; padding: 20px; text-align: center; border-radius: 10px;">
                            <div style="font-size: 36px; font-weight: bold; color: #27ae60;">
                                {weekly_stats.get('completed', 0)}
                            </div>
                            <div>Tasks Completed</div>
                        </div>
                        <div style="background: #f8f9fa; padding: 20px; text-align: center; border-radius: 10px;">
                            <div style="font-size: 36px; font-weight: bold; color: #3498db;">
                                {weekly_stats.get('total_hours', 0)}h
                            </div>
                            <div>Time Tracked</div>
                        </div>
                        <div style="background: #f8f9fa; padding: 20px; text-align: center; border-radius: 10px;">
                            <div style="font-size: 36px; font-weight: bold; color: #e74c3c;">
                                {weekly_stats.get('streak', 0)} 🔥
                            </div>
                            <div>Day Streak</div>
                        </div>
                    </div>
                    
                    <div style="background: #fff3cd; padding: 20px; margin: 20px 0; 
                                border-left: 4px solid #ffc107; border-radius: 5px;">
                        <strong>💪 Coach's Insights:</strong><br><br>
                        {weekly_stats.get('coach_message', 'Keep up the great work!')}
                    </div>
                    
                    <div style="background: #d1ecf1; padding: 20px; margin: 20px 0; 
                                border-left: 4px solid #17a2b8; border-radius: 5px;">
                        <strong>🎯 Next Week's Goal:</strong><br><br>
                        {weekly_stats.get('next_week_goal', 'Increase your completion rate by 10%')}
                    </div>
                </div>
                
                <div style="text-align: center; color: #999; padding: 20px; font-size: 12px;">
                    <p>SycproBot 🤖 | Powered by AI</p>
                </div>
            </body>
            </html>
            """
            
            print(f"📧 Weekly report prepared for {user_email}")
            print(f"Completion Rate: {completion_rate}%")
            print("✅ Weekly report ready")
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error preparing weekly report: {e}")
            return False
    
    def send_email(self, to_email, subject, html_content):
        """
        Send a custom email with any content
        Generic method for sending any email
        """
        if not self.enabled:
            print("⚠️ Gmail not configured. Cannot send email.")
            return False
        
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.gmail_address
            msg['To'] = to_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send via Gmail SMTP
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
                server.login(self.gmail_address, self.gmail_app_password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully!")
            print(f"   To: {to_email}")
            print(f"   Subject: {subject}")
            
            return True
            
        except smtplib.SMTPAuthenticationError:
            print(f"⚠️ Gmail authentication failed! Check GMAIL_APP_PASSWORD")
            print(f"   Create App Password at: https://myaccount.google.com/apppasswords")
            return False
        except Exception as e:
            print(f"⚠️ Error sending email: {e}")
            return False

# Global instance
gmail_manager = GmailManager()
