from flask import Blueprint, render_template, session, g, flash
from db_connection import get_db_connection


seller_messages_bp = Blueprint('seller_messages', __name__)

@seller_messages_bp.route('/seller_messages')
def seller_messages():
    shop_profile = fetch_shop_profile()

    return render_template('seller_messages.html', shop_profile=shop_profile)


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

@seller_messages_bp.route('/logout')
def logout():
    session.clear()  # Clear the session to reset to guest mode
    return render_template('buyer_homepage.html', seller_name="Guest")
