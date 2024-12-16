from db_connection import get_db
from datetime import datetime, timedelta
from notification_scheduler import schedule_notification

class PrescriptionHandler:
    @staticmethod
    def get_prescription_details(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM prescriptions WHERE user_id = ?", (user_id,))
        prescriptions = cursor.fetchall()
        conn.close()
        return prescriptions

    @staticmethod
    def request_refill(user_id, prescription_id):
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if prescription exists and is eligible for refill
        cursor.execute("SELECT * FROM prescriptions WHERE id = ? AND user_id = ?", 
                      (prescription_id, user_id))
        prescription = cursor.fetchone()
        
        if prescription:
            # Create a refill request
            cursor.execute("""
                INSERT INTO prescriptions (user_id, details, status)
                VALUES (?, ?, 'pending')
            """, (user_id, f"Refill request for prescription #{prescription_id}"))
            
            refill_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return refill_id
        return None

    @staticmethod
    def get_refill_status(refill_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM prescriptions WHERE id = ?", (refill_id,))
        status = cursor.fetchone()
        conn.close()
        return status['status'] if status else None

    @staticmethod
    def schedule_refill_reminder(user_id, prescription_id, days_before=3):
        conn = get_db()
        cursor = conn.cursor()
        
        # Get prescription details
        cursor.execute("SELECT * FROM prescriptions WHERE id = ?", (prescription_id,))
        prescription = cursor.fetchone()
        
        if prescription:
            reminder_date = datetime.now() + timedelta(days=30 - days_before)  # Assuming 30-day prescription
            reminder_message = f"Your prescription #{prescription_id} will need a refill soon."
            
            schedule_notification(
                user_id=user_id,
                reminder_type='prescription_refill',
                reminder_message=reminder_message,
                reminder_date=reminder_date
            )
            return True
        return False

    @staticmethod
    def get_medication_info(medication_name):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM medication_info 
            WHERE name LIKE ?
        """, (f"%{medication_name}%",))
        info = cursor.fetchone()
        conn.close()
        return info if info else None
