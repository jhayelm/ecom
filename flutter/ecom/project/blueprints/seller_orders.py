from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from db_connection import get_db_connection

seller_orders_bp = Blueprint('seller_orders', __name__)

@seller_orders_bp.route('/seller_orders')
def seller_orders():
    shop_profile = fetch_shop_profile()

    page = request.args.get('page', 1, type=int)  # Current page
    limit = 10  # Items per page
    offset = (page - 1) * limit

    # Fetch filter, sort, and search parameters
    filter_status = request.args.get('filter', 'Pending')  # Default filter set to 'Pending'
    sort_order = request.args.get('sort', 'recent')  # Sort by order date
    search= request.args.get('search', '')  # Search term for orders

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Base query to fetch orders with related details
        query = """
            SELECT o.Order_ID, 
                   p.Product_ID, 
                   o.Seller_ID, 
                   o.Shop_ID, 
                   o.Buyer_ID, 
                   pi.Product_Name, 
                   s.Shop_Name, 
                   se.Firstname AS seller_firstname,
                   se.Lastname AS seller_lastname,
                   b.Firstname AS buyer_firstname,
                   b.Lastname AS buyer_lastname,
                   o.Quantity, 
                   o.Total_Amount, 
                   o.Payment_Method, 
                   o.Payment_Status,
                   o.Status,
                   o.Date_Ordered
            FROM buyer_orders o
            JOIN products p ON o.Product_ID = p.Product_ID
            JOIN product_info pi ON p.Product_Info_ID = pi.Product_Info_ID
            JOIN seller_accounts sa ON o.Seller_ID = sa.Seller_ID
            JOIN seller_personal_info se ON sa.Personal_ID = se.Personal_ID
            JOIN buyer_accounts ba ON o.Buyer_ID = ba.Buyer_ID
            JOIN buyer_personal_info b ON ba.Personal_ID = b.Personal_ID
            JOIN seller_shop s ON o.Shop_ID = s.Shop_ID
            WHERE o.Seller_ID = %s 
        """
        
        # Prepare parameters for query
        params = [session.get('user_id')]

        # Filter by status (Pending, Active, Archived)
        if filter_status != 'All':  # 'All' filter is not included in the code now
            query += " AND o.Status = %s"
            params.append(filter_status)

        # Search functionality (search by product name or buyer's name)
        if search:
            query += " AND (pi.Product_Name LIKE %s OR CONCAT(b.Firstname, ' ', b.Lastname) LIKE %s OR o.Quantity LIKE %s OR o.Total_Amount LIKE %s OR o.Payment_Status LIKE %s OR o.Payment_Method LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])

        # Sorting logic
        if sort_order == 'recent':
            query += " ORDER BY o.Date_Ordered DESC"
        elif sort_order == 'oldest':
            query += " ORDER BY o.Date_Ordered ASC"
        else:
            query += " ORDER BY o.Date_Ordered DESC"

        # Pagination
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        # Execute the query
        cursor.execute(query, tuple(params))
        orders = cursor.fetchall()

        # Combine first and last names for seller and buyer
        for order in orders:
            order['seller_name'] = f"{order['seller_firstname']} {order['seller_lastname']}"
            order['buyer_name'] = f"{order['buyer_firstname']} {order['buyer_lastname']}"

        # Count total orders for pagination
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM buyer_orders o
            WHERE o.Seller_ID = %s
        """, (session.get('user_id'),))
        total_orders = cursor.fetchone()['total']
        total_pages = (total_orders // limit) + (1 if total_orders % limit else 0)

    except Exception as e:
        flash(f"Error retrieving orders: {e}", 'danger')
        orders = []
        total_pages = 1
    finally:
        cursor.close()
        conn.close()

    # Render the template with orders and pagination data
    return render_template(
        'seller_orders.html',
        orders=orders,
        page=page,
        total_pages=total_pages,
        limit=limit,
        selected_filter=filter_status,
        selected_sort=sort_order,
        search=search,
        shop_profile=shop_profile# Pass the search term to the template for retaining search input
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

@seller_orders_bp.route('/update_order_status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Step 1: Update order status to "Packed"
        update_order_query = """
            UPDATE buyer_orders
            SET Status = 'Packed'
            WHERE Order_ID = %s AND Seller_ID = %s
        """
        cursor.execute(update_order_query, (order_id, session.get('user_id')))

        # Step 2: Fetch Buyer Info and Product Details
        fetch_order_query = """
            SELECT 
                bo.Buyer_ID, 
                bpi.Firstname, 
                bpi.Lastname,
                pi.Product_Name,
                pc.Color_Name,
                bo.Quantity
            FROM buyer_orders bo
            JOIN buyer_accounts ba ON bo.Buyer_ID = ba.Buyer_ID
            JOIN buyer_personal_info bpi ON ba.Personal_ID = bpi.Personal_ID
            JOIN products p ON bo.Product_ID = p.Product_ID
            JOIN product_info pi ON p.Product_Info_ID = pi.Product_Info_ID
            JOIN product_color pc ON p.Product_Info_ID = pc.Product_Info_ID
            WHERE bo.Order_ID = %s
        """
        cursor.execute(fetch_order_query, (order_id,))
        order_info = cursor.fetchone()

        if not order_info:
            flash('Error: Order not found.', 'danger')
            return redirect(url_for('seller_orders.seller_orders', page=1))

        # Extract information from the query result
        buyer_id, first_name, last_name, product_name, color_name, quantity = order_info
        buyer_name = f"{first_name} {last_name}"

        # Step 3: Insert notification for the buyer
        insert_buyer_notification_query = """
            INSERT INTO notifications_buyer 
            (recipient_id, recipient_role, notification_type, title, message, is_read, created_at)
            VALUES (%s, 'Buyer', 'Order Update', %s, %s, 0, NOW())
        """
        buyer_notification_title = "Order Packed"
        buyer_notification_message = f"Your order {product_name} - {quantity} unit/s ({color_name}) has been packed by the seller."
        cursor.execute(insert_buyer_notification_query, 
                       (buyer_id, buyer_notification_title, buyer_notification_message))

        # Step 4: Insert notification for the seller
        seller_id = session.get('user_id')
        insert_seller_notification_query = """
            INSERT INTO notifications_seller 
            (recipient_id, recipient_role, notification_type, title, message, is_read, created_at)
            VALUES (%s, 'Seller', 'Order Update', %s, %s, 0, NOW())
        """
        seller_notification_title = "Order Ready for Shipment"
        seller_notification_message = (
            f"Order {product_name} - {quantity} unit/s ({color_name}) for {buyer_name} is ready for shipment."
        )
        cursor.execute(insert_seller_notification_query, 
                       (seller_id, seller_notification_title, seller_notification_message))

        # Step 5: Notify the admin
        insert_admin_notification_query = """
            INSERT INTO notifications_admin
            (recipient_id, recipient_role, notification_type, title, message, is_read, created_at)
            VALUES (%s, 'Admin', 'Order Update', %s, %s, 0, NOW())
        """
        admin_id = 1  # Replace with the actual Admin ID or make it dynamic
        admin_notification_title = "Order Packed"
        admin_notification_message = (
            f"Order {product_name} - {quantity} unit/s ({color_name}) for {buyer_name} is waiting for you to ship their orders. Check it now!"
        )
        cursor.execute(insert_admin_notification_query, 
                       (admin_id, admin_notification_title, admin_notification_message))

        # Commit the changes
        conn.commit()

        flash('Order status updated to Packed successfully, and notifications sent.', 'success')
    except Exception as e:
        conn.rollback()  # Rollback on error
        flash(f"Error updating order status: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('seller_orders.seller_orders', page=1))





