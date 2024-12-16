import sqlite3
from db_connection import get_db
from datetime import datetime, timedelta

def create_sample_data(user_id):
    """Create sample data for a new user."""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Create patient profile
        cursor.execute("""
            INSERT INTO patient_profiles (user_id, first_name, last_name, blood_type, allergies)
            VALUES (?, 'John', 'Doe', 'O+', 'None')
        """, (user_id,))

        # Create sample appointments
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        cursor.execute("""
            INSERT INTO appointments (user_id, doctor_name, appointment_date, appointment_time, appointment_type)
            VALUES 
            (?, 'Dr. Smith', ?, '14:00', 'General Checkup'),
            (?, 'Dr. Johnson', ?, '10:30', 'Follow-up')
        """, (user_id, tomorrow, user_id, next_week))

        # Create sample prescriptions
        ten_days = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
        thirty_days = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        cursor.execute("""
            INSERT INTO prescriptions (user_id, medication_name, dosage, frequency, end_date, refills_remaining)
            VALUES 
            (?, 'Amoxicillin', '500mg', 'Twice daily', ?, 2),
            (?, 'Ibuprofen', '200mg', 'As needed', ?, 1)
        """, (user_id, ten_days, user_id, thirty_days))

        # Create sample bills
        cursor.execute("""
            INSERT INTO bills (user_id, appointment_id, amount, description, status, due_date)
            VALUES 
            (?, 1, 150.00, 'General Checkup', 'PENDING', ?),
            (?, 2, 75.00, 'Follow-up Consultation', 'PENDING', ?)
        """, (user_id, thirty_days, user_id, thirty_days))

        conn.commit()
        print(f"Sample data created for user_id: {user_id}")
        return True
    except Exception as e:
        print(f"Error creating sample data: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

def register_user(username, password, email, first_name=None, last_name=None):
    """Register a new user"""
    if not username or not password or not email:
        return False, "All fields are required"
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username already exists"
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return False, "Email already exists"
        
        # Insert new user
        cursor.execute("""
            INSERT INTO users (username, password, email)
            VALUES (?, ?, ?)
        """, (username, password, email))
        
        user_id = cursor.lastrowid
        
        # Create patient profile
        cursor.execute("""
            INSERT INTO patient_profiles (
                user_id, first_name, last_name, 
                date_of_birth, gender, blood_type, 
                allergies, medical_conditions
            ) VALUES (?, ?, ?, NULL, NULL, NULL, NULL, NULL)
        """, (user_id, first_name or username, last_name or ''))
        
        conn.commit()
        conn.close()
        return True, "Registration successful"
        
    except Exception as e:
        print(f"Error in register_user: {str(e)}")
        if conn:
            conn.close()
        return False, "Registration failed"

def login_user(username, password):
    """Authenticate a user"""
    if not username or not password:
        return False, "Username and password are required"
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get user data
        cursor.execute("""
            SELECT id, username, email, status
            FROM users 
            WHERE username = ? AND password = ? AND status = 'active'
        """, (username, password))
        
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return False, "Invalid username or password"
        
        # Get profile data
        cursor.execute("""
            SELECT first_name, last_name
            FROM patient_profiles
            WHERE user_id = ?
        """, (user['id'],))
        
        profile = cursor.fetchone()
        
        # Combine user and profile data
        user_data = {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'first_name': profile['first_name'] if profile else username,
            'last_name': profile['last_name'] if profile else ''
        }
        
        conn.close()
        return True, user_data
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        if conn:
            conn.close()
        return False, "An error occurred during login"

def logout_user():
    """Logout user (handled by Flask session)."""
    pass

def update_user_profile(user_id, profile_data):
    """Update user profile information"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Update users table
        user_fields = ['username', 'email', 'phone', 'address', 'emergency_contact']
        user_updates = []
        user_values = []
        
        for field in user_fields:
            if field in profile_data:
                user_updates.append(f"{field} = ?")
                user_values.append(profile_data[field])
        
        if user_updates:
            user_values.append(user_id)
            cursor.execute(f"""
                UPDATE users 
                SET {', '.join(user_updates)}
                WHERE id = ?
            """, user_values)
        
        # Update patient_profiles table
        profile_fields = ['first_name', 'last_name', 'date_of_birth', 
                         'gender', 'blood_type', 'allergies', 'medical_conditions']
        profile_updates = []
        profile_values = []
        
        for field in profile_fields:
            if field in profile_data:
                profile_updates.append(f"{field} = ?")
                profile_values.append(profile_data[field])
        
        if profile_updates:
            profile_values.append(user_id)
            cursor.execute(f"""
                UPDATE patient_profiles 
                SET {', '.join(profile_updates)}, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, profile_values)
        
        conn.commit()
        return True, "Profile updated successfully"
        
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        return False, "Failed to update profile"
    finally:
        conn.close()

def get_user_profile(user_id):
    """Get complete user profile information"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.*, p.*
            FROM users u
            LEFT JOIN patient_profiles p ON u.id = p.user_id
            WHERE u.id = ?
        """, (user_id,))
        
        profile = cursor.fetchone()
        return profile if profile else None
        
    except Exception as e:
        print(f"Error getting profile: {str(e)}")
        return None
    finally:
        conn.close()
