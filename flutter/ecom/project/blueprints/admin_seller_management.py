from flask import Blueprint, render_template, request, flash, redirect, url_for
from db_connection import get_db_connection

# Define the Blueprint for the admin section
admin_seller_management_bp = Blueprint('admin_seller_management', __name__)

@admin_seller_management_bp.route('/admin_seller_management')
def admin_seller_management():
    # Fetch query parameters for search, sort, filter, and pagination
    page = request.args.get('page', 1, type=int)  # Default to page 1
    limit = 10  # Number of sellers per page
    offset = (page - 1) * limit
    search = request.args.get('search', '')  # Search query
    view_status = request.args.get('status', 'Registered')  # Filter for status (Active/Archived/Banned)
    sort = request.args.get('sort', 'recent')  # Sort by recent (default) or oldest

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Base query with status filter
        query = """
        SELECT 
            sa.Seller_ID,
            CONCAT(spi.Firstname, ' ', IFNULL(spi.Middlename, ''), ' ', spi.Lastname, ' ', IFNULL(spi.Suffix, '')) AS Full_Name,
            spi.Age,
            spi.Sex,
            sa.Phone AS Phone_Number,
            sa.Email AS Email_Address,
            sa.Status,
            sa.timestamp AS Date_Registered
        FROM 
            seller_accounts AS sa
        LEFT JOIN 
            seller_personal_info AS spi ON sa.Personal_ID = spi.Personal_ID
        WHERE 
            sa.Status = %s
        """
        params = [view_status]

        # Apply search filter
        if search.strip():
            query += """
                AND (
                    spi.Firstname LIKE %s OR
                    spi.Middlename LIKE %s OR
                    spi.Lastname LIKE %s OR
                    spi.Age LIKE %s OR
                    spi.Sex LIKE %s OR
                    sa.Email LIKE %s OR
                    sa.Phone LIKE %s
                )
            """
            params.extend([f"%{search}%"] * 7)

        # Apply sorting
        if sort == 'recent':
            query += " ORDER BY Date_Registered DESC"
        elif sort == 'oldest':
            query += " ORDER BY Date_Registered ASC"

        # Add pagination
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, tuple(params))
        sellers = cursor.fetchall()

        # Count total sellers for pagination
        cursor.execute(f"""
            SELECT COUNT(*) AS total
            FROM seller_accounts AS sa
            LEFT JOIN seller_personal_info AS spi ON sa.Personal_ID = spi.Personal_ID
            WHERE sa.Status = %s
        """ + ("""
            AND (
                spi.Firstname LIKE %s OR
                spi.Middlename LIKE %s OR
                spi.Lastname LIKE %s OR
                spi.Age LIKE %s OR
                spi.Sex LIKE %s OR
                sa.Email LIKE %s OR
                sa.Phone LIKE %s
            )
        """ if search.strip() else ""),
        tuple(params[:-2]) if search.strip() else (view_status,))
        total_sellers = cursor.fetchone()['total']
        total_pages = (total_sellers // limit) + (1 if total_sellers % limit else 0)

    except Exception as e:
        flash(f"Error retrieving sellers: {e}", "danger")
        sellers = []
        total_pages = 1
    finally:
        cursor.close()
        conn.close()

    return render_template(
        'admin_seller_management.html',
        sellers=sellers,
        page=page,
        total_pages=total_pages,
        search=search,
        current_status=view_status,
        limit=limit,
        selected_sort=sort
    )


@admin_seller_management_bp.route('/archive_seller/<int:seller_id>', methods=['POST'])
def archive_seller(seller_id):
    """Set the status of a seller to 'Archived'."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the seller's status to 'Archived'
        cursor.execute("""
            UPDATE seller_accounts
            SET Status = 'Archived'
            WHERE Seller_ID = %s
        """, (seller_id,))
        conn.commit()

        flash('Seller archived successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f"Error archiving seller: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_seller_management.admin_seller_management'))


@admin_seller_management_bp.route('/unarchive_seller/<int:seller_id>', methods=['POST'])
def unarchive_seller(seller_id):
    """Set the status of a seller back to 'Registered'."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the seller's status to 'Registered'
        cursor.execute("""
            UPDATE seller_accounts
            SET Status = 'Registered'
            WHERE Seller_ID = %s
        """, (seller_id,))
        conn.commit()

        flash('Seller unarchived successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f"Error unarchiving seller: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_seller_management.admin_seller_management', status='Archived'))


@admin_seller_management_bp.route('/ban_seller/<int:seller_id>', methods=['POST'])
def ban_seller(seller_id):
    """Set the status of a seller to 'Banned'."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the seller's status to 'Banned'
        cursor.execute("""
            UPDATE seller_accounts
            SET Status = 'Banned'
            WHERE Seller_ID = %s
        """, (seller_id,))
        conn.commit()

        flash('Seller banned successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f"Error banning seller: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_seller_management.admin_seller_management'))


@admin_seller_management_bp.route('/unban_seller/<int:seller_id>', methods=['POST'])
def unban_seller(seller_id):
    """Set the status of a seller back to 'Registered'."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the seller's status to 'Registered'
        cursor.execute("""
            UPDATE seller_accounts
            SET Status = 'Registered'
            WHERE Seller_ID = %s
        """, (seller_id,))
        conn.commit()

        flash('Seller unbanned successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f"Error unbanning seller: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_seller_management.admin_seller_management', status='Banned'))


@admin_seller_management_bp.route('/approve_seller/<int:seller_id>', methods=['POST'])
def approve_seller(seller_id):
    """Set the status of a seller to 'Registered' and create a notification."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Ensure dictionary-style access

        # Update the seller's status to 'Registered'
        cursor.execute("""
            UPDATE seller_accounts
            SET Status = 'Registered'
            WHERE Seller_ID = %s
        """, (seller_id,))
        
        # Fetch seller information for notification
        cursor.execute("""
            SELECT Seller_ID, Email
            FROM seller_accounts
            WHERE Seller_ID = %s
        """, (seller_id,))
        seller = cursor.fetchone()

        # Insert a notification into the notifications_seller table
        if seller:
            notification_query = """
                INSERT INTO notifications_seller (recipient_id, recipient_role, notification_type, title, message, is_read)
                VALUES (%s, 'Seller', 'Approval', 'Account Approved', 'Your seller account has been approved!', 0)
            """
            cursor.execute(notification_query, (seller['Seller_ID'],))

        conn.commit()
        flash('Seller approved successfully and notification sent.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f"Error approving seller: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_seller_management.admin_seller_management', status='Pending'))


@admin_seller_management_bp.route('/decline_seller/<int:seller_id>', methods=['POST'])
def decline_seller(seller_id):
    """Set the status of a seller to 'Declined'."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the seller's status to 'Declined'
        cursor.execute("""
            UPDATE seller_accounts
            SET Status = 'Declined'
            WHERE Seller_ID = %s
        """, (seller_id,))
        conn.commit()

        flash('Seller declined successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f"Error declining seller: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_seller_management.admin_seller_management', status='Pending'))
