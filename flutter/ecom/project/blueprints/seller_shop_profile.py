from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db_connection import get_db_connection  

# Blueprint initialization
seller_shop_profile_bp = Blueprint('seller_shop_profile', __name__)

# Route to display the shop profile setup form
@seller_shop_profile_bp.route('/seller_shop_profile')
def seller_shop_profile():
    if 'user_id' not in session:
        flash('You need to log in to view your shop profile.', 'danger')
        return redirect(url_for('login.login'))

    shop_profile = fetch_shop_profile()
    seller_id = session['user_id']

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get shop information
        query_shop = "SELECT * FROM seller_shop WHERE Seller_ID = %s"
        cursor.execute(query_shop, (seller_id,))
        shop = cursor.fetchone()

        if shop:
            # Calculate average rating and participant count
            query_rating = """
                SELECT AVG(Rating) AS Average_Rating, COUNT(*) AS Participants
                FROM shop_rating
                WHERE Shop_ID = %s
            """
            cursor.execute(query_rating, (shop['Shop_ID'],))
            rating_data = cursor.fetchone()

            # Add rating data to the shop dictionary
            shop['Average_Rating'] = round(rating_data['Average_Rating'], 1) if rating_data['Average_Rating'] else 0
            shop['Participants'] = rating_data['Participants'] if rating_data['Participants'] else 0

            # Get total feedbacks
            query_feedbacks = """
                SELECT COUNT(*) AS Total_Feedbacks
                FROM shop_feedbacks
                WHERE Shop_ID = %s
            """
            cursor.execute(query_feedbacks, (shop['Shop_ID'],))
            feedback_data = cursor.fetchone()

            # Add total feedbacks to the shop dictionary
            shop['Total_Feedbacks'] = feedback_data['Total_Feedbacks'] if feedback_data['Total_Feedbacks'] else 0

    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')
        shop = None
    finally:
        cursor.close()
        conn.close()

    return render_template('seller_shop_profile.html', shop=shop, shop_profile=shop_profile)


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

@seller_shop_profile_bp.route('/seller_shop_profile/update', methods=['POST'])
def update_shop_profile():
    if 'user_id' not in session:
        flash('You need to log in to update your shop profile.', 'danger')
        return redirect(url_for('login.login'))

    shop_id = request.form.get('shop_id')
    shop_name = request.form.get('shopName')
    shop_description = request.form.get('shopDescription')
    shop_profile_file = request.files.get('shopProfilePicture')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update query
        if shop_profile_file:
            profile_picture_blob = shop_profile_file.read()
            query = """
                UPDATE seller_shop 
                SET Shop_Name = %s, Shop_Description = %s, Shop_Profile = %s 
                WHERE Shop_ID = %s
            """
            cursor.execute(query, (shop_name, shop_description, profile_picture_blob, shop_id))
        else:
            query = """
                UPDATE seller_shop 
                SET Shop_Name = %s, Shop_Description = %s 
                WHERE Shop_ID = %s
            """
            cursor.execute(query, (shop_name, shop_description, shop_id))

        conn.commit()
        flash('Shop details updated successfully!', 'success')
    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('seller_shop_profile.seller_shop_profile'))
