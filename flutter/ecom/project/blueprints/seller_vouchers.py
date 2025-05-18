from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from db_connection import get_db_connection
from mysql.connector import Error
from datetime import date, datetime, timedelta


seller_vouchers_bp = Blueprint('seller_vouchers', __name__)

@seller_vouchers_bp.route('/seller_vouchers', methods=['GET'])
def seller_vouchers():
    shop_profile = fetch_shop_profile()

    page = request.args.get('page', 1, type=int)  # Current page
    limit = 10  # Items per page
    offset = (page - 1) * limit
    search = request.args.get('search', '')  # Search query
    view_archived = request.args.get('view_archived', 'false') == 'true'
    filter_type = request.args.get('filter', 'All')  # Filter by type
    sort_order = request.args.get('sort', 'recent')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Base query
        query = """
            SELECT Voucher_ID, Voucher_Type, Voucher_Name, Voucher_Min, Voucher_Description, 
                Voucher_Start_Date, Voucher_End_Date, Date_Added, Status
            FROM seller_vouchers
            WHERE Seller_ID = %s
        """
        params = [session.get('user_id')]

        # Filter by status (Active/Archived)
        if view_archived:
            query += " AND Status = 'Archived'"
        else:
            query += " AND Status = 'Active'"

        # Apply search
        if search.strip():
            query += """
                AND (
                    Voucher_Type LIKE %s OR
                    Voucher_Name LIKE %s OR
                    Voucher_Min LIKE %s OR
                    Voucher_Description LIKE %s
                )
            """
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])
            
        # Filter by voucher type
        if filter_type != 'All':
            query += " AND Voucher_Type = %s"
            params.append(filter_type)

        # Sort order
        if sort_order == 'recent':
            query += " ORDER BY Date_Added DESC"
        elif sort_order == 'oldest':
            query += " ORDER BY Date_Added ASC"

        # Pagination
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, tuple(params))
        vouchers = cursor.fetchall()

        # Count total for pagination
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM seller_vouchers
            WHERE Seller_ID = %s
        """ + (" AND Status = 'Archived'" if view_archived else " AND Status = 'Active'"), (session.get('user_id'),))
        total_vouchers = cursor.fetchone()['total']
        total_pages = (total_vouchers // limit) + (1 if total_vouchers % limit else 0)

    except Exception as e:
        flash(f"Error retrieving vouchers: {e}", 'danger')
        vouchers = []
        total_pages = 1
    finally:
        cursor.close()
        conn.close()

    return render_template(
        'seller_vouchers.html',
        vouchers=vouchers,
        page=page,
        total_pages=total_pages,
        limit=limit,
        search=search,
        view_archived=view_archived,
        selected_filter=filter_type,
        selected_sort=sort_order,
        shop_profile=shop_profile
    )


def fetch_shop_profile():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    seller_id = session['user_id']
    
    try:
        cursor.execute("""
            SELECT Shop_Name, Shop_Profile
            FROM seller_shop
            WHERE Seller_ID = %s
        """, (seller_id,))
        shop_profile = cursor.fetchone()
        return shop_profile if shop_profile else {}  # Return empty dict if no profile found
    except Exception as e:
        flash(f'Error fetching shop profile: {e}', 'danger')
        return {}
    finally:
        cursor.close()
        conn.close()

# Add Voucher
@seller_vouchers_bp.route('/seller_vouchers/add', methods=['POST'])
def add_voucher():
    # Get Seller_ID from the session
    seller_id = session.get('user_id')  # Correctly retrieve from session
    voucher_type = request.form.get('voucherType')
    voucher_name = request.form.get('voucherName')
    voucher_min = request.form.get('voucherMinimum')
    voucher_description = request.form.get('voucherDescription')
    voucher_start_date = request.form.get('voucherStartDate') 
    voucher_end_date = request.form.get('voucherEndDate') 


    if not all([seller_id, voucher_type, voucher_name, voucher_min, voucher_start_date, voucher_end_date]):
        flash('All fields are required.', 'danger')
        return redirect(url_for('seller_vouchers.seller_vouchers'))
    
    # Validate that the end date is after the start date
    if voucher_start_date >= voucher_end_date:
        flash('Invalid Input: End Date must be later than Start Date.', 'danger')
        return redirect(url_for('seller_vouchers.seller_vouchers'))

    try:
        # Connect to the database
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed!', 'error')
            return redirect(url_for('seller_vouchers.seller_vouchers'))
        
        cursor = conn.cursor()

        # Ensure the Seller_ID exists in the seller_accounts table
        cursor.execute("SELECT COUNT(*) FROM seller_accounts WHERE Seller_ID = %s", (seller_id,))
        seller_exists = cursor.fetchone()[0]

        if not seller_exists:
            flash('Invalid Seller ID. Please ensure the seller exists.', 'error')
            return redirect(url_for('seller_vouchers.seller_vouchers'))

        # Insert voucher into the database with Status='Active'
        sql = """
            INSERT INTO seller_vouchers 
            (Seller_ID, Voucher_Type, Voucher_Name, Voucher_Min, Voucher_Description, Voucher_Start_Date, Voucher_End_Date, Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Active')
        """
        cursor.execute(sql, (seller_id, voucher_type, voucher_name, voucher_min, voucher_description, voucher_start_date, voucher_end_date))
        conn.commit()
        
        notification_sql = """
            INSERT INTO notifications_seller 
            (recipient_id, recipient_role, notification_type, title, message, is_read)
            VALUES (%s, 'Seller', 'Voucher Added', %s, %s, 0)
        """
        notification_title = "New Voucher Added"
        notification_message = (
            f"A new voucher '{voucher_name}' has been successfully added."
            f"\nStart Date: {voucher_start_date}\nEnd Date: {voucher_end_date}."
        )
        cursor.execute(notification_sql, (seller_id, notification_title, notification_message))
        conn.commit()
        
        
        flash('Voucher added successfully!', 'success')
    except Error as e:
        flash(f"Error adding voucher: {str(e)}", 'error')
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    return redirect(url_for('seller_vouchers.seller_vouchers'))


@seller_vouchers_bp.route('/archive_voucher/<int:voucher_id>', methods=['POST'])
def archive_voucher(voucher_id):
    """Set the status of a voucher to 'Archived'."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the status of the voucher to 'Archived'
        cursor.execute("""
            UPDATE seller_vouchers
            SET Status = 'Archived'
            WHERE Voucher_ID = %s AND Seller_ID = %s
        """, (voucher_id, session.get('user_id')))
        conn.commit()

        flash('Voucher archived successfully.', 'success')
    except Error as e:
        conn.rollback()
        flash(f'Error archiving voucher: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('seller_vouchers.seller_vouchers'))


@seller_vouchers_bp.route('/unarchive_voucher/<int:voucher_id>', methods=['POST'])
def unarchive_voucher(voucher_id):
    """Set the status of a voucher to 'Active'."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the status of the voucher to 'Active'
        cursor.execute("""
            UPDATE seller_vouchers
            SET Status = 'Active'
            WHERE Voucher_ID = %s AND Seller_ID = %s
        """, (voucher_id, session.get('user_id')))
        conn.commit()

        flash('Voucher unarchived successfully.', 'success')
    except Error as e:
        conn.rollback()
        flash(f'Error unarchiving voucher: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('seller_vouchers.seller_vouchers', view_archived='true'))


@seller_vouchers_bp.route('/update_voucher', methods=['POST'])
def update_voucher():
    voucher_id = request.form.get('voucher_id')  # Get Voucher_ID
    voucher_type = request.form.get('voucherType')
    voucher_name = request.form.get('voucherName')
    voucher_min = request.form.get('voucherMinimum')
    voucher_description = request.form.get('voucherDescription')
    voucher_start_date = request.form.get('voucherStartDate')  
    voucher_end_date = request.form.get('voucherEndDate') 

    # Validate inputs
    if not all([voucher_id, voucher_type, voucher_name, voucher_min]):
        flash('All fields except description are required.', 'danger')
        return redirect(url_for('seller_vouchers.seller_vouchers'))
    
    # Validate that the end date is after the start date
    if voucher_start_date >= voucher_end_date:
        flash('Invalid Input: End Date must be later than Start Date.', 'danger')
        return redirect(url_for('seller_vouchers.seller_vouchers'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the voucher details
        cursor.execute("""
            UPDATE seller_vouchers
            SET Voucher_Type = %s,
                Voucher_Name = %s,
                Voucher_Min = %s,
                Voucher_Description = %s,
                Voucher_Start_Date = %s,
                Voucher_End_Date = %s
            WHERE Voucher_ID = %s AND Seller_ID = %s
        """, (voucher_type, voucher_name, voucher_min, voucher_description, voucher_start_date, voucher_end_date, voucher_id, session.get('user_id')))
        conn.commit()

        flash('Voucher updated successfully!', 'success')
    except Error as e:
        conn.rollback()
        flash(f"Error updating voucher: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('seller_vouchers.seller_vouchers'))


def check_and_notify_vouchers(seller_id):
    """
    Checks for vouchers expiring tomorrow and expired vouchers, sends notifications, and updates statuses.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Get today's and tomorrow's dates
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)

        # Notify for vouchers expiring tomorrow
        query_expiring = """
            SELECT Voucher_ID, Voucher_Name, Voucher_End_Date
            FROM seller_vouchers
            WHERE Seller_ID = %s AND Voucher_End_Date = %s AND Status = 'Active'
        """
        cursor.execute(query_expiring, (seller_id, tomorrow))
        expiring_vouchers = cursor.fetchall()

        for voucher in expiring_vouchers:
            # Check if notification already exists for this voucher
            notification_check_sql = """
                SELECT COUNT(*) AS count
                FROM notifications_seller
                WHERE recipient_id = %s AND notification_type = 'Voucher Expiring'
                AND message LIKE %s
            """
            notification_message_check = f"%Your voucher '{voucher['Voucher_Name']}' is set to expire on {voucher['Voucher_End_Date']}%"
            cursor.execute(notification_check_sql, (seller_id, notification_message_check))
            if cursor.fetchone()["count"] == 0:  # No notification exists
                notification_sql = """
                    INSERT INTO notifications_seller 
                    (recipient_id, recipient_role, notification_type, title, message, is_read)
                    VALUES (%s, 'Seller', 'Voucher Expiring', %s, %s, 0)
                """
                notification_title = "Voucher Expiring Soon"
                notification_message = (
                    f"Your voucher '{voucher['Voucher_Name']}' is set to expire on {voucher['Voucher_End_Date']}."
                )
                cursor.execute(notification_sql, (seller_id, notification_title, notification_message))
                conn.commit()

        # Mark vouchers as expired and notify for expired vouchers
        query_expired = """
            SELECT Voucher_ID, Voucher_Name, Voucher_End_Date
            FROM seller_vouchers
            WHERE Seller_ID = %s AND Voucher_End_Date < %s AND Status = 'Active'
        """
        cursor.execute(query_expired, (seller_id, today))
        expired_vouchers = cursor.fetchall()

        for voucher in expired_vouchers:
            # Update the status to 'Expired'
            update_sql = """
                UPDATE seller_vouchers
                SET Status = 'Expired'
                WHERE Voucher_ID = %s
            """
            cursor.execute(update_sql, (voucher['Voucher_ID'],))
            conn.commit()
            
            # Check if notification already exists for this voucher
            notification_check_sql = """
                SELECT COUNT(*) AS count
                FROM notifications_seller
                WHERE recipient_id = %s AND notification_type = 'Voucher Expired'
                AND message LIKE %s
            """
            notification_message_check = f"%Your voucher '{voucher['Voucher_Name']}' has expired on {voucher['Voucher_End_Date']}%"
            cursor.execute(notification_check_sql, (seller_id, notification_message_check))
            if cursor.fetchone()["count"] == 0:  # No notification exists
                notification_sql = """
                    INSERT INTO notifications_seller 
                    (recipient_id, recipient_role, notification_type, title, message, is_read)
                    VALUES (%s, 'Seller', 'Voucher Expired', %s, %s, 0)
                """
                notification_title = "Voucher Expired"
                notification_message = (
                    f"Your voucher '{voucher['Voucher_Name']}' has expired on {voucher['Voucher_End_Date']}."
                )
                cursor.execute(notification_sql, (seller_id, notification_title, notification_message))
                conn.commit()

        print(f"Notifications sent for {len(expiring_vouchers)} expiring and {len(expired_vouchers)} expired vouchers.")
    except Exception as e:
        print(f"Error checking and notifying vouchers: {e}")
    finally:
        cursor.close()
        conn.close()