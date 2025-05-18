from flask import Blueprint, render_template, session, g
from db_connection import get_db_connection

# Define the Blueprint for the admin section
admin_bp = Blueprint('admin', __name__)


@admin_bp.before_app_request
def admin_fetch_unread_notifications_count():
    if 'user_id' in session:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Query to count unread notifications
            query = """
                SELECT COUNT(*) AS unread_count
                FROM notifications_admin
                WHERE recipient_id = %s AND is_read = 0
            """
            cursor.execute(query, (session['user_id'],))
            g.admin_unread_notifications_count = cursor.fetchone()['unread_count']
        except Exception as e:
            g.admin_unread_notifications_count = 0  # Default to 0 if an error occurs
        finally:
            cursor.close()
            conn.close()
    else:
        g.admin_unread_notifications_count = 0

# Route for Admin Dashboard
@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# Route for User Management (Managing Buyers, Sellers, Couriers)
@admin_bp.route('/admin_user_management')
def admin_user_management():
    return render_template('admin_user_management.html')

# Route for Commission Management
@admin_bp.route('/admin_commission_management')
def admin_commission_management():
    return render_template('admin_commission_management.html')

# Route for Reports
@admin_bp.route('/admin_reports')
def admin_reports():
    return render_template('admin_reports.html')

# Route for Message Center
@admin_bp.route('/admin_message_center')
def admin_message_center():
    return render_template('admin_message_center.html')


# Route for Admin Settings
@admin_bp.route('/admin_settings')
def admin_settings():
    return render_template('admin_settings.html')
