from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from db_connection import get_db, initialize_database
from auth import register_user, login_user, logout_user
from dialogflow_handler import DialogflowHandler
from notification_scheduler import schedule_notification
from appointment_scheduler import AppointmentScheduler
from payment_handler import PaymentHandler
from prescription_handler import PrescriptionHandler
from health_records_handler import HealthRecordsHandler
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize handlers
dialogflow = DialogflowHandler('chatbotproject-444010')
payment_handler = PaymentHandler()
prescription_handler = PrescriptionHandler()
health_records_handler = HealthRecordsHandler()
appointment_scheduler = AppointmentScheduler()

# Initialize database when the app starts
initialize_database()

@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('index.html', user_id=session['user_id'])  # Pass user_id to the template
    return render_template('index.html', user_id=None)  # Pass None if not logged in


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        success, result = login_user(username, password)
        
        if success:
            # Store user data in session
            session['user_id'] = result['id']
            session['username'] = result['username']
            return redirect(url_for('chat'))
        else:
            # Display error message
            return render_template('login.html', error=result)
    
    return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()  # Clear the session data
    return redirect(url_for('index'))  # Redirect to the home page


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        first_name = request.form.get('first_name', username)
        last_name = request.form.get('last_name', '')
        
        success, message = register_user(
            username, 
            password, 
            email,
            first_name,
            last_name
        )
        
        if success:
            return redirect(url_for('login'))
        return render_template('register.html', error=message)
    return render_template('register.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    print(f"Current session data: {dict(session)}")
    
    if 'user_id' not in session:
        print("No user_id in session, redirecting to login")
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data or 'message' not in data:
                return jsonify({"error": "No message provided"}), 400
                
            user_message = data['message']
            user_id = session.get('user_id')
            
            print(f"Processing message: {user_message}")
            print(f"User ID: {user_id}")
            
            # Pass the actual user_id from session
            response = dialogflow.handle_intent(user_id, user_message)
            return jsonify({"response": response})
            
        except Exception as e:
            print(f"Error in chat endpoint: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return jsonify({"error": "An internal error occurred"}), 500

    return render_template('chat.html', 
                         username=session.get('username'),
                         user_id=session.get('user_id'))


def get_prescription_details(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prescriptions WHERE user_id = ?", (user_id,))
    prescriptions = cursor.fetchall()
    conn.close()
    return prescriptions

def get_user_bills(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bills WHERE user_id = ?", (user_id,))
    bills = cursor.fetchall()
    conn.close()
    return bills

def get_user_profile(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user_profile(user_id, username, email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username = ?, email = ? WHERE id = ?", (username, email, user_id))
    conn.commit()
    conn.close()




# Define the /appointments route for handling the appointment page
@app.route('/appointments')
def appointments():
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Redirect to home if not logged in
    return render_template('appointments.html')  # Render appointments page

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/prescriptions')
def prescriptions():
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Redirect to home if not logged in
    
    # Fetch prescriptions from database for the logged-in user
    user_id = session['user_id']
    prescriptions = get_prescription_details(user_id)
    
    return render_template('prescription.html', prescriptions=prescriptions)

@app.route('/billing')
def billing():
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Redirect to home if not logged in
    
    # Fetch bills from database for the logged-in user
    user_id = session['user_id']
    bills = get_user_bills(user_id)
    
    return render_template('billing.html', bills=bills)



@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Redirect to home if not logged in
    
    # Fetch profile details from database for the logged-in user
    user_id = session['user_id']
    user = get_user_profile(user_id)
    
    if request.method == 'POST':
        # Update user profile logic here
        username = request.form['username']
        email = request.form['email']
        
        update_user_profile(user_id, username, email)
        return redirect(url_for('profile'))  # Redirect after updating
    
    return render_template('profile.html', user=user)

# Health Records Routes
@app.route('/health-records', methods=['GET'])
def health_records():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    records = health_records_handler.get_health_record_summary(session['user_id'])
    return render_template('health_records.html', records=records)

@app.route('/lab-results', methods=['GET'])
def lab_results():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    results = health_records_handler.view_lab_results(session['user_id'])
    return render_template('lab_results.html', results=results)

@app.route('/request-records', methods=['POST'])
def request_records():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    format_type = request.form.get('format_type', 'digital')
    request_id = health_records_handler.request_record_copy(session['user_id'], format_type)
    return jsonify({"request_id": request_id})

# Prescription Routes
@app.route('/prescriptions/refill', methods=['POST'])
def request_refill():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    prescription_id = request.form.get('prescription_id')
    refill_id = prescription_handler.request_refill(session['user_id'], prescription_id)
    return jsonify({"refill_id": refill_id})

@app.route('/prescriptions/status/<int:refill_id>', methods=['GET'])
def refill_status(refill_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    status = prescription_handler.get_refill_status(refill_id)
    return jsonify({"status": status})

@app.route('/prescriptions/medication-info/<medication_name>', methods=['GET'])
def medication_info(medication_name):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    info = prescription_handler.get_medication_info(medication_name)
    return jsonify(info if info else {"error": "Medication information not found"})

# Payment Routes
@app.route('/billing/outstanding', methods=['GET'])
def outstanding_bills():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    bills = payment_handler.get_outstanding_bills(session['user_id'])
    return render_template('billing.html', bills=bills)

@app.route('/billing/pay', methods=['POST'])
def process_payment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    bill_id = request.form.get('bill_id')
    amount = float(request.form.get('amount'))
    payment_method = request.form.get('payment_method')
    
    success = payment_handler.process_payment(bill_id, amount, payment_method)
    if success:
        return jsonify({"status": "success"})
    return jsonify({"status": "failed"}), 400

@app.route('/billing/payment-plans', methods=['GET'])
def payment_plans():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    plans = payment_handler.get_payment_plans(session['user_id'])
    return render_template('payment_plans.html', plans=plans)

@app.route('/billing/setup-plan', methods=['POST'])
def setup_payment_plan():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    bill_id = request.form.get('bill_id')
    installments = int(request.form.get('installments'))
    
    plan_id = payment_handler.setup_payment_plan(session['user_id'], bill_id, installments)
    if plan_id:
        return jsonify({"plan_id": plan_id})
    return jsonify({"error": "Could not create payment plan"}), 400

@app.route('/billing/receipt/<int:payment_id>', methods=['GET'])
def payment_receipt(payment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    receipt = payment_handler.generate_payment_receipt(payment_id)
    if receipt:
        return render_template('receipt.html', receipt=receipt)
    return jsonify({"error": "Receipt not found"}), 404

# Clinic Information Routes
@app.route('/clinic/info/<info_type>', methods=['GET'])
def get_clinic_info(info_type):
    if info_type not in ['opening_hours', 'location', 'contact']:
        return jsonify({"error": "Invalid information type"}), 400
    
    info = dialogflow.get_clinic_info(info_type)
    return jsonify(info)

@app.route('/clinic/services', methods=['GET'])
def get_services():
    category = request.args.get('category')
    services = dialogflow.get_available_services(category)
    return jsonify({"services": services})

# Language Support
@app.route('/set-language', methods=['POST'])
def set_language():
    language = request.form.get('language')
    if language:
        session['language'] = language
        return jsonify({"status": "success"})
    return jsonify({"error": "Language not specified"}), 400

# Account Management Routes
@app.route('/account/deactivate', methods=['POST'])
def deactivate_account():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = 'deactivated' WHERE id = ?", (session['user_id'],))
    conn.commit()
    conn.close()
    
    session.clear()
    return jsonify({"status": "success"})

@app.route('/account/reset-password', methods=['POST'])
def reset_password():
    email = request.form.get('email')
    if not email:
        return jsonify({"error": "Email not provided"}), 400
    
    # In a real application, you would:
    # 1. Generate a secure reset token
    # 2. Store it in the database with an expiration
    # 3. Send an email with a reset link
    # For this demo, we'll just return success
    return jsonify({
        "status": "success",
        "message": "If an account exists with this email, you will receive password reset instructions."
    })

# Auto-logout after inactivity
@app.before_request
def check_session_timeout():
    if 'user_id' in session:
        last_activity = session.get('last_activity')
        if last_activity:
            timeout = 30 * 60  # 30 minutes
            if (datetime.now() - datetime.fromtimestamp(last_activity)).seconds > timeout:
                session.clear()
                return jsonify({"error": "Session expired"}), 401
        session['last_activity'] = datetime.now().timestamp()

# Post-Care Instructions Routes
@app.route('/post-care/<int:user_id>', methods=['GET'])
def get_post_care(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    procedure = request.args.get('procedure')
    instructions = dialogflow.get_post_care_info(user_id, procedure)
    return jsonify({"instructions": instructions})

@app.route('/health/advice', methods=['GET'])
def get_health_advice():
    category = request.args.get('category')
    advice = dialogflow.get_health_advice(category)
    return jsonify({"advice": advice})

@app.route('/health/events', methods=['GET'])
def get_health_events():
    events = dialogflow.get_health_events()
    return jsonify({"events": events})

@app.route('/health/reminders', methods=['POST'])
def set_health_reminder():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    reminder_type = data.get('reminder_type')
    reminder_date = data.get('reminder_date')
    message = data.get('message')
    is_recurring = data.get('is_recurring', False)
    recurrence_pattern = data.get('recurrence_pattern')
    
    if not all([reminder_type, reminder_date, message]):
        return jsonify({"error": "Missing required fields"}), 400
    
    reminder_id = dialogflow.health_reminders.set_reminder(
        session['user_id'],
        reminder_type,
        message,
        reminder_date,
        is_recurring,
        recurrence_pattern
    )
    
    return jsonify({
        "status": "success",
        "reminder_id": reminder_id
    })

@app.route('/health/reminders/<int:user_id>', methods=['GET'])
def get_user_reminders(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    reminders = dialogflow.health_reminders.get_user_reminders(user_id)
    return jsonify({"reminders": reminders})

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Dialogflow webhook requests"""
    try:
        if 'user_id' not in session:
            return jsonify({
                'fulfillmentText': "Please log in to continue."
            })
            
        user_id = session['user_id']
        req = request.get_json()
        
        print(f"Webhook request: {req}")
        print(f"User ID: {user_id}")
        
        # Get intent and parameters
        intent = req['queryResult']['intent']['displayName']
        parameters = req['queryResult']['parameters']
        
        # Handle different intents
        if intent == 'appointment_scheduling':
            return handle_appointment_webhook(user_id, parameters)
        elif intent == 'service_inquiry':
            return handle_service_inquiry_webhook(user_id, parameters)
        else:
            return jsonify({
                'fulfillmentText': "I'm not sure how to help with that. Could you please rephrase?"
            })
            
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'fulfillmentText': "Sorry, there was an error processing your request."
        })

def handle_appointment_webhook(user_id, parameters):
    """Handle appointment scheduling webhook"""
    try:
        print(f"Processing appointment for user {user_id}")
        print(f"Parameters: {parameters}")
        
        date_time = parameters.get('date-time')
        doctor = parameters.get('doctor')
        appointment_type = parameters.get('appointment-type', 'General Checkup')
        
        # Check availability
        if date_time and doctor:
            try:
                date = date_time.split('T')[0]
                time = date_time.split('T')[1].split('+')[0][:5]
                
                # Validate date is not in past
                if datetime.strptime(date, '%Y-%m-%d').date() < datetime.now().date():
                    return jsonify({
                        'fulfillmentText': "Sorry, you cannot schedule appointments in the past. Please choose a future date."
                    })
                
                # Try to schedule appointment
                appointment_id = appointment_scheduler.schedule_appointment(
                    user_id, doctor, date, appointment_type, time
                )
                
                if appointment_id:
                    return jsonify({
                        'fulfillmentText': f"""✅ Appointment scheduled successfully!
📅 Date: {date}
⏰ Time: {time}
👨‍⚕️ Doctor: Dr. {doctor}
📋 Type: {appointment_type}

Your appointment has been confirmed. Would you like to set a reminder?"""
                    })
                else:
                    return jsonify({
                        'fulfillmentText': "Sorry, that slot is not available. Would you like to see other available times?"
                    })
            except Exception as e:
                print(f"Error parsing date/time: {str(e)}")
                return jsonify({
                    'fulfillmentText': "Sorry, I couldn't understand the date and time format. Please try again."
                })
        
        return jsonify({
            'fulfillmentText': "I need more information. Please provide your preferred date, time, and doctor."
        })
    except Exception as e:
        print(f"Error in appointment webhook: {str(e)}")
        return jsonify({
            'fulfillmentText': "Sorry, there was an error processing your request. Please try again."
        })

def handle_service_inquiry_webhook(user_id, parameters):
    """Handle service inquiry webhook"""
    try:
        service_type = parameters.get('service-type')
        
        if service_type:
            # Get service information
            service_info = dialogflow.get_service_info(service_type)
            return jsonify({
                'fulfillmentText': service_info
            })
        
        # Return list of all services
        services = dialogflow.get_available_services()
        return jsonify({
            'fulfillmentText': services
        })
        
    except Exception as e:
        print(f"Service inquiry webhook error: {str(e)}")
        return jsonify({
            'fulfillmentText': 'Sorry, there was an error retrieving service information.'
        })
