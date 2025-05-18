from flask import Blueprint, render_template, session, redirect, url_for, flash
from db_connection import get_db_connection
from mysql.connector import Error
import base64
from flask import request, jsonify
import os

buyer_profile_bp = Blueprint('buyer_profile', __name__)

@buyer_profile_bp.route('/buyer_profile')
def show_buyer_profile():
    # Ensure that the user is logged in
    if 'user_id' not in session:
        flash("You need to log in first", "danger")
        return redirect(url_for('login.login'))  # Redirect to login if user is not logged in

    user_id = session['user_id']  # Get Buyer_ID from session
    

    # Fetch buyer details from the database
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)

            # Query to fetch buyer details
            cursor.execute("""
                SELECT 
                    buyer_personal_info.Firstname,
                    buyer_personal_info.Middlename,
                    buyer_personal_info.Lastname,
                    buyer_personal_info.Suffix,
                    buyer_personal_info.Sex,
                    buyer_personal_info.Age,
                    buyer_personal_info.Birthdate,
                    buyer_accounts.Email,
                    buyer_accounts.Phone,
                    buyer_address_info.House_No,
                    buyer_address_info.Barangay AS Brgy,
                    buyer_address_info.City,
                    buyer_address_info.Province,
                    buyer_address_info.Postal_Code,
                    buyer_accounts.Profile_Pic,
                    buyer_valid_info.Valid_Type,
                    buyer_valid_info.Valid_Pic,
                    buyer_valid_info.Valid_No
                FROM buyer_accounts
                JOIN buyer_personal_info ON buyer_accounts.Personal_ID = buyer_personal_info.Personal_ID
                JOIN buyer_address_info ON buyer_accounts.Address_ID = buyer_address_info.Address_ID
                JOIN buyer_valid_info ON buyer_accounts.Valid_ID = buyer_valid_info.Valid_ID
                WHERE buyer_accounts.Buyer_ID = %s
            """, (user_id,))

            buyer = cursor.fetchone()

            if buyer:
                # Base64 encode the Valid_Pic binary data
                if buyer['Valid_Pic']:
                    buyer['Valid_Pic'] = base64.b64encode(buyer['Valid_Pic']).decode('utf-8')
                # Render the template and pass the buyer's data to it
                return render_template('buyer_profile.html', buyer=buyer)
            else:
                flash("Buyer not found", "danger")
                return redirect(url_for('login.login'))  # Redirect if buyer is not found

        except Error as e:
            print(f"Error fetching buyer profile: {e}")
            flash("An error occurred while fetching your profile.", "danger")
            return redirect(url_for('buyer_profile.show_buyer_profile'))  # Handle errors

        finally:
            cursor.close()
            conn.close()
    else:
        flash("Database connection error.", "danger")
        return redirect(url_for('login.login'))  # Handle DB connection error
    
    
@buyer_profile_bp.route('/update_profile_pic', methods=['POST'])
def update_profile_pic():
    user_id = session['user_id']
    file = request.files['profile_pic']

    if file and file.filename:
        # Save the file
        try:
            # Here you can save the file to the database or file system
            profile_pic_data = file.read()
            
            # Open a connection to the database
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE buyer_accounts 
                    SET Profile_Pic = %s 
                    WHERE Buyer_ID = %s
                """, (profile_pic_data, user_id))
                conn.commit()

                cursor.close()
                conn.close()

                # Flash success message
                flash("Profile picture updated successfully!", "success")
            else:
                flash("Database connection error.", "danger")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
    else:
        flash("No file uploaded.", "danger")

    return redirect(url_for('buyer_profile.show_buyer_profile'))
