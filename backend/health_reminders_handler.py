from db_connection import get_db
from datetime import datetime, timedelta

class HealthRemindersHandler:
    @staticmethod
    def get_post_care_instructions(user_id, procedure_name=None):
        conn = get_db()
        cursor = conn.cursor()
        
        if procedure_name:
            cursor.execute("""
                SELECT * FROM post_care_instructions 
                WHERE user_id = ? AND procedure_name = ?
                ORDER BY created_at DESC
            """, (user_id, procedure_name))
        else:
            cursor.execute("""
                SELECT * FROM post_care_instructions 
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
            
        instructions = cursor.fetchall()
        conn.close()
        return instructions

    @staticmethod
    def get_health_advice(category=None):
        conn = get_db()
        cursor = conn.cursor()
        
        if category:
            cursor.execute("SELECT * FROM health_advice WHERE category = ?", (category,))
        else:
            cursor.execute("SELECT * FROM health_advice")
            
        advice = cursor.fetchall()
        conn.close()
        return advice

    @staticmethod
    def get_upcoming_events():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM health_events 
            WHERE event_date >= date('now')
            ORDER BY event_date ASC
        """)
        events = cursor.fetchall()
        conn.close()
        return events

    @staticmethod
    def set_reminder(user_id, reminder_type, message, reminder_date, is_recurring=False, recurrence_pattern=None):
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO health_reminders 
            (user_id, reminder_type, reminder_message, reminder_date, is_recurring, recurrence_pattern)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, reminder_type, message, reminder_date, is_recurring, recurrence_pattern))
        
        reminder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return reminder_id

    @staticmethod
    def get_user_reminders(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM health_reminders 
            WHERE user_id = ? AND reminder_date >= date('now')
            ORDER BY reminder_date ASC
        """, (user_id,))
        reminders = cursor.fetchall()
        conn.close()
        return reminders

    @staticmethod
    def update_post_care_instructions(user_id, procedure_name, instructions, side_effects=None, follow_up_date=None):
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO post_care_instructions 
            (user_id, procedure_name, instructions, side_effects, follow_up_date)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, procedure_name, instructions, side_effects, follow_up_date))
        
        instruction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return instruction_id 