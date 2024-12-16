from db_connection import get_db
from datetime import datetime

class PaymentHandler:
    @staticmethod
    def get_outstanding_bills(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.*, a.appointment_date, a.doctor_name 
            FROM bills b
            JOIN appointments a ON b.appointment_id = a.id
            WHERE b.user_id = ? AND b.paid = 0
            ORDER BY b.due_date ASC
        """, (user_id,))
        bills = cursor.fetchall()
        conn.close()
        return bills

    @staticmethod
    def process_payment(bill_id, payment_amount, payment_method):
        conn = get_db()
        cursor = conn.cursor()
        
        # Get bill details
        cursor.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
        bill = cursor.fetchone()
        
        if bill and payment_amount >= bill['amount']:
            # Update bill status
            cursor.execute("""
                UPDATE bills 
                SET paid = 1,
                    payment_date = CURRENT_TIMESTAMP,
                    payment_method = ?
                WHERE id = ?
            """, (payment_method, bill_id))
            
            # Record payment transaction
            cursor.execute("""
                INSERT INTO payment_transactions 
                (bill_id, amount, payment_method, status)
                VALUES (?, ?, ?, 'completed')
            """, (bill_id, payment_amount, payment_method))
            
            conn.commit()
            conn.close()
            return True
        return False

    @staticmethod
    def get_payment_plans(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM payment_plans 
            WHERE user_id = ?
        """, (user_id,))
        plans = cursor.fetchall()
        conn.close()
        return plans

    @staticmethod
    def setup_payment_plan(user_id, bill_id, installments):
        conn = get_db()
        cursor = conn.cursor()
        
        # Get bill details
        cursor.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
        bill = cursor.fetchone()
        
        if bill:
            monthly_amount = bill['amount'] / installments
            
            # Create payment plan
            cursor.execute("""
                INSERT INTO payment_plans 
                (user_id, bill_id, total_amount, monthly_amount, remaining_installments)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, bill_id, bill['amount'], monthly_amount, installments))
            
            plan_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return plan_id
        return None

    @staticmethod
    def generate_payment_receipt(payment_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pt.*, b.amount as bill_amount, u.email 
            FROM payment_transactions pt
            JOIN bills b ON pt.bill_id = b.id
            JOIN users u ON b.user_id = u.id
            WHERE pt.id = ?
        """, (payment_id,))
        payment_details = cursor.fetchone()
        conn.close()
        
        if payment_details:
            receipt = {
                'transaction_id': payment_id,
                'date': payment_details['created_at'],
                'amount_paid': payment_details['amount'],
                'payment_method': payment_details['payment_method'],
                'bill_amount': payment_details['bill_amount'],
                'email': payment_details['email']
            }
            return receipt
        return None
