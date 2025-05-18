import random
import smtplib
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db_connection import get_db_connection
from mysql.connector import Error

login_bp = Blueprint('login', __name__)

def validate_user(email, password):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)

            # Check in buyer_accounts and join with buyer_personal_info to get name details
            cursor.execute("""
                SELECT 
                    buyer_accounts.Buyer_ID, 
                    buyer_personal_info.Firstname, 
                    buyer_personal_info.Lastname,
                    'buyer' AS user_type, 
                    buyer_accounts.Status AS buyer_status
                FROM buyer_accounts
                JOIN buyer_personal_info ON buyer_accounts.Personal_ID = buyer_personal_info.Personal_ID
                WHERE Email = %s AND Password = %s
            """, (email, password))
            user = cursor.fetchone()
            if user:
                if user['buyer_status'] == 'Banned':
                    return 'banned'  # If the buyer status is "Banned", return 'banned'
                return user  # Return user details for buyers

            # Check in seller_accounts
            cursor.execute("""
                SELECT 
                    seller_accounts.Seller_ID, 
                    seller_personal_info.Firstname, 
                    seller_personal_info.Lastname,
                    'seller' AS user_type,
                    seller_accounts.Status AS seller_status
                FROM seller_accounts
                JOIN seller_personal_info ON seller_accounts.Personal_ID = seller_personal_info.Personal_ID
                WHERE Email = %s AND Password = %s
            """, (email, password))
            user = cursor.fetchone()
            if user:
                if user['seller_status'] == 'Pending':
                    return 'pending'  # If the seller status is "Pending", return 'pending'
                if user['seller_status'] == 'Banned':
                    return 'banned'  # If the seller status is "Banned", return 'banned'
                return user  # Return user details for sellers

            # Check in admin_accounts
            cursor.execute("""
                SELECT 
                    admin_accounts.Admin_ID, 
                    admin_accounts.Firstname, 
                    admin_accounts.Lastname, 
                    'admin' AS user_type 
                FROM admin_accounts
                WHERE Email = %s AND Password = %s AND Status = 'Active'
            """, (email, password))
            user = cursor.fetchone()
            if user:
                return user  # Return user details for admins

            return None  # Return None if not found
        except Error as e:
            print(f"Error validating user: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    return None


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = validate_user(email, password)
        if user == 'banned':
            return redirect(url_for('login.account_banned'))  # Redirect to banned page if status is "Banned"
        elif user == 'pending':
            return redirect(url_for('login.account_pending'))  # Redirect to pending page if status is "Pending"
        
        if user: 
            session['user_id'] = (
                user.get('Buyer_ID') 
                or user.get('Seller_ID') 
                or user.get('Admin_ID')
            )
            session['user_name'] = f"{user['Firstname']} {user['Lastname']}"
            session['user_type'] = user['user_type']
            session['login_success'] = True

            # Store the URL based on user type for later use in the frontend
            redirect_url = ''
            if user['user_type'] == 'buyer':
                redirect_url = url_for('buyer.buyer_homepage')
            elif user['user_type'] == 'seller':
                redirect_url = url_for('seller_dashboard.seller_dashboard')
            elif user['user_type'] == 'admin':
                redirect_url = url_for('admin.admin_dashboard')

            session['redirect_url'] = redirect_url

            return redirect(url_for('login.login'))

        else:
            flash("Invalid email or password. Please try again.", "danger")
            return redirect(url_for('login.login'))

    login_success = session.pop('login_success', False)
    redirect_url = session.pop('redirect_url', None)

    return render_template('login.html', login_success=login_success, redirect_url=redirect_url)



@login_bp.route('/user_choose')
def user_choose():
    return render_template('registration_user_choose.html')


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
            # Modified query to check both buyer_accounts and seller_accounts for the email
            cursor.execute("""
                SELECT COUNT(*) 
                FROM buyer_accounts 
                WHERE Email = %s
                UNION
                SELECT COUNT(*) 
                FROM seller_accounts 
                WHERE Email = %s
            """, (email, email))
            result = cursor.fetchall()
            # The result will contain two rows, one for buyer_accounts and one for seller_accounts
            count = sum(row[0] for row in result)  # Sum the counts from both queries

            return count > 0
        except Error as e:
            print(f"Error checking email: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False


@login_bp.route('/forgot_pass', methods=['GET', 'POST'])
def forgot_pass():
    if request.method == 'POST':
        email = request.form.get('email')
        
        # Check if the email exists in the database
        if not email_exists(email):
            flash("Email not found. Please try again.", "danger")
            return redirect(url_for('login.forgot_pass'))

        # Generate and send OTP to the email
        otp = random.randint(100000, 999999)
        session['forgot_otp'] = otp
        session['forgot_email'] = email

        send_otp_email(email, otp)
        
        return redirect(url_for('login.verify_otp'))

    return render_template('forgot_pass.html')

@login_bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        
        # Check if the OTP entered matches the one sent
        if int(entered_otp) == session.get('forgot_otp'):
            # OTP is correct, ask for new password (You can implement this next)
            flash("OTP verified successfully! Please enter your new password.", "success")
            return redirect(url_for('login.reset_password'))
        else:
            flash("Invalid OTP. Please try again.", "danger")
            return redirect(url_for('login.verify_otp'))

    return render_template('verify_otp.html')


@login_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        
        # Get the email from session
        email = session.get('forgot_email')
        
        # Check if email is valid
        if not email:
            flash("Session expired. Please try again.", "danger")
            return redirect(url_for('login.forgot_pass'))

        # Update the password in the relevant account (buyer or seller)
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # Update password in buyer_accounts if the email belongs to a buyer
                cursor.execute(""" 
                    UPDATE buyer_accounts 
                    SET Password = %s 
                    WHERE Email = %s 
                """, (new_password, email))
                
                # Update password in seller_accounts if the email belongs to a seller
                cursor.execute(""" 
                    UPDATE seller_accounts 
                    SET Password = %s 
                    WHERE Email = %s 
                """, (new_password, email))

                conn.commit()

                # Clear OTP session data after password reset
                session.pop('forgot_otp', None)
                session.pop('forgot_email', None)
                flash("Your password has been reset successfully!", "success")
                return redirect(url_for('login.login'))  # Redirect to the login page

            except Error as e:
                print(f"Error resetting password: {e}")
                flash("An error occurred. Please try again later.", "danger")
                return redirect(url_for('login.reset_password'))
            finally:
                cursor.close()
                conn.close()
        else:
            flash("Database connection error. Please try again.", "danger")
            return redirect(url_for('login.reset_password'))

    return render_template('reset_password.html')


# New Route for Pending Approval
@login_bp.route('/account_pending', methods=['GET'])
def account_pending():
    return render_template('account_pending.html')

@login_bp.route('/account_banned', methods=['GET'])
def account_banned():
    return render_template('account_banned.html')
