from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from db_connection import get_db_connection

# Define the Blueprint for the admin section
admin_shipping_bp = Blueprint('admin_shipping', __name__)

@admin_shipping_bp.route('/admin_shipping', methods=['GET', 'POST'])
def admin_shipping():
    # Establish pagination parameters
    page = request.args.get('page', 1, type=int)  # Current page
    limit = 10  # Orders per page
    offset = (page - 1) * limit

    # Get filter, sort, and search parameters
    selected_filter = request.args.get('filter', 'Packed')  # Default filter set to 'Packed'
    selected_sort = request.args.get('sort', 'recent')  # Sort by order date
    search = request.args.get('search', '')  # Search term for orders

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
            WHERE o.Status = %s
        """
        
        # Prepare parameters for the query
        params = [selected_filter]

        # Filter by search term (search by product name, seller/buyer names, etc.)
        if search:
            query += """
                AND (pi.Product_Name LIKE %s OR 
                     CONCAT(b.Firstname, ' ', b.Lastname) LIKE %s OR 
                     CONCAT(se.Firstname, ' ', se.Lastname) LIKE %s OR 
                     o.Quantity LIKE %s OR o.Total_Amount LIKE %s OR 
                     o.Payment_Status LIKE %s OR o.Payment_Method LIKE %s)
            """
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])

        # Sorting logic
        if selected_sort == 'recent':
            query += " ORDER BY o.Date_Ordered DESC"
        elif selected_sort == 'oldest':
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
            WHERE o.Status = %s
        """, (selected_filter,))
        total_orders = cursor.fetchone()['total']
        total_pages = (total_orders // limit) + (1 if total_orders % limit else 0)

        # Fetch all couriers
        couriers = get_couriers()

    except Exception as e:
        flash(f"Error retrieving orders: {e}", 'danger')
        orders = []
        total_pages = 1
        couriers = []
    finally:
        cursor.close()
        conn.close()

    # Render the template with orders, couriers, and pagination data
    return render_template(
        'admin_shipping.html',
        orders=orders,
        page=page,
        total_pages=total_pages,
        limit=limit,
        selected_filter=selected_filter,
        selected_sort=selected_sort,
        search=search,
        couriers=couriers  # Pass couriers to the template
    )

# Function to fetch courier details (Courier_ID, Firstname, Lastname)
def get_couriers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    couriers = []
    try:
        cursor.execute("""
            SELECT Courier_ID, Firstname, Lastname
            FROM couriers
        """)
        couriers = cursor.fetchall()
    except Exception as e:
        flash(f"Error fetching couriers: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return couriers


@admin_shipping_bp.route('/update_shipping_status', methods=['POST'])
def update_shipping_status():
    # Establish database connection
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Step 1: Retrieve Order ID from form data
        order_id = request.form.get('order_id')

        if not order_id:
            flash('No order ID provided!', 'danger')
            return redirect(url_for('admin_shipping.admin_shipping'))

        # Step 2: Fetch Buyer, Seller, Order, and Color Details
        fetch_order_query = """
            SELECT 
                bo.Buyer_ID, 
                bpi.Firstname AS Buyer_Firstname,
                bpi.Lastname AS Buyer_Lastname,
                sa.Seller_ID,
                spi.Firstname AS Seller_Firstname,
                spi.Lastname AS Seller_Lastname,
                pi.Product_Name,
                pc.Color_Name,
                bo.Quantity
            FROM buyer_orders bo
            JOIN buyer_accounts ba ON bo.Buyer_ID = ba.Buyer_ID
            JOIN buyer_personal_info bpi ON ba.Personal_ID = bpi.Personal_ID
            JOIN seller_accounts sa ON bo.Seller_ID = sa.Seller_ID
            JOIN seller_personal_info spi ON sa.Personal_ID = spi.Personal_ID
            JOIN products p ON bo.Product_ID = p.Product_ID
            JOIN product_info pi ON p.Product_Info_ID = pi.Product_Info_ID
            JOIN product_color pc ON pc.Product_Info_ID = pi.Product_Info_ID
            WHERE bo.Order_ID = %s
        """
        cursor.execute(fetch_order_query, (order_id,))
        order_info = cursor.fetchone()

        if not order_info:
            flash('Error: Order not found.', 'danger')
            return redirect(url_for('admin_shipping.admin_shipping'))

        buyer_id = order_info[0]
        buyer_name = f"{order_info[1]} {order_info[2]}"
        seller_id = order_info[3]
        seller_name = f"{order_info[4]} {order_info[5]}"
        product_name = order_info[6]
        color_name = order_info[7]
        quantity = order_info[8]

        # Step 3: Update order status to "Shipped"
        update_order_status_query = "UPDATE buyer_orders SET Status = 'Shipped' WHERE Order_ID = %s"
        cursor.execute(update_order_status_query, (order_id,))

        # Step 4: Insert shipping order record
        insert_shipping_query = "INSERT INTO shipping_orders (Order_ID, Status) VALUES (%s, 'Shipped')"
        cursor.execute(insert_shipping_query, (order_id,))

        # Step 5: Notify the Buyer
        buyer_notification_query = """
            INSERT INTO notifications_buyer
            (recipient_id, recipient_role, notification_type, title, message, is_read, created_at)
            VALUES (%s, 'Buyer', 'Order Update', %s, %s, 0, NOW())
        """
        buyer_notification_title = "Order Shipped"
        buyer_notification_message = (
            f"Your order {product_name} - {quantity} unit/s ({color_name}) has been shipped by the seller."
        )
        cursor.execute(buyer_notification_query, 
                       (buyer_id, buyer_notification_title, buyer_notification_message))

        # Step 6: Notify the Seller
        seller_notification_query = """
            INSERT INTO notifications_seller
            (recipient_id, recipient_role, notification_type, title, message, is_read, created_at)
            VALUES (%s, 'Seller', 'Order Update', %s, %s, 0, NOW())
        """
        seller_notification_title = "Order Shipped"
        seller_notification_message = (
            f"The order {product_name} - {quantity} unit/s ({color_name}) for buyer {buyer_name} has been shipped."
        )
        cursor.execute(seller_notification_query, 
                       (seller_id, seller_notification_title, seller_notification_message))

        # Step 7: Notify the Admin
        admin_notification_query = """
            INSERT INTO notifications_admin
            (recipient_id, recipient_role, notification_type, title, message, is_read, created_at)
            VALUES (%s, 'Admin', 'Order Update', %s, %s, 0, NOW())
        """
        admin_id = 1  # Update as needed
        admin_notification_title = "Order Shipped"
        admin_notification_message = (
            f"The order {product_name} - {quantity} unit/s ({color_name}) for buyer {buyer_name} has been marked as shipped."
        )
        cursor.execute(admin_notification_query, 
                       (admin_id, admin_notification_title, admin_notification_message))

        # Commit changes
        conn.commit()

        flash('Order status updated to "Shipped" successfully, and notifications sent.', 'success')

    except Exception as e:
        conn.rollback()
        flash(f"Error updating shipping status: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_shipping.admin_shipping'))





@admin_shipping_bp.route('/assign_courier', methods=['POST'])
def assign_courier():
    # Get the order ID and selected courier ID from the form
    order_id = request.form.get('order_id')
    courier_id = request.form.get('courier_id')

    if not order_id or not courier_id:
        flash('Order ID or Courier ID not provided!', 'danger')
        return redirect(url_for('admin_shipping.admin_shipping'))

    try:
        # Establish the database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Step 1: Update the order status to "For Delivery"
        update_order_status_query = "UPDATE buyer_orders SET Status = 'For Delivery' WHERE Order_ID = %s"
        cursor.execute(update_order_status_query, (order_id,))

        # Step 2: Insert into the for_delivery table
        insert_for_delivery_query = """
            INSERT INTO for_delivery (Order_ID, Courier_ID, Status)
            VALUES (%s, %s, 'Pending')
        """
        cursor.execute(insert_for_delivery_query, (order_id, courier_id))

        # Step 3: Fetch order, buyer, and seller details
        fetch_order_query = """
            SELECT 
                bo.Buyer_ID,
                bpi.Firstname AS Buyer_Firstname,
                bpi.Lastname AS Buyer_Lastname,
                sa.Seller_ID,
                spi.Firstname AS Seller_Firstname,
                spi.Lastname AS Seller_Lastname,
                pi.Product_Name,
                pc.Color_Name,
                bo.Quantity
            FROM buyer_orders bo
            JOIN buyer_accounts ba ON bo.Buyer_ID = ba.Buyer_ID
            JOIN buyer_personal_info bpi ON ba.Personal_ID = bpi.Personal_ID
            JOIN seller_accounts sa ON bo.Seller_ID = sa.Seller_ID
            JOIN seller_personal_info spi ON sa.Personal_ID = spi.Personal_ID
            JOIN products p ON bo.Product_ID = p.Product_ID
            JOIN product_info pi ON p.Product_Info_ID = pi.Product_Info_ID
            JOIN product_color pc ON pc.Product_Info_ID = pi.Product_Info_ID
            WHERE bo.Order_ID = %s
        """
        cursor.execute(fetch_order_query, (order_id,))
        order_info = cursor.fetchone()

        if not order_info:
            flash('Error: Order not found.', 'danger')
            conn.rollback()
            return redirect(url_for('admin_shipping.admin_shipping'))

        buyer_id = order_info[0]
        buyer_name = f"{order_info[1]} {order_info[2]}"
        seller_id = order_info[3]
        seller_name = f"{order_info[4]} {order_info[5]}"
        product_name = order_info[6]
        color_name = order_info[7]
        quantity = order_info[8]

        # Step 4: Notify the Buyer
        buyer_notification_query = """
            INSERT INTO notifications_buyer
            (recipient_id, recipient_role, notification_type, title, message, is_read, created_at)
            VALUES (%s, 'Buyer', 'Order Update', %s, %s, 0, NOW())
        """
        buyer_notification_title = "Courier Assigned"
        buyer_notification_message = (
            f"Your order {product_name} - {quantity} unit/s ({color_name}) is now assigned to a courier for delivery."
        )
        cursor.execute(buyer_notification_query, 
                       (buyer_id, buyer_notification_title, buyer_notification_message))

        # Step 5: Notify the Seller
        seller_notification_query = """
            INSERT INTO notifications_seller
            (recipient_id, recipient_role, notification_type, title, message, is_read, created_at)
            VALUES (%s, 'Seller', 'Order Update', %s, %s, 0, NOW())
        """
        seller_notification_title = "Courier Assigned"
        seller_notification_message = (
            f"Your order {product_name} - {quantity} unit/s ({color_name}) for buyer {buyer_name} is now assigned to a courier."
        )
        cursor.execute(seller_notification_query, 
                       (seller_id, seller_notification_title, seller_notification_message))

        # Step 6: Notify the Admin
        admin_notification_query = """
            INSERT INTO notifications_admin
            (recipient_id, recipient_role, notification_type, title, message, is_read, created_at)
            VALUES (%s, 'Admin', 'Order Update', %s, %s, 0, NOW())
        """
        admin_id = 1  # Update as needed
        admin_notification_title = "Courier Assigned"
        admin_notification_message = (
            f"The courier has been assigned to deliver order {product_name} - {quantity} unit/s ({color_name}) for buyer {buyer_name}."
        )
        cursor.execute(admin_notification_query, 
                       (admin_id, admin_notification_title, admin_notification_message))

        # Commit the transaction
        conn.commit()

        flash('Courier assigned to order successfully, and notifications sent.', 'success')

    except Exception as e:
        conn.rollback()  # Rollback in case of error
        flash(f"Error assigning courier: {e}", 'danger')

    finally:
        cursor.close()
        conn.close()

    # Redirect back to the admin shipping page
    return redirect(url_for('admin_shipping.admin_shipping'))


@admin_shipping_bp.route('/update_delivered_status', methods=['POST'])
def update_delivered_status():
    # Get the order ID from the form
    order_id = request.form.get('order_id')
    
    if not order_id:
        flash('No order ID provided!', 'danger')
        return redirect(url_for('admin_shipping.admin_shipping'))

    try:
        # Establish the database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Step 1: Update the order status to 'Delivered' in the buyer_orders table
        update_order_query = "UPDATE buyer_orders SET Status = 'Delivered' WHERE Order_ID = %s"
        cursor.execute(update_order_query, (order_id,))

        # Step 2: Update the status in the for_delivery table to 'Delivered'
        update_for_delivery_query = "UPDATE for_delivery SET Status = 'Delivered' WHERE Order_ID = %s"
        cursor.execute(update_for_delivery_query, (order_id,))

        # Step 3: Fetch order, buyer, and seller details
        fetch_order_query = """
            SELECT 
                bo.Buyer_ID,
                bpi.Firstname AS Buyer_Firstname,
                bpi.Lastname AS Buyer_Lastname,
                sa.Seller_ID,
                spi.Firstname AS Seller_Firstname,
                spi.Lastname AS Seller_Lastname,
                pi.Product_Name,
                pc.Color_Name,
                bo.Quantity
            FROM buyer_orders bo
            JOIN buyer_accounts ba ON bo.Buyer_ID = ba.Buyer_ID
            JOIN buyer_personal_info bpi ON ba.Personal_ID = bpi.Personal_ID
            JOIN seller_accounts sa ON bo.Seller_ID = sa.Seller_ID
            JOIN seller_personal_info spi ON sa.Personal_ID = spi.Personal_ID
            JOIN products p ON bo.Product_ID = p.Product_ID
            JOIN product_info pi ON p.Product_Info_ID = pi.Product_Info_ID
            JOIN product_color pc ON pc.Product_Info_ID = pi.Product_Info_ID
            WHERE bo.Order_ID = %s
        """
        cursor.execute(fetch_order_query, (order_id,))
        order_info = cursor.fetchone()

        if not order_info:
            flash('Error: Order not found.', 'danger')
            conn.rollback()
            return redirect(url_for('admin_shipping.admin_shipping'))

        buyer_id = order_info[0]
        buyer_name = f"{order_info[1]} {order_info[2]}"
        seller_id = order_info[3]
        seller_name = f"{order_info[4]} {order_info[5]}"
        product_name = order_info[6]
        color_name = order_info[7]
        quantity = order_info[8]

        # Step 4: Notify the Buyer
        buyer_notification_query = """
            INSERT INTO notifications_buyer
            (recipient_id, recipient_role, notification_type, title, message, is_read, created_at)
            VALUES (%s, 'Buyer', 'Order Update', %s, %s, 0, NOW())
        """
        buyer_notification_title = "Order Delivered"
        buyer_notification_message = (
            f"Your order {product_name} - {quantity} unit/s ({color_name}) has been delivered successfully."
        )
        cursor.execute(buyer_notification_query, 
                       (buyer_id, buyer_notification_title, buyer_notification_message))

        # Step 5: Notify the Seller
        seller_notification_query = """
            INSERT INTO notifications_seller
            (recipient_id, recipient_role, notification_type, title, message, is_read, created_at)
            VALUES (%s, 'Seller', 'Order Update', %s, %s, 0, NOW())
        """
        seller_notification_title = "Order Delivered"
        seller_notification_message = (
            f"Your order {product_name} - {quantity} unit/s ({color_name}) for buyer {buyer_name} has been delivered successfully."
        )
        cursor.execute(seller_notification_query, 
                       (seller_id, seller_notification_title, seller_notification_message))

        # Step 6: Notify the Admin
        admin_notification_query = """
            INSERT INTO notifications_admin
            (recipient_id, recipient_role, notification_type, title, message, is_read, created_at)
            VALUES (%s, 'Admin', 'Order Update', %s, %s, 0, NOW())
        """
        admin_id = 1  # Update as needed
        admin_notification_title = "Order Delivered"
        admin_notification_message = (
            f"The order {product_name} - {quantity} unit/s ({color_name}) for buyer {buyer_name} has been delivered successfully."
        )
        cursor.execute(admin_notification_query, 
                       (admin_id, admin_notification_title, admin_notification_message))

        # Commit the changes to the database
        conn.commit()

        flash('Order status updated to "Delivered", and notifications sent.', 'success')

    except Exception as e:
        conn.rollback()  # Rollback in case of error
        flash(f"Error updating order status: {e}", 'danger')

    finally:
        cursor.close()
        conn.close()

    # Redirect back to the admin shipping page
    return redirect(url_for('admin_shipping.admin_shipping'))
