from flask import Blueprint, render_template, session, g
from db_connection import get_db_connection


seller_bp = Blueprint('seller', __name__)

@seller_bp.before_app_request
def seller_fetch_unread_notifications_count():
    if 'user_id' in session:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Query to count unread notifications
            query = """
                SELECT COUNT(*) AS unread_count
                FROM notifications_seller
                WHERE recipient_id = %s AND is_read = 0
            """
            cursor.execute(query, (session['user_id'],))
            g.seller_unread_notifications_count = cursor.fetchone()['unread_count']
        except Exception as e:
            g.seller_unread_notifications_count = 0 
        finally:
            cursor.close()
            conn.close()
    else:
        g.seller_unread_notifications_count = 0


@seller_bp.route('/logout')
def logout():
    session.clear()  # Clear the session to reset to guest mode
    return render_template('buyer_homepage.html', seller_name="Guest")
