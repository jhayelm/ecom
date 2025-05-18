from flask import Blueprint, render_template, request, flash, redirect, url_for
from db_connection import get_db_connection  # Import the DB connection function
from datetime import datetime

# Define the Blueprint for the admin section
admin_courier_management_bp = Blueprint('admin_courier_management', __name__)

@admin_courier_management_bp.route('/admin_courier_management')
def admin_courier_management():
    # Fetch query parameters for search, sort, filter, and pagination
    page = request.args.get('page', 1, type=int)  # Default to page 1
    limit = 10  # Number of couriers per page
    offset = (page - 1) * limit
    search = request.args.get('search', '')  # Search query
    view_status = request.args.get('status', 'Active')  # Filter for status (Active/Archived/Banned)
    sort = request.args.get('sort', 'recent')  # Sort by recent (default) or oldest

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Base query with status filter
        query = """
        SELECT 
            c.Courier_ID,
            CONCAT(c.Firstname, ' ', c.Lastname) AS Full_Name,
            c.Age,
            c.Sex,
            c.Phone,
            c.Email,
            c.Status,
            c.Date_Added
        FROM 
            couriers AS c
        WHERE 
            c.Status = %s
        """
        params = [view_status]

        # Apply search filter
        if search.strip():
            query += """
                AND (
                    c.Firstname LIKE %s OR
                    c.Lastname LIKE %s OR
                    c.Age LIKE %s OR
                    c.Sex LIKE %s OR
                    c.Email LIKE %s OR
                    c.Phone LIKE %s
                )
            """
            params.extend([f"%{search}%"] * 6)

        # Apply sorting
        if sort == 'recent':
            query += " ORDER BY c.Date_Added DESC"
        elif sort == 'oldest':
            query += " ORDER BY c.Date_Added ASC"

        # Add pagination
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, tuple(params))
        couriers = cursor.fetchall()

        # Count total couriers for pagination
        cursor.execute(f"""
            SELECT COUNT(*) AS total
            FROM couriers AS c
            WHERE c.Status = %s
        """ + ("""
            AND (
                c.Firstname LIKE %s OR
                c.Lastname LIKE %s OR
                c.Age LIKE %s OR
                c.Sex LIKE %s OR
                c.Email LIKE %s OR
                c.Phone LIKE %s
            )
        """ if search.strip() else ""), tuple(params[:-2]) if search.strip() else (view_status,))
        total_couriers = cursor.fetchone()['total']
        total_pages = (total_couriers // limit) + (1 if total_couriers % limit else 0)

    except Exception as e:
        flash(f"Error retrieving couriers: {e}", "danger")
        couriers = []
        total_pages = 1
    finally:
        cursor.close()
        conn.close()

    return render_template(
        'admin_courier_management.html',
        couriers=couriers,
        page=page,
        total_pages=total_pages,
        search=search,
        current_status=view_status,
        limit=limit,
        selected_sort=sort
    )


@admin_courier_management_bp.route('/archive_courier/<int:courier_id>', methods=['POST'])
def archive_courier(courier_id):
    """Set the status of a courier to 'Archived'."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the courier's status to 'Archived'
        cursor.execute("""
            UPDATE couriers
            SET Status = 'Archived'
            WHERE Courier_ID = %s
        """, (courier_id,))
        conn.commit()

        flash('Courier archived successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f"Error archiving courier: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_courier_management.admin_courier_management'))


@admin_courier_management_bp.route('/unarchive_courier/<int:courier_id>', methods=['POST'])
def unarchive_courier(courier_id):
    """Set the status of a courier back to 'Active'."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the courier's status to 'Active'
        cursor.execute("""
            UPDATE couriers
            SET Status = 'Active'
            WHERE Courier_ID = %s
        """, (courier_id,))
        conn.commit()

        flash('Courier unarchived successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f"Error unarchiving courier: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_courier_management.admin_courier_management', status='Archived'))


@admin_courier_management_bp.route('/ban_courier/<int:courier_id>', methods=['POST'])
def ban_courier(courier_id):
    """Set the status of a courier to 'Banned'."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the courier's status to 'Banned'
        cursor.execute("""
            UPDATE couriers
            SET Status = 'Banned'
            WHERE Courier_ID = %s
        """, (courier_id,))
        conn.commit()

        flash('Courier banned successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f"Error banning courier: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_courier_management.admin_courier_management'))


@admin_courier_management_bp.route('/unban_courier/<int:courier_id>', methods=['POST'])
def unban_courier(courier_id):
    """Set the status of a courier back to 'Active'."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the courier's status to 'Active'
        cursor.execute("""
            UPDATE couriers
            SET Status = 'Active'
            WHERE Courier_ID = %s
        """, (courier_id,))
        conn.commit()

        flash('Courier unbanned successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f"Error unbanning courier: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_courier_management.admin_courier_management', status='Banned'))


@admin_courier_management_bp.route('/add_courier', methods=['POST'])
def add_courier():
    """Handle the form submission to add a new courier."""
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    birthdate = request.form['birthdate']
    sex = request.form['sex']
    phone = request.form['phone']
    email = request.form['email']

    # Calculate age based on birthdate
    birth_date_obj = datetime.strptime(birthdate, '%Y-%m-%d')
    today = datetime.today()
    age = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert the new courier into the couriers table
        cursor.execute("""
            INSERT INTO couriers (Firstname, Lastname, Age, Sex, Phone, Email, Status)
            VALUES (%s, %s, %s, %s, %s, %s, 'Active')
        """, (firstname, lastname, age, sex, phone, email))
        conn.commit()

        flash('Courier added successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f"Error adding courier: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_courier_management.admin_courier_management'))
