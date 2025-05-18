import smtplib
import random
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from werkzeug.utils import secure_filename
from mysql.connector import Error
from db_connection import get_db_connection

registration_bp = Blueprint('registration', __name__)

# File upload configuration
UPLOAD_FOLDER = 'project/upload/buyer_valid_id'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def send_otp_email(email, otp):
    sender_email = "fanamazecommerce@zohomail.com"
    zoho_smtp_server = "smtp.zoho.com"
    zoho_smtp_port = 587
    zoho_smtp_user = sender_email
    zoho_smtp_password = "7v7pi67S2Sy6"

    message = f"Subject: Your OTP Code\n\nYour OTP code is {otp}."

    try:
        with smtplib.SMTP(zoho_smtp_server, zoho_smtp_port) as server:
            server.starttls()
            server.login(zoho_smtp_user, zoho_smtp_password)
            server.sendmail(sender_email, email, message)
        print(f"OTP sent to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def email_exists(email):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM buyer_accounts WHERE Email = %s", (email,))
            count = cursor.fetchone()[0]
            return count > 0
        except Error as e:
            print(f"Error checking email: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False

def phone_exists(phone):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM buyer_accounts WHERE Phone = %s", (phone,))
            count = cursor.fetchone()[0]
            return count > 0
        except Error as e:
            print(f"Error checking phone: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@registration_bp.route('/personal_info', methods=['GET', 'POST'])
def personal_info():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        middlename = request.form.get('middlename')
        lastname = request.form.get('lastname')
        suffix = request.form.get('suffix')
        sex = request.form.get('sex')
        birthdate_str = request.form.get('birthdate')

        birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

        # Check if the user is above 12 years old
        if age < 12:
            flash("You must be above 12 years old to create an account.", "danger")
            return redirect(url_for('registration.personal_info'))

        session['personal_info'] = {
            'firstname': firstname,
            'middlename': middlename,
            'lastname': lastname,
            'suffix': suffix,
            'sex': sex,
            'age': age,
            'birthdate': birthdate_str
        }

        return redirect(url_for('registration.address_info'))

    return render_template('registration_personal_info.html')

@registration_bp.route('/address_info', methods=['GET', 'POST'])
def address_info():
    if request.method == 'POST':
        street = request.form.get('street')
        brgy = request.form.get('brgy')
        city = request.form.get('city')
        state = request.form.get('state')
        zipcode = request.form.get('zipcode')

        session['address_info'] = {
            'street': street,
            'brgy': brgy,
            'city': city,
            'state': state,
            'zipcode': zipcode
        }

        return redirect(url_for('registration.valid_info'))

    return render_template('registration_address_info.html')

@registration_bp.route('/valid_info', methods=['GET', 'POST'])
def valid_info():
    if request.method == 'POST':
        # Handle file upload
        if 'valid_pic' not in request.files:
            flash("No file part", "danger")
            return redirect(request.url)
        
        file = request.files['valid_pic']
        if file.filename == '':
            flash("No selected file", "danger")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            valid_type = request.form.get('valid_type')
            valid_no = request.form.get('valid_no')

            session['valid_info'] = {
                'valid_pic': file_path,  # Store file path in session
                'valid_type': valid_type,
                'valid_no': valid_no
            }

            return redirect(url_for('registration.account_info'))

        else:
            flash("Invalid file type. Only images are allowed.", "danger")
            return redirect(request.url)

    return render_template('registration_valid_info.html')

@registration_bp.route('/account_info', methods=['GET', 'POST'])
def account_info():
    if request.method == 'POST':
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if email_exists(email):
            flash("Email already exists. Please try a different one.", "danger")
            return redirect(url_for('registration.account_info'))

        if phone_exists(phone):
            flash("Phone number already exists. Please try a different one.", "danger")
            return redirect(url_for('registration.account_info'))
        
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return redirect(url_for('registration.account_info'))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('registration.account_info'))

        session['account_info'] = {
            'phone': phone,
            'email': email,
            'password': password
        }

        otp = random.randint(100000, 999999)
        session['otp'] = otp
        send_otp_email(email, otp)

        return redirect(url_for('registration.verification'))

    return render_template('registration_account_info.html')

@registration_bp.route('/verification', methods=['GET', 'POST'])
def verification():
    if request.method == 'POST':
        entered_otp = request.form.get('otp')

        if int(entered_otp) == session.get('otp'):
            insert_data_to_db()
            return redirect(url_for('registration.registration_success'))  # Redirect after successful registration
        else:
            flash("Invalid OTP. Please try again.", "danger")
            return redirect(url_for('registration.verification'))

    return render_template('registration_verification.html')

@registration_bp.route('/registration_success')
def registration_success():
    return render_template('registration_success.html')

def insert_data_to_db():
    personal_info = session.get('personal_info')
    address_info = session.get('address_info')
    account_info = session.get('account_info')
    valid_info = session.get('valid_info')

    conn = get_db_connection()

    if conn:
        conn.autocommit = True
        try:
            cursor = conn.cursor()

            # Insert personal info
            cursor.execute('''INSERT INTO buyer_personal_info
                              (Firstname, Middlename, Lastname, Suffix, Sex, Age, Birthdate) 
                              VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                           (personal_info['firstname'], personal_info['middlename'], personal_info['lastname'],
                            personal_info['suffix'], personal_info['sex'], personal_info['age'], personal_info['birthdate']))
            personal_id = cursor.lastrowid
            print(f"Inserted personal info with ID: {personal_id}")

            # Insert address info
            cursor.execute('''INSERT INTO buyer_address_info 
                              (House_No, Barangay, City, Province, Postal_Code)
                              VALUES (%s, %s, %s, %s, %s)''',
                           (address_info['street'], address_info['brgy'], address_info['city'],
                            address_info['state'], address_info['zipcode']))
            address_id = cursor.lastrowid
            print(f"Inserted address info with ID: {address_id}")

            # Insert validation info
            cursor.execute('''INSERT INTO buyer_valid_info
                              (Valid_Type, Valid_Pic, Valid_No) 
                              VALUES (%s, %s, %s)''',
                           (valid_info['valid_type'], valid_info['valid_pic'], valid_info['valid_no']))
            valid_id = cursor.lastrowid
            print(f"Inserted valid info with ID: {valid_id}")

            # Insert account info
            cursor.execute('''INSERT INTO buyer_accounts 
                              (Personal_ID, Address_ID, Valid_ID, Phone, Email, Password, Status, Role) 
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                           (personal_id, address_id, valid_id, account_info['phone'], account_info['email'], account_info['password'],
                            "Registered", "Buyer"))
            buyer_id = cursor.lastrowid
            print(f"Inserted buyer account with ID: {buyer_id}")

            # Insert registration notification for buyer
            cursor.execute('''INSERT INTO notifications_buyer
                              (recipient_id, notification_type, title, message) 
                              VALUES (%s, %s, %s, %s)''',
                           (buyer_id, 'Buyer Registration', 'Registration Successful',
                            'Your registration was successful! Welcome to Fenamaz!'))
            
            # Insert registration notification for admin
            cursor.execute('''INSERT INTO notifications_admin
                              (recipient_id, notification_type, title, message) 
                              VALUES (%s, %s, %s, %s)''',
                           (1, 'Buyer Registration', 'New User Registration',
                            f'A new user has successfully registered. \n\nName: {personal_info["firstname"]} {personal_info["lastname"]} \nEmail: {account_info["email"]} \nPhone: {account_info["phone"]}'))

            # Commit all changes
            conn.commit()
            print("All data inserted successfully, including notification!")

            session.clear()
        except Error as e:
            print(f"Error while inserting data: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    else:
        print("Failed to get database connection.")


