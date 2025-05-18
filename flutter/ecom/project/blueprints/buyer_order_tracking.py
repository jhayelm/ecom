from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from db_connection import get_db_connection

buyer_order_tracking_bp = Blueprint('buyer_order_tracking', __name__)

@buyer_order_tracking_bp.route('/buyer_order_tracking')
def buyer_order_tracking():
    page = request.args.get('page', 1, type=int)  # Current page number
    limit = 5  # Number of orders per page
    offset = (page - 1) * limit  # Offset for pagination
    selected_filter = request.args.get('filter', 'All')  # Order status filter
    selected_sort = request.args.get('sort', 'recent')  # Sort by date
    search = request.args.get('search', '')  # Search term

    buyer_id = session.get('user_id')  # Fetch buyer ID from the session
    if not buyer_id:
        flash('Please log in to view your orders.', 'warning')
        return render_template('buyer_order_tracking.html', orders=[], page=1, total_pages=1)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Base query to fetch orders for the buyer
        query = """
            SELECT o.Order_ID, p.Product_ID, pi.Product_Name, pi.Product_Main_Picture, s.Shop_ID,
                s.Shop_Name, s.Shop_Profile, o.Quantity, 
                o.Total_Amount, o.Payment_Method, o.Status, o.Date_Ordered,
                c.Color_Name AS Product_Color
            FROM buyer_orders o
            JOIN products p ON o.Product_ID = p.Product_ID
            JOIN product_info pi ON p.Product_Info_ID = pi.Product_Info_ID
            JOIN product_color c ON pi.Product_Info_ID = c.Product_Info_ID
            JOIN seller_shop s ON o.Shop_ID = s.Shop_ID
            WHERE o.Buyer_ID = %s
        """

        params = [buyer_id]

        # Apply status filter if selected
        if selected_filter != 'All':
            query += " AND o.Status = %s"
            params.append(selected_filter)

        # Apply search term filter
        if search:
            query += """
                AND (pi.Product_Name LIKE %s OR s.Shop_Name LIKE %s 
                     OR o.Status LIKE %s OR o.Payment_Method LIKE %s)
            """
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term, search_term])

        # Apply sorting
        if selected_sort == 'recent':
            query += " ORDER BY o.Date_Ordered DESC"
        elif selected_sort == 'oldest':
            query += " ORDER BY o.Date_Ordered ASC"

        # Apply pagination
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        # Execute the query
        cursor.execute(query, tuple(params))
        orders = cursor.fetchall()

        # Get the total count of orders for pagination
        count_query = "SELECT COUNT(*) AS total FROM buyer_orders o WHERE o.Buyer_ID = %s"
        count_params = [buyer_id]

        # Add filter and search term conditions to the count query
        if selected_filter != 'All':
            count_query += " AND o.Status = %s"
            count_params.append(selected_filter)
        if search:
            count_query += """
                AND (pi.Product_Name LIKE %s OR s.Shop_Name LIKE %s 
                     OR o.Status LIKE %s OR o.Payment_Method LIKE %s)
            """
            count_params.extend([search_term, search_term, search_term, search_term])

        cursor.execute(count_query, tuple(count_params))
        total_orders = cursor.fetchone()['total']
        total_pages = (total_orders // limit) + (1 if total_orders % limit > 0 else 0)

    except Exception as e:
        flash(f"Error fetching orders: {e}", 'danger')
        orders = []
        total_pages = 1
    finally:
        cursor.close()
        conn.close()

    # Render the template with order data
    return render_template(
        'buyer_order_tracking.html',
        orders=orders,
        page=page,
        total_pages=total_pages,
        selected_filter=selected_filter,
        selected_sort=selected_sort,
        search=search
    )


@buyer_order_tracking_bp.route('/mark_as_received/<int:order_id>', methods=['POST'])
def mark_as_received(order_id):
    if not session.get('user_id'):
        flash('Please log in to update your order.', 'warning')
        return redirect('/buyer_order_tracking')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Step 1: Update the order status to Completed
        update_query = """
            UPDATE buyer_orders 
            SET Status = 'Completed' 
            WHERE Order_ID = %s AND Buyer_ID = %s
        """
        cursor.execute(update_query, (order_id, session['user_id']))
        conn.commit()

        if cursor.rowcount > 0:
            # Step 2: Fetch Order Details
            fetch_order_query = """
                SELECT 
                    bo.Buyer_ID,
                    sa.Seller_ID,
                    spi.Firstname AS Seller_Firstname,
                    spi.Lastname AS Seller_Lastname,
                    pi.Product_Name,
                    pc.Color_Name,
                    bo.Quantity
                FROM buyer_orders bo
                JOIN seller_accounts sa ON bo.Seller_ID = sa.Seller_ID
                JOIN seller_personal_info spi ON sa.Personal_ID = spi.Personal_ID
                JOIN products p ON bo.Product_ID = p.Product_ID
                JOIN product_info pi ON p.Product_Info_ID = pi.Product_Info_ID
                JOIN product_color pc ON pc.Product_Info_ID = pi.Product_Info_ID
                WHERE bo.Order_ID = %s
            """
            cursor.execute(fetch_order_query, (order_id,))
            order_info = cursor.fetchone()

            if order_info:
                buyer_id = order_info[0]
                seller_id = order_info[1]
                seller_name = f"{order_info[2]} {order_info[3]}"
                product_name = order_info[4]
                color_name = order_info[5]
                quantity = order_info[6]

                # Step 3: Notify the Seller
                seller_notification_query = """
                    INSERT INTO notifications_seller
                    (recipient_id, recipient_role, notification_type, title, message, is_read, created_at)
                    VALUES (%s, 'Seller', 'Order Update', %s, %s, 0, NOW())
                """
                seller_notification_title = "Order Completed"
                seller_notification_message = (
                    f"The order {product_name} - {quantity} unit/s ({color_name}) has been marked as received by the buyer."
                )
                cursor.execute(seller_notification_query, 
                               (seller_id, seller_notification_title, seller_notification_message))

                # Step 4: Notify the Admin
                admin_notification_query = """
                    INSERT INTO notifications_admin
                    (recipient_id, recipient_role, notification_type, title, message, is_read, created_at)
                    VALUES (%s, 'Admin', 'Order Update', %s, %s, 0, NOW())
                """
                admin_id = 1  # Update as needed
                admin_notification_title = "Order Completed"
                admin_notification_message = (
                    f"The order {product_name} - {quantity} unit/s ({color_name}) has been marked as received by the buyer."
                )
                cursor.execute(admin_notification_query, 
                               (admin_id, admin_notification_title, admin_notification_message))

                # Commit notifications
                conn.commit()

                flash('Order status updated to Completed, and notifications sent.', 'success')
            else:
                flash('Order details not found. Notifications not sent.', 'warning')
        else:
            flash('Failed to update order status. Please try again.', 'danger')

    except Exception as e:
        conn.rollback()
        flash(f"An error occurred: {str(e)}", 'danger')
    finally:
        cursor.close()
        conn.close()

    # Redirect back to the buyer order tracking page
    return redirect('/buyer_order_tracking')



def rating_exists(order_id, buyer_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        check_query = """
            SELECT COUNT(*) AS rating_count
            FROM shop_rating sr
            JOIN buyer_orders bo ON sr.Product_ID = bo.Product_ID
            WHERE bo.Order_ID = %s AND sr.Sender_ID = %s
        """
        cursor.execute(check_query, (order_id, buyer_id))
        result = cursor.fetchone()
        return result['rating_count'] > 0
    except Exception as e:
        flash(f"Error checking rating: {e}", 'danger')
        return False
    finally:
        cursor.close()
        conn.close()


@buyer_order_tracking_bp.route('/submit_rating/<int:order_id>', methods=['POST'])
def submit_rating(order_id):
    if not session.get('user_id'):
        flash('Please log in to rate the shop.', 'warning')
        return redirect(url_for('buyer_order_tracking.buyer_order_tracking'))

    shop_id = request.form.get('shop_id')
    rating = request.form.get('rating')
    buyer_id = session.get('user_id')
    buyer_name = session.get('user_name', 'Anonymous')

    if rating_exists(order_id, buyer_id):
        flash('You have already submitted a rating for this order.', 'info')
        return redirect(url_for('buyer_order_tracking.buyer_order_tracking'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch the Seller_ID and Product_ID related to the order
        seller_query = """
            SELECT s.Seller_ID, o.Product_ID
            FROM buyer_orders o
            JOIN seller_shop s ON o.Shop_ID = s.Shop_ID
            WHERE o.Order_ID = %s
        """
        cursor.execute(seller_query, (order_id,))
        seller_data = cursor.fetchone()

        if not seller_data:
            flash('Invalid order. Please try again.', 'danger')
            return redirect(url_for('buyer_order_tracking.buyer_order_tracking'))

        # Insert the rating into the database
        insert_query = """
            INSERT INTO shop_rating (Shop_ID, Seller_ID, Product_ID, Rating, Sender_ID, Sender_Name)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (shop_id, seller_data['Seller_ID'], seller_data['Product_ID'], rating, buyer_id, buyer_name))
        conn.commit()
        flash('Thank you for your rating!', 'success')
    except Exception as e:
        flash(f"Error submitting rating: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('buyer_order_tracking.buyer_order_tracking'))


def feedback_exists(order_id, buyer_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        check_query = """
            SELECT COUNT(*) AS feedback_count
            FROM shop_feedbacks sf
            JOIN buyer_orders bo ON sf.Product_ID = bo.Product_ID
            WHERE bo.Order_ID = %s AND sf.Sender_ID = %s
        """
        cursor.execute(check_query, (order_id, buyer_id))
        result = cursor.fetchone()
        return result['feedback_count'] > 0
    except Exception as e:
        flash(f"Error checking feedback: {e}", 'danger')
        return False
    finally:
        cursor.close()
        conn.close()


@buyer_order_tracking_bp.route('/submit_feedback/<int:order_id>', methods=['POST'])
def submit_feedback(order_id):
    if not session.get('user_id'):
        flash('Please log in to provide feedback.', 'warning')
        return redirect(url_for('buyer_order_tracking.buyer_order_tracking'))

    shop_id = request.form.get('shop_id')
    product_id = request.form.get('product_id')
    feedback = request.form.get('feedback')
    buyer_id = session.get('user_id')
    buyer_name = session.get('user_name', 'Anonymous')

    if feedback_exists(order_id, buyer_id):
        flash('You have already provided feedback for this order.', 'info')
        return redirect(url_for('buyer_order_tracking.buyer_order_tracking'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        insert_query = """
            INSERT INTO shop_feedbacks (Shop_ID, Product_ID, Sender_ID, Sender_Name, Sender_Message)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (shop_id, product_id, buyer_id, buyer_name, feedback))
        conn.commit()
        flash('Thank you for your feedback!', 'success')
    except Exception as e:
        flash(f"Error submitting feedback: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('buyer_order_tracking.buyer_order_tracking'))


