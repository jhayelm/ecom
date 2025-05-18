import smtplib
import random
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from datetime import datetime
from mysql.connector import Error
from db_connection import get_db_connection
from werkzeug.utils import secure_filename
import os

VALID_ID_FOLDER = os.path.join(os.getcwd(), 'project', 'upload', 'seller_valid_id')
BUSINESS_PERMIT_FOLDER = os.path.join(os.getcwd(), 'project', 'upload', 'business_permit')

# Ensure the directories exist
os.makedirs(VALID_ID_FOLDER, exist_ok=True)
os.makedirs(BUSINESS_PERMIT_FOLDER, exist_ok=True)

seller_registration_bp = Blueprint('seller_registration', __name__, template_folder='templates')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

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
            cursor.execute("SELECT COUNT(*) FROM seller_accounts WHERE Email = %s", (email,))
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
            cursor.execute("SELECT COUNT(*) FROM seller_accounts WHERE Phone = %s", (phone,))
            count = cursor.fetchone()[0]
            return count > 0  
        except Error as e:
            print(f"Error checking phone: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False

@seller_registration_bp.route('/seller_personal_info', methods=['GET', 'POST'])
def seller_personal_info():
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

        if age < 12:
            flash("You must be at least 12 years old to register.", "danger")
            return redirect(url_for('seller_registration.seller_personal_info'))
        
        session['personal_info'] = {
            'firstname': firstname,
            'middlename': middlename,
            'lastname': lastname,
            'suffix': suffix,
            'sex': sex,
            'age': age,
            'birthdate': birthdate_str
        }
        
        return redirect(url_for('seller_registration.seller_address_info'))

    return render_template('seller_registration_personal_info.html')

@seller_registration_bp.route('/seller_address_info', methods=['GET', 'POST'])
def seller_address_info():
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

        return redirect(url_for('seller_registration.seller_valid_info'))

    return render_template('seller_registration_address_info.html')

@seller_registration_bp.route('/seller_valid_info', methods=['GET', 'POST'])
def seller_valid_info():
    if request.method == 'POST':
        valid_pic = request.files.get('valid_pic')
        valid_type = request.form.get('valid_type')
        valid_no = request.form.get('valid_no')

        if valid_pic:
            # Secure the file name and save it to the valid ID folder
            filename = secure_filename(valid_pic.filename)
            file_path = os.path.join(VALID_ID_FOLDER, filename)
            valid_pic.save(file_path)
        
        # Store the file path in the session to use later
        session['valid_info'] = {
            'valid_pic_path': file_path,
            'valid_type': valid_type,
            'valid_no': valid_no
        }

        return redirect(url_for('seller_registration.seller_business_info'))

    return render_template('seller_registration_valid_info.html')

@seller_registration_bp.route('/seller_business_info', methods=['GET', 'POST'])
def seller_business_info():
    if request.method == 'POST':
        business_permit = request.files.get('business_permit')
        business_permit_no = request.form.get('business_permit_no')

        if business_permit:
            filename = secure_filename(business_permit.filename)
            file_path = os.path.join(BUSINESS_PERMIT_FOLDER, filename)
            business_permit.save(file_path)

            session['business_info'] = {
                'business_permit_path': file_path,
                'business_permit_no': business_permit_no
            }

        return redirect(url_for('seller_registration.seller_account_info'))

    return render_template('seller_registration_business_info.html')

@seller_registration_bp.route('/seller_account_info', methods=['GET', 'POST'])
def seller_account_info():
    if request.method == 'POST':
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if email_exists(email):
            flash("Email already exists. Please try a different one.", "danger")
            return redirect(url_for('seller_registration.seller_account_info'))

        if phone_exists(phone):
            flash("Phone number already exists. Please try a different one.", "danger")
            return redirect(url_for('seller_registration.seller_account_info'))
        
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return redirect(url_for('registration.account_info'))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('seller_registration.seller_account_info'))

        session['account_info'] = {
            'phone': phone,
            'email': email,
            'password': password  
        }

        otp = random.randint(100000, 999999)
        session['otp'] = otp
        send_otp_email(email, otp)

        return redirect(url_for('seller_registration.seller_verification'))

    return render_template('seller_registration_account_info.html')

@seller_registration_bp.route('/seller_verification', methods=['GET', 'POST'])
def seller_verification():
    if request.method == 'POST':
        entered_otp = request.form.get('otp')

        if int(entered_otp) == session.get('otp'):
            return redirect(url_for('seller_registration.seller_setup_shop_profile'))  # Redirect after successful registration
        else:
            flash("Invalid OTP. Please try again.", "danger")
            return redirect(url_for('seller_registration.seller_verification'))

    return render_template('seller_registration_verification.html')


@seller_registration_bp.route('/seller_setup_shop_profile', methods=['GET', 'POST'])
def seller_setup_shop_profile():
    if request.method == 'POST':
        # Retrieve the data from the form
        shop_name = request.form.get('shopName')
        shop_description = request.form.get('shopDescription')
        shop_profile_file = request.files.get('shopProfilePicture')

        # Validation for required fields
        if not shop_name or not shop_profile_file:
            flash('Shop Name and Profile Picture are required.', 'danger')
            return redirect(url_for('seller_registration.seller_setup_shop_profile'))  # Reload the page to show error

        # Process the uploaded profile picture
        profile_picture_blob = shop_profile_file.read()

        # Save this data temporarily in the session (until the final submission)
        session['shop_profile'] = {
            'shop_name': shop_name,
            'shop_description': shop_description,
            'shop_profile_picture': profile_picture_blob
        }

        # Redirect to the final step or show success message
        insert_data_to_db()
        flash('Shop profile setup successfully! Now your registration is complete.', 'success')
        return redirect(url_for('login.account_pending'))

    return render_template('seller_registration_shop_profile.html')


def insert_data_to_db():
    personal_info = session.get('personal_info')
    address_info = session.get('address_info')
    valid_info = session.get('valid_info')
    business_info = session.get('business_info')
    account_info = session.get('account_info')
    shop_profile = session.get('shop_profile')  # Fetching shop profile data

    conn = get_db_connection()

    if conn:
        conn.autocommit = True
        try:
            cursor = conn.cursor()

            # Insert into seller_personal_info
            cursor.execute('''INSERT INTO seller_personal_info
                              (Firstname, Middlename, Lastname, Suffix, Sex, Age, Birthdate) 
                              VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                           (personal_info['firstname'], personal_info['middlename'], personal_info['lastname'],
                            personal_info['suffix'], personal_info['sex'], personal_info['age'], personal_info['birthdate']))
            personal_id = cursor.lastrowid

            # Insert into seller_address_info
            cursor.execute('''INSERT INTO seller_address_info 
                              (House_No, Barangay, City, Province, Postal_Code)
                              VALUES (%s, %s, %s, %s, %s)''',
                           (address_info['street'], address_info['brgy'], address_info['city'],
                            address_info['state'], address_info['zipcode']))
            address_id = cursor.lastrowid

            # Insert into seller_valid_info
            cursor.execute('''INSERT INTO seller_valid_info 
                              (Valid_Type, Valid_No, Valid_Pic)
                              VALUES (%s, %s, %s)''',
                           (valid_info['valid_type'], valid_info['valid_no'], valid_info['valid_pic_path']))
            valid_id = cursor.lastrowid

            # Insert into seller_business_info
            cursor.execute('''INSERT INTO seller_business_info
                              (Business_Permit, Business_Permit_No)
                              VALUES (%s, %s)''',
                           (business_info['business_permit_path'], business_info['business_permit_no']))
            business_id = cursor.lastrowid

            # Insert into seller_accounts
            cursor.execute('''INSERT INTO seller_accounts 
                              (Personal_ID, Address_ID, Valid_ID, Business_ID, Phone, Email, Password, Status, Role) 
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                           (personal_id, address_id, valid_id, business_id, account_info['phone'], account_info['email'], account_info['password'],
                            "Pending", "Seller"))
            seller_id = cursor.lastrowid  # Get the seller ID from the last insert

            # Insert into seller_shop (shop profile data)
            if shop_profile:
                cursor.execute('''INSERT INTO seller_shop 
                                  (Seller_ID, Shop_Name, Shop_Description, Shop_Profile) 
                                  VALUES (%s, %s, %s, %s)''',
                               (seller_id, shop_profile['shop_name'], shop_profile['shop_description'], shop_profile['shop_profile_picture']))
            
            # Insert into notifications_admin
            cursor.execute('''INSERT INTO notifications_admin
                              (recipient_id, notification_type, title, message) 
                              VALUES (%s, %s, %s, %s)''',
                           (1, 'Pending Registration', 'Pending Seller Registration',
                            f'A new seller has successfully registered and is waiting for your approval. Check Now! \n\nName: {personal_info["firstname"]} {personal_info["lastname"]} \nEmail: {account_info["email"]} \nPhone: {account_info["phone"]}'))

            conn.commit()
            print("All data inserted successfully including the shop profile and notification!")

            session.clear()  # Clear session data after successful registration
        except Error as e:
            import traceback
            traceback.print_exc()
            print(f"Error inserting data: {e}")
            flash("Error during registration. Please try again.", "danger")
        finally:
            cursor.close()
            conn.close()


