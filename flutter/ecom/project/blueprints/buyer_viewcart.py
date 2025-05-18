from flask import Blueprint, render_template, redirect, url_for, session, jsonify, request
from db_connection import get_db_connection
import base64
import os

# Define the Blueprint for the buyer section
buyer_viewcart_bp = Blueprint('buyer_viewcart', __name__)

# Route for viewing cart items
@buyer_viewcart_bp.route('/view_cart', methods=['GET'])
def view_cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect if not logged in

    buyer_id = session['user_id']
    sort_by = request.args.get('sort', 'date')  # Default sort by 'date'
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)

            # Sorting query based on the selected sort option
            if sort_by == 'price':
                order_by = "pi.Product_Price"
            elif sort_by == 'name':
                order_by = "pi.Product_Name"
            else:
                order_by = "ci.Added_At"  # Default to sorting by date

            cart_query = f"""
                SELECT 
                    ci.cart_item_id,
                    ci.Quantity,
                    ci.Added_At,
                    pi.Product_Name,
                    CAST(pi.Product_Price AS DECIMAL(10, 2)) AS Product_Price,
                    pi.Product_Main_Picture,
                    p.Product_Category,
                    p.Seller_ID,
                    ps.Stock_Quantity,
                    ci.Product_ID,
                    ss.Shop_ID
                FROM cart_items AS ci
                JOIN products AS p ON ci.Product_ID = p.Product_ID
                JOIN product_info AS pi ON ci.Product_Info_ID = pi.Product_Info_ID
                JOIN seller_shop AS ss ON p.Seller_ID = ss.Seller_ID
                LEFT JOIN product_stock AS ps ON ci.Product_Color_ID = ps.Product_Color_ID
                WHERE ci.Buyer_ID = %s
                ORDER BY {order_by}
            """
            cursor.execute(cart_query, (buyer_id,))
            cart_items = cursor.fetchall()

            # Convert images to base64
            for item in cart_items:
                if item['Product_Main_Picture']:
                    item['Product_Main_Picture'] = base64.b64encode(item['Product_Main_Picture']).decode('utf-8')

            return jsonify(cart_items)
        except Exception as e:
            print(f"Error fetching cart details: {e}")
            return jsonify({'error': 'Internal Server Error'}), 500
        finally:
            cursor.close()
            conn.close()

    return jsonify({'error': 'Database connection failed'}), 500


@buyer_viewcart_bp.route('/remove_cart_item/<int:cart_item_id>', methods=['DELETE'])
def remove_cart_item(cart_item_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401

    buyer_id = session['user_id']
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Check if the item belongs to the logged-in buyer
            check_query = "SELECT cart_item_id FROM cart_items WHERE cart_item_id = %s AND Buyer_ID = %s"
            cursor.execute(check_query, (cart_item_id, buyer_id))
            item = cursor.fetchone()

            if not item:
                return jsonify({'success': False, 'message': 'Item not found or not authorized'}), 404

            # Delete the item
            delete_query = "DELETE FROM cart_items WHERE cart_item_id = %s"
            cursor.execute(delete_query, (cart_item_id,))
            conn.commit()

            return jsonify({'success': True, 'message': 'Item removed successfully'})
        except Exception as e:
            print(f"Error removing cart item: {e}")
            return jsonify({'success': False, 'message': 'Internal Server Error'}), 500
        finally:
            cursor.close()
            conn.close()

    return jsonify({'success': False, 'message': 'Database connection failed'}), 500

@buyer_viewcart_bp.route('/update_quantity/<int:cart_item_id>', methods=['PUT'])
def update_quantity(cart_item_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401

    buyer_id = session['user_id']
    quantity = request.json.get('quantity')

    if not quantity or quantity <= 0:
        return jsonify({'success': False, 'message': 'Invalid quantity'}), 400

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # Check if the item exists in the cart for the logged-in user
            check_query = """
                SELECT ci.cart_item_id, ps.Stock_Quantity
                FROM cart_items AS ci
                JOIN product_stock AS ps ON ci.Product_Color_ID = ps.Product_Color_ID
                WHERE ci.cart_item_id = %s AND ci.Buyer_ID = %s
            """
            cursor.execute(check_query, (cart_item_id, buyer_id))
            item = cursor.fetchone()

            if not item:
                return jsonify({'success': False, 'message': 'Item not found or not authorized'}), 404

            available_stock = item['Stock_Quantity']

            # Check if the requested quantity exceeds available stock
            if quantity > available_stock:
                return jsonify({
                    'success': False,
                    'message': f'Requested quantity exceeds available stock. Only {available_stock} available.'
                }), 400

            # Update the quantity in the cart
            update_query = "UPDATE cart_items SET Quantity = %s WHERE cart_item_id = %s"
            cursor.execute(update_query, (quantity, cart_item_id))
            conn.commit()

            return jsonify({'success': True, 'message': 'Quantity updated successfully'}), 200

        except Exception as e:
            conn.rollback()
            print(f"Error updating quantity: {e}")
            return jsonify({'success': False, 'message': 'Internal Server Error'}), 500

        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({'success': False, 'message': 'Failed to connect to the database'}), 500

@buyer_viewcart_bp.route('/checkout_details', methods=['GET'])
def checkout_details():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect if not logged in

    buyer_id = session['user_id']
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)

            # Fetch the Address_ID and Address Details
            address_query = """
                SELECT bai.House_No, bai.Barangay, bai.City, bai.Province, bai.Postal_Code, bai.Country
                FROM buyer_accounts AS ba
                JOIN buyer_address_info AS bai ON ba.Address_ID = bai.Address_ID
                WHERE ba.Buyer_ID = %s
            """
            cursor.execute(address_query, (buyer_id,))
            address = cursor.fetchone()

            # Fetch cart items with Product_ID, Seller_ID, Shop_ID, and Buyer_ID
            cart_query = """
                SELECT 
                    ci.cart_item_id,
                    ci.Quantity,
                    pi.Product_Name,
                    CAST(pi.Product_Price AS DECIMAL(10, 2)) AS Product_Price,
                    pi.Product_Main_Picture,
                    ci.Product_ID,
                    p.Seller_ID,
                    ss.Shop_ID
                FROM cart_items AS ci
                JOIN products AS p ON ci.Product_ID = p.Product_ID
                JOIN product_info AS pi ON ci.Product_Info_ID = pi.Product_Info_ID
                JOIN seller_shop AS ss ON p.Seller_ID = ss.Seller_ID
                WHERE ci.Buyer_ID = %s
            """
            cursor.execute(cart_query, (buyer_id,))
            cart_items = cursor.fetchall()

            # Convert images to base64
            for item in cart_items:
                if item['Product_Main_Picture']:
                    item['Product_Main_Picture'] = base64.b64encode(item['Product_Main_Picture']).decode('utf-8')

            return jsonify({
                'address': address,
                'cart_items': cart_items,
                'buyer_id': buyer_id
            })
        except Exception as e:
            print(f"Error fetching checkout details: {e}")
            return jsonify({'error': 'Internal Server Error'}), 500
        finally:
            cursor.close()
            conn.close()

    return jsonify({'error': 'Database connection failed'}), 500

@buyer_viewcart_bp.route('/confirm_order', methods=['POST'])
def confirm_order():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401

    buyer_id = session['user_id']
    orders = request.json.get('cart_items', [])

    if not orders:
        print("No orders received from frontend.")
        return jsonify({'success': False, 'message': 'No items to process'}), 400

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            print("Received orders:", orders)  # Debugging line

            cart_item_ids = []  # To track cart items to be deleted
            for order in orders:
                # Insert into buyer_orders table
                insert_query = """
                    INSERT INTO buyer_orders (
                        Product_ID, Seller_ID, Shop_ID, Buyer_ID, Quantity, 
                        Total_Amount, Payment_Method, Payment_Status, Status, Date_Ordered
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """
                cursor.execute(insert_query, (
                    order['Product_ID'],
                    order['Seller_ID'],
                    order['Shop_ID'],
                    buyer_id,
                    order['Quantity'],
                    order['Total_Amount'],
                    'Cash on Delivery',  # Default Payment Method
                    'Unpaid',  # Default Payment Status
                    'Pending'  # Default Status
                ))

                # Collect cart_item_id for deletion
                cart_item_ids.append(order['cart_item_id'])

                # Fetch product and seller details for notifications
                fetch_details_query = """
                    SELECT 
                        spi.Firstname AS Seller_Firstname,
                        spi.Lastname AS Seller_Lastname,
                        pi.Product_Name,
                        pc.Color_Name
                    FROM products p
                    JOIN product_info pi ON p.Product_Info_ID = pi.Product_Info_ID
                    JOIN product_color pc ON pc.Product_Info_ID = pi.Product_Info_ID
                    JOIN seller_accounts sa ON p.Seller_ID = sa.Seller_ID
                    JOIN seller_personal_info spi ON sa.Personal_ID = spi.Personal_ID
                    WHERE p.Product_ID = %s
                """
                cursor.execute(fetch_details_query, (order['Product_ID'],))
                product_details = cursor.fetchone()

                if product_details:
                    seller_name = f"{product_details[0]} {product_details[1]}"
                    product_name = product_details[2]
                    color_name = product_details[3]

                    # Notify Seller
                    seller_notification_query = """
                        INSERT INTO notifications_seller
                        (recipient_id, recipient_role, notification_type, title, message, is_read, created_at)
                        VALUES (%s, 'Seller', 'Order Update', %s, %s, 0, NOW())
                    """
                    seller_notification_title = "New Order Confirmed"
                    seller_notification_message = (
                        f"A new order for {product_name} ({color_name}) has been placed. Quantity: {order['Quantity']}."
                    )
                    cursor.execute(seller_notification_query, 
                                   (order['Seller_ID'], seller_notification_title, seller_notification_message))

                    # Notify Admin
                    admin_notification_query = """
                        INSERT INTO notifications_admin
                        (recipient_id, recipient_role, notification_type, title, message, is_read, created_at)
                        VALUES (%s, 'Admin', 'Order Update', %s, %s, 0, NOW())
                    """
                    admin_id = 1  # Update as needed
                    admin_notification_title = "New Order Placed"
                    admin_notification_message = (
                        f"A new order for {product_name} ({color_name}) has been placed by Buyer ID: {buyer_id}. Quantity: {order['Quantity']}."
                    )
                    cursor.execute(admin_notification_query, 
                                   (admin_id, admin_notification_title, admin_notification_message))

            # Delete items from cart_items table
            if cart_item_ids:
                delete_query = "DELETE FROM cart_items WHERE cart_item_id IN (%s)" % ','.join(['%s'] * len(cart_item_ids))
                cursor.execute(delete_query, cart_item_ids)

            conn.commit()
            return jsonify({'success': True, 'message': 'Order confirmed, cart items removed, and notifications sent!'}), 200

        except Exception as e:
            conn.rollback()
            print(f"Error confirming order: {e}")
            return jsonify({'success': False, 'message': 'Internal Server Error'}), 500
        finally:
            cursor.close()
            conn.close()

    return jsonify({'success': False, 'message': 'Database connection failed'}), 500

