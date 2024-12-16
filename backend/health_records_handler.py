from db_connection import get_db
from datetime import datetime

class HealthRecordsHandler:
    @staticmethod
    def view_lab_results(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM lab_results 
            WHERE user_id = ? 
            ORDER BY result_date DESC
        """, (user_id,))
        results = cursor.fetchall()
        conn.close()
        return results

    @staticmethod
    def get_health_record_summary(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM health_records 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 10
        """, (user_id,))
        records = cursor.fetchall()
        conn.close()
        return records

    @staticmethod
    def request_record_copy(user_id, format_type='digital'):
        conn = get_db()
        cursor = conn.cursor()
        
        # Create a record request
        cursor.execute("""
            INSERT INTO record_requests (user_id, format_type, status)
            VALUES (?, ?, 'processing')
        """, (user_id, format_type))
        
        request_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return request_id

    @staticmethod
    def update_personal_info(user_id, updated_info):
        conn = get_db()
        cursor = conn.cursor()
        
        # Update user information
        cursor.execute("""
            UPDATE users 
            SET email = ?,
                phone = ?,
                address = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (updated_info.get('email'), 
              updated_info.get('phone'),
              updated_info.get('address'),
              user_id))
        
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_health_history(user_id, record_type=None):
        conn = get_db()
        cursor = conn.cursor()
        
        if record_type:
            cursor.execute("""
                SELECT * FROM health_records 
                WHERE user_id = ? AND record_type = ?
                ORDER BY created_at DESC
            """, (user_id, record_type))
        else:
            cursor.execute("""
                SELECT * FROM health_records 
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
            
        records = cursor.fetchall()
        conn.close()
        return records

    @staticmethod
    def notify_record_update(user_id, record_type, message):
        conn = get_db()
        cursor = conn.cursor()
        
        # Create notification for the user
        cursor.execute("""
            INSERT INTO reminders (user_id, reminder_type, reminder_message, reminder_date)
            VALUES (?, 'record_update', ?, CURRENT_TIMESTAMP)
        """, (user_id, message))
        
        conn.commit()
        conn.close()
        return True 