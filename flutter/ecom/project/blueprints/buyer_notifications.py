from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from db_connection import get_db_connection

buyer_notifications_bp = Blueprint('buyer_notifications', __name__)

@buyer_notifications_bp.route('/buyer_notifications')
def buyer_notifications():
    if 'user_id' not in session:
        flash('You need to log in to view notifications.', 'danger')
        return redirect(url_for('login.login'))
    
    buyer_id = session['user_id']
    mark_all_notifications_as_read(buyer_id)

    page = request.args.get('page', 1, type=int)  # Current page number
    limit = 10  # Notifications per page
    offset = (page - 1) * limit  # Calculate offset
    selected_type = request.args.get('type', 'All')  # Selected notification type
    view_archived = request.args.get('view_archived', 'false') == 'true'  # Show archived or active
    sort_order = request.args.get('sort', 'recent')  # Sort order (recent or oldest)
    search_query = request.args.get('search', '').strip()  # Search term

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch unique notification types for the dropdown
        cursor.execute("""
            SELECT DISTINCT notification_type
            FROM notifications_buyer
            WHERE recipient_id = %s
        """, (buyer_id,))
        notification_types = cursor.fetchall()

        # Base query
        query = """
            SELECT notification_id, title, message, created_at, is_read, notification_type
            FROM notifications_buyer
            WHERE recipient_id = %s
        """
        params = [buyer_id]

        # Filter by archived or active
        if view_archived:
            query += " AND status = 'Archived'"
        else:
            query += " AND status = 'Active'"

        # Filter by notification type
        if selected_type != 'All':
            query += " AND notification_type = %s"
            params.append(selected_type)

        # Apply search filter
        if search_query:
            query += " AND (title LIKE %s OR message LIKE %s)"
            search_term = f"%{search_query}%"
            params.extend([search_term, search_term])

        # Sort order
        if sort_order == 'recent':
            query += " ORDER BY created_at DESC"
        elif sort_order == 'oldest':
            query += " ORDER BY created_at ASC"

        # Pagination
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, tuple(params))
        notifications = cursor.fetchall()

        # Count total notifications for pagination
        count_query = """
            SELECT COUNT(*) AS total
            FROM notifications_buyer
            WHERE recipient_id = %s
        """
        count_params = [buyer_id]

        if view_archived:
            count_query += " AND status = 'Archived'"
        else:
            count_query += " AND status = 'Active'"

        if selected_type != 'All':
            count_query += " AND notification_type = %s"
            count_params.append(selected_type)

        if search_query:
            count_query += " AND (title LIKE %s OR message LIKE %s)"
            count_params.extend([search_term, search_term])

        cursor.execute(count_query, tuple(count_params))
        total_notifications = cursor.fetchone()['total']
        total_pages = (total_notifications + limit - 1) // limit

    except Exception as e:
        flash(f"An error occurred while fetching notifications: {e}", "danger")
        notifications = []
        total_pages = 1
        notification_types = []
    finally:
        cursor.close()
        conn.close()

    return render_template(
        'buyer_notifications.html',
        notifications=notifications,
        page=page,
        total_pages=total_pages,
        view_archived=view_archived,
        selected_sort=sort_order,
        selected_type=selected_type,
        notification_types=notification_types,
        search_query=search_query
    )
    
@buyer_notifications_bp.route('/buyer_notifications/unread_count', methods=['GET'])
def get_unread_notifications_count():
    """
    API endpoint to fetch the unread notifications count.
    """
    if 'user_id' not in session:
        return jsonify({'unread_count': 0})  # Return 0 if user is not logged in

    buyer_id = session['user_id']
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to count unread notifications
        query = """
            SELECT COUNT(*) AS unread_count
            FROM notifications_buyer
            WHERE recipient_id = %s AND is_read = 0
        """
        cursor.execute(query, (buyer_id,))
        unread_count = cursor.fetchone()[0]
    except Exception as e:
        print(f"Error fetching unread notifications count: {e}")
        unread_count = 0
    finally:
        cursor.close()
        conn.close()

    return jsonify({'unread_count': unread_count})


def mark_all_notifications_as_read(buyer_id):
    """
    Marks all unread notifications as read for the given buyer.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the is_read status to True for all unread notifications
        query = """
            UPDATE notifications_buyer
            SET is_read = 1
            WHERE recipient_id = %s AND is_read = 0
        """
        cursor.execute(query, (buyer_id,))
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Error marking notifications as read: {e}")
    finally:
        cursor.close()
        conn.close()


# Archive Notification
@buyer_notifications_bp.route('/buyer_notifications/archive/<int:notification_id>', methods=['POST'])
def archive_notification(notification_id):
    if 'user_id' not in session:
        flash('You need to log in to archive notifications.', 'danger')
        return redirect(url_for('login.login'))

    buyer_id = session['user_id']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the status of the notification to "Archived"
        query = """
            UPDATE notifications_buyer
            SET status = 'Archived'
            WHERE notification_id = %s AND recipient_id = %s
        """
        cursor.execute(query, (notification_id, buyer_id))
        conn.commit()
        flash('Notification archived successfully.', 'success')

    except Exception as e:
        conn.rollback()
        flash(f"An error occurred while archiving the notification: {e}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('buyer_notifications.buyer_notifications'))


# Unarchive Notification
@buyer_notifications_bp.route('/buyer_notifications/unarchive/<int:notification_id>', methods=['POST'])
def unarchive_notification(notification_id):
    if 'user_id' not in session:
        flash('You need to log in to unarchive notifications.', 'danger')
        return redirect(url_for('login.login'))

    buyer_id = session['user_id']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the status of the notification to "Active"
        query = """
            UPDATE notifications_buyer
            SET status = 'Active'
            WHERE notification_id = %s AND recipient_id = %s
        """
        cursor.execute(query, (notification_id, buyer_id))
        conn.commit()
        flash('Notification unarchived successfully.', 'success')

    except Exception as e:
        conn.rollback()
        flash(f"An error occurred while unarchiving the notification: {e}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('buyer_notifications.buyer_notifications', view_archived='true'))


# Delete Notification
@buyer_notifications_bp.route('/buyer_notifications/delete/<int:notification_id>', methods=['POST'])
def delete_notification(notification_id):
    if 'user_id' not in session:
        flash('You need to log in to delete notifications.', 'danger')
        return redirect(url_for('login.login'))

    buyer_id = session['user_id']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Delete the notification from the database
        query = """
            DELETE FROM notifications_buyer
            WHERE notification_id = %s AND recipient_id = %s
        """
        cursor.execute(query, (notification_id, buyer_id))
        conn.commit()
        flash('Notification deleted successfully.', 'success')

    except Exception as e:
        conn.rollback()
        flash(f"An error occurred while deleting the notification: {e}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('buyer_notifications.buyer_notifications'))


# Mark Notification as Read
@buyer_notifications_bp.route('/buyer_notifications/mark_as_read/<int:notification_id>', methods=['POST'])
def mark_as_read(notification_id):
    if 'user_id' not in session:
        flash('You need to log in to update notifications.', 'danger')
        return redirect(url_for('login.login'))

    buyer_id = session['user_id']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the is_read status to True
        query = """
            UPDATE notifications_buyer
            SET is_read = 1
            WHERE notification_id = %s AND recipient_id = %s
        """
        cursor.execute(query, (notification_id, buyer_id))
        conn.commit()

        flash('Notification marked as read.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred while updating the notification: {e}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('buyer_notifications.buyer_notifications'))


# Mark All Notifications as Read
@buyer_notifications_bp.route('/buyer_notifications/mark_all_as_read', methods=['POST'])
def mark_all_as_read():
    if 'user_id' not in session:
        flash('You need to log in to mark notifications as read.', 'danger')
        return redirect(url_for('login.login'))

    buyer_id = session['user_id']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update all unread notifications to "read"
        query = """
            UPDATE notifications_buyer
            SET is_read = 1
            WHERE recipient_id = %s AND is_read = 0
        """
        cursor.execute(query, (buyer_id,))
        conn.commit()

        flash('All notifications marked as read successfully.', 'success')

    except Exception as e:
        conn.rollback()
        flash(f"An error occurred while marking notifications as read: {e}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('buyer_notifications.buyer_notifications'))
