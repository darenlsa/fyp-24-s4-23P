-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    emergency_contact TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Patient Profiles Table
CREATE TABLE IF NOT EXISTS patient_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    blood_type TEXT,
    allergies TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Appointments Table
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    doctor_name TEXT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    appointment_type TEXT NOT NULL,
    status TEXT DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Prescriptions Table
CREATE TABLE IF NOT EXISTS prescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    medication_name TEXT NOT NULL,
    dosage TEXT NOT NULL,
    frequency TEXT NOT NULL,
    end_date DATE NOT NULL,
    refills_remaining INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Bills Table
CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    appointment_id INTEGER,
    amount REAL NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'PENDING',
    due_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(appointment_id) REFERENCES appointments(id)
);

-- Create Clinic Info Table
CREATE TABLE IF NOT EXISTS clinic_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opening_hours TEXT NOT NULL,
    address TEXT NOT NULL,
    map_link TEXT,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    support_hours TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert test clinic info
INSERT OR REPLACE INTO clinic_info (
    opening_hours, 
    address, 
    map_link, 
    phone, 
    email, 
    support_hours
) VALUES (
    'Monday-Friday: 8:00 AM - 6:00 PM\nSaturday: 9:00 AM - 2:00 PM\nSunday: Closed',
    '123 Healthcare Avenue, Medical District, City, 12345',
    'https://maps.google.com/?q=123+Healthcare+Avenue',
    '1-800-HEALTH-CARE',
    'contact@healthcareclinic.com',
    'Monday-Friday: 8:00 AM - 5:00 PM'
);

-- Create Services Table
CREATE TABLE IF NOT EXISTS clinic_services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample services
INSERT INTO clinic_services (category, name, description) VALUES
('General', 'Regular Checkup', 'Comprehensive physical examination and health assessment'),
('General', 'Vaccination', 'Various immunization services for all age groups'),
('Specialist', 'Cardiology', 'Heart and cardiovascular system examination and treatment'),
('Specialist', 'Dermatology', 'Skin, hair, and nail treatments'),
('Emergency', 'Urgent Care', '24/7 emergency medical services for immediate health concerns'),
('Laboratory', 'Blood Tests', 'Complete blood work and analysis'),
('Laboratory', 'X-Ray Services', 'Diagnostic imaging services');

-- Insert test user
INSERT OR REPLACE INTO users (id, username, password, email, phone, address, emergency_contact) 
VALUES (1, 'testuser', 'password123', 'test@example.com', '555-0123', '123 Test St', '555-9999');

-- Insert test profile
INSERT OR REPLACE INTO patient_profiles (user_id, first_name, last_name, blood_type, allergies) 
VALUES (1, 'John', 'Doe', 'O+', 'Penicillin');

-- Insert test appointments
INSERT OR REPLACE INTO appointments (user_id, doctor_name, appointment_date, appointment_time, appointment_type) 
VALUES 
(1, 'Dr. Smith', date('now', '+1 day'), '14:00', 'General Checkup'),
(1, 'Dr. Johnson', date('now', '+7 days'), '10:30', 'Follow-up');

-- Insert test prescriptions
INSERT OR REPLACE INTO prescriptions (user_id, medication_name, dosage, frequency, end_date, refills_remaining) 
VALUES 
(1, 'Amoxicillin', '500mg', 'Twice daily', date('now', '+10 days'), 2),
(1, 'Ibuprofen', '200mg', 'As needed', date('now', '+30 days'), 1);

-- Insert test bills
INSERT OR REPLACE INTO bills (user_id, appointment_id, amount, description, status, due_date) 
VALUES 
(1, 1, 150.00, 'General Checkup', 'PENDING', date('now', '+30 days')),
(1, 2, 75.00, 'Follow-up Consultation', 'PENDING', date('now', '+30 days'));

-- Create Post-Care Instructions Table
CREATE TABLE IF NOT EXISTS post_care_instructions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    procedure_name TEXT NOT NULL,
    instructions TEXT NOT NULL,
    side_effects TEXT,
    follow_up_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Create Health Reminders Table
CREATE TABLE IF NOT EXISTS health_reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    reminder_type TEXT NOT NULL,
    reminder_message TEXT NOT NULL,
    reminder_date DATE NOT NULL,
    is_recurring BOOLEAN DEFAULT 0,
    recurrence_pattern TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Create Health Advice Table
CREATE TABLE IF NOT EXISTS health_advice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Health Events Table
CREATE TABLE IF NOT EXISTS health_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    event_date DATE NOT NULL,
    location TEXT,
    max_participants INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample post-care instructions
INSERT INTO post_care_instructions (user_id, procedure_name, instructions, side_effects, follow_up_date) VALUES
(1, 'Dental Cleaning', 'Avoid hot foods for 24 hours. Brush gently around treated areas.', 'Mild sensitivity may occur', date('now', '+7 days')),
(1, 'Flu Shot', 'Monitor injection site. Take acetaminophen if needed for discomfort.', 'Soreness at injection site, mild fever', date('now', '+1 day'));

-- Insert sample health advice
INSERT INTO health_advice (category, title, content) VALUES
('Wellness', 'Staying Hydrated', 'Drink at least 8 glasses of water daily. Signs of dehydration include...'),
('Exercise', 'Starting a Walking Routine', 'Begin with 10 minutes daily, gradually increase to 30 minutes...');

-- Insert sample health events
INSERT INTO health_events (title, description, event_date, location, max_participants) VALUES
('Flu Shot Clinic', 'Annual flu vaccination event', date('now', '+30 days'), 'Main Clinic', 100),
('Diabetes Workshop', 'Learn about managing diabetes', date('now', '+14 days'), 'Education Center', 50);

-- Create Doctors Table
CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    speciality TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    schedule TEXT,  -- JSON string containing weekly schedule
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample doctors
INSERT INTO doctors (name, speciality, schedule) VALUES
('Smith', 'General Practice', '{"monday": "08:00-17:00", "tuesday": "08:00-17:00", "wednesday": "08:00-17:00", "thursday": "08:00-17:00", "friday": "08:00-17:00"}'),
('Johnson', 'Cardiology', '{"monday": "09:00-18:00", "tuesday": "09:00-18:00", "wednesday": "09:00-18:00", "thursday": "09:00-18:00", "friday": "09:00-18:00"}'),
('Williams', 'Pediatrics', '{"monday": "08:00-17:00", "tuesday": "08:00-17:00", "wednesday": "08:00-17:00", "thursday": "08:00-17:00", "friday": "08:00-17:00"}'),
('Brown', 'Dermatology', '{"monday": "09:00-18:00", "tuesday": "09:00-18:00", "wednesday": "09:00-18:00", "thursday": "09:00-18:00", "friday": "09:00-18:00"}');
