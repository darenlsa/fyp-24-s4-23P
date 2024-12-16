from db_connection import get_db

def schedule_notification(user_id, reminder_type, reminder_message, reminder_date):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reminders (user_id, reminder_type, reminder_message, reminder_date) VALUES (?, ?, ?, ?)",
                   (user_id, reminder_type, reminder_message, reminder_date))
    conn.commit()
    conn.close()
