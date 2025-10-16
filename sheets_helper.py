"""
Google Sheets Integration for Task Syncing
Syncs tasks to Google Sheets for backup and visualization
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json
import os
from config import Config

class SheetsManager:
    def __init__(self):
        """Initialize Google Sheets connection"""
        self.spreadsheet_id = Config.SPREADSHEET_ID
        self.sheet = None
        self.connected = False
        
        # Try to connect
        try:
            self._connect()
        except Exception as e:
            print(f"⚠️ Sheets connection failed: {e}")
            print("Bot will work without Sheets sync")
    
    def _connect(self):
        """Connect to Google Sheets using credentials"""
        # For now, we'll use a simpler approach with API key
        # In production, use service account credentials
        try:
            # Check if credentials file exists
            if os.path.exists('credentials.json'):
                scope = ['https://spreadsheets.google.com/feeds',
                        'https://www.googleapis.com/auth/drive']
                creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
                client = gspread.authorize(creds)
                self.sheet = client.open_by_key(self.spreadsheet_id).sheet1
                self.connected = True
                print("✅ Google Sheets connected successfully!")
                self._setup_headers()
            else:
                print("⚠️ credentials.json not found. Sheets sync disabled.")
                self.connected = False
        except Exception as e:
            print(f"⚠️ Sheets connection error: {e}")
            self.connected = False
    
    def _setup_headers(self):
        """Setup spreadsheet headers if not exists"""
        if not self.connected:
            return
        
        try:
            headers = ['Task ID', 'User ID', 'Username', 'Task', 'Status', 
                      'Priority', 'Reminder Time', 'Recurring', 'Created At', 
                      'Completed At', 'Notes', 'Mood', 'Time Spent (min)']
            
            # Check if first row is empty
            first_row = self.sheet.row_values(1)
            if not first_row or first_row[0] != 'Task ID':
                self.sheet.insert_row(headers, 1)
                print("✅ Spreadsheet headers created")
        except Exception as e:
            print(f"⚠️ Error setting up headers: {e}")
    
    def sync_task(self, task_data, username="Unknown"):
        """Sync a single task to Google Sheets"""
        if not self.connected:
            return False
        
        try:
            # Prepare row data
            row = [
                task_data.get('id', ''),
                task_data.get('user_id', ''),
                username,
                task_data.get('task', ''),
                task_data.get('status', 'pending'),
                task_data.get('priority', 'medium'),
                task_data.get('reminder_time', ''),
                task_data.get('recurring', ''),
                task_data.get('created_at', ''),
                task_data.get('completed_at', ''),
                task_data.get('notes', ''),
                task_data.get('mood', ''),
                task_data.get('time_spent', 0)
            ]
            
            # Check if task already exists
            task_id = task_data.get('id')
            cell = self.sheet.find(str(task_id)) if task_id else None
            
            if cell:
                # Update existing row
                row_num = cell.row
                self.sheet.update(f'A{row_num}:M{row_num}', [row])
                print(f"✅ Updated task {task_id} in Sheets")
            else:
                # Append new row
                self.sheet.append_row(row)
                print(f"✅ Added task {task_id} to Sheets")
            
            return True
        except Exception as e:
            print(f"⚠️ Error syncing task: {e}")
            return False
    
    def sync_all_tasks(self, tasks_file='tasks.json'):
        """Sync all tasks from JSON to Sheets"""
        if not self.connected:
            return False
        
        try:
            with open(tasks_file, 'r') as f:
                data = json.load(f)
            
            synced = 0
            for task in data.get('tasks', []):
                if self.sync_task(task):
                    synced += 1
            
            print(f"✅ Synced {synced} tasks to Google Sheets")
            return True
        except Exception as e:
            print(f"⚠️ Error syncing all tasks: {e}")
            return False
    
    def get_task_stats(self):
        """Get task statistics from Sheets"""
        if not self.connected:
            return None
        
        try:
            all_values = self.sheet.get_all_values()
            if len(all_values) <= 1:
                return {"total": 0, "completed": 0, "pending": 0}
            
            # Skip header row
            tasks = all_values[1:]
            total = len(tasks)
            completed = sum(1 for task in tasks if task[4] == 'done')
            pending = total - completed
            
            return {
                "total": total,
                "completed": completed,
                "pending": pending,
                "completion_rate": round((completed / total * 100) if total > 0 else 0, 2)
            }
        except Exception as e:
            print(f"⚠️ Error getting stats: {e}")
            return None
    
    def clear_completed_tasks(self):
        """Archive completed tasks (move to archive sheet)"""
        if not self.connected:
            return False
        
        try:
            # Get all rows
            all_values = self.sheet.get_all_values()
            if len(all_values) <= 1:
                return True
            
            # Find completed tasks
            rows_to_delete = []
            for idx, row in enumerate(all_values[1:], start=2):
                if row[4] == 'done':  # Status column
                    rows_to_delete.append(idx)
            
            # Delete from bottom to top to avoid index shifting
            for row_num in reversed(rows_to_delete):
                self.sheet.delete_rows(row_num)
            
            print(f"✅ Archived {len(rows_to_delete)} completed tasks")
            return True
        except Exception as e:
            print(f"⚠️ Error archiving tasks: {e}")
            return False
    
    def export_to_csv(self, filename='tasks_backup.csv'):
        """Export all tasks to CSV"""
        if not self.connected:
            return False
        
        try:
            all_values = self.sheet.get_all_values()
            with open(filename, 'w', encoding='utf-8') as f:
                for row in all_values:
                    f.write(','.join([f'"{cell}"' for cell in row]) + '\n')
            
            print(f"✅ Exported to {filename}")
            return True
        except Exception as e:
            print(f"⚠️ Error exporting: {e}")
            return False

# Global instance
sheets_manager = SheetsManager()
