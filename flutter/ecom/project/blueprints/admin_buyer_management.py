from flask import Blueprint, render_template, request, flash, redirect, url_for
from db_connection import get_db_connection  # Import the DB connection function

# Define the Blueprint for the admin section
admin_buyer_management_bp = Blueprint('admin_buyer_management', __name__)

@admin_buyer_management_bp.route('/admin_buyer_management')
def admin_buyer_management():
    # Fetch query parameters for search, sort, filter, and pagination
    page = request.args.get('page', 1, type=int)  # Default to page 1
    limit = 10  # Number of buyers per page
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
            ba.Buyer_ID,
            CONCAT(bpi.Firstname, ' ', IFNULL(bpi.Middlename, ''), ' ', bpi.Lastname, ' ', IFNULL(bpi.Suffix, '')) AS Full_Name,
            bpi.Age,
            bpi.Sex,
            ba.Phone AS Phone_Number,
            ba.Email AS Email_Address,
            ba.Status,
            ba.timestamp AS Date_Registered
        FROM 
            buyer_accounts AS ba
        LEFT JOIN 
            buyer_personal_info AS bpi ON ba.Personal_ID = bpi.Personal_ID
        WHERE 
            ba.Status = %s
        """
        params = [view_status]

        # Apply search filter
        if search.strip():
            query += """
                AND (
                    bpi.Firstname LIKE %s OR
                    bpi.Middlename LIKE %s OR
                    bpi.Lastname LIKE %s OR
                    bpi.Age LIKE %s OR
                    bpi.Sex LIKE %s OR
                    ba.Email LIKE %s OR
                    ba.Phone LIKE %s
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
        buyers = cursor.fetchall()

        # Count total buyers for pagination
        cursor.execute(f"""
            SELECT COUNT(*) AS total
            FROM buyer_accounts AS ba
            LEFT JOIN buyer_personal_info AS bpi ON ba.Personal_ID = bpi.Personal_ID
            WHERE ba.Status = %s
        """ + ("""
            AND (
                bpi.Firstname LIKE %s OR
                bpi.Middlename LIKE %s OR
                bpi.Lastname LIKE %s OR
                bpi.Age LIKE %s OR
                bpi.Sex LIKE %s OR
                ba.Email LIKE %s OR
                ba.Phone LIKE %s
            )
        """ if search.strip() else ""),
        tuple(params[:-2]) if search.strip() else (view_status,))
        total_buyers = cursor.fetchone()['total']
        total_pages = (total_buyers // limit) + (1 if total_buyers % limit else 0)

    except Exception as e:
        flash(f"Error retrieving buyers: {e}", "danger")
        buyers = []
        total_pages = 1
    finally:
        cursor.close()
        conn.close()

    return render_template(
        'admin_buyer_management.html',
        buyers=buyers,
        page=page,
        total_pages=total_pages,
        search=search,
        current_status=view_status,
        limit=limit,
        selected_sort=sort
    )


@admin_buyer_management_bp.route('/archive_buyer/<int:buyer_id>', methods=['POST'])
def archive_buyer(buyer_id):
    """Set the status of a buyer to 'Archived'."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the buyer's status to 'Archived'
        cursor.execute("""
            UPDATE buyer_accounts
            SET Status = 'Archived'
            WHERE Buyer_ID = %s
        """, (buyer_id,))
        conn.commit()

        flash('Buyer archived successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f"Error archiving buyer: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_buyer_management.admin_buyer_management'))


@admin_buyer_management_bp.route('/unarchive_buyer/<int:buyer_id>', methods=['POST'])
def unarchive_buyer(buyer_id):
    """Set the status of a buyer back to 'Registered'."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the buyer's status to 'Registered'
        cursor.execute("""
            UPDATE buyer_accounts
            SET Status = 'Registered'
            WHERE Buyer_ID = %s
        """, (buyer_id,))
        conn.commit()

        flash('Buyer unarchived successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f"Error unarchiving buyer: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_buyer_management.admin_buyer_management', status='Archived'))


@admin_buyer_management_bp.route('/ban_buyer/<int:buyer_id>', methods=['POST'])
def ban_buyer(buyer_id):
    """Set the status of a buyer to 'Banned'."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the buyer's status to 'Banned'
        cursor.execute("""
            UPDATE buyer_accounts
            SET Status = 'Banned'
            WHERE Buyer_ID = %s
        """, (buyer_id,))
        conn.commit()

        flash('Buyer banned successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f"Error banning buyer: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_buyer_management.admin_buyer_management'))


@admin_buyer_management_bp.route('/unban_buyer/<int:buyer_id>', methods=['POST'])
def unban_buyer(buyer_id):
    """Set the status of a buyer back to 'Registered'."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the buyer's status to 'Registered'
        cursor.execute("""
            UPDATE buyer_accounts
            SET Status = 'Registered'
            WHERE Buyer_ID = %s
        """, (buyer_id,))
        conn.commit()

        flash('Buyer unbanned successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f"Error unbanning buyer: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_buyer_management.admin_buyer_management', status='Banned'))
