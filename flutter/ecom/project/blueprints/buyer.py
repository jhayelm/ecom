
from flask import Blueprint, render_template, session, request, jsonify, redirect, flash, url_for, g
from db_connection import get_db_connection
from mysql.connector import Error
import base64
from datetime import datetime
import mysql.connector
buyer_bp = Blueprint('buyer', __name__)

# Existing buyer homepage route
@buyer_bp.route('/')
def buyer_homepage():
    if 'user_id' not in session:
        return redirect(url_for('login.login'))  

    user_id = session['user_id'] 

    conn = get_db_connection()
    profile_pic = None  
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)

            # Query to fetch profile picture
            cursor.execute("""
                SELECT Profile_Pic
                FROM buyer_accounts
                WHERE Buyer_ID = %s
            """, (user_id,))

            result = cursor.fetchone()
            
            if result and result['Profile_Pic']:
                profile_pic = base64.b64encode(result['Profile_Pic']).decode('utf-8')  # Encode to base64 if exists

        except Error as e:
            print(f"Error fetching profile picture: {e}")
            flash("An error occurred while fetching your profile picture.", "danger")
            return redirect(url_for('buyer_profile.show_buyer_profile'))  # Handle errors

        finally:
            cursor.close()
            conn.close()

    # Pass the profile_pic to the template
    return render_template('buyer_homepage.html', profile_pic=profile_pic)


@buyer_bp.before_app_request
def buyer_fetch_unread_notifications_count():
    if 'user_id' in session:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Query to count unread notifications for the logged-in buyer
            query = """
                SELECT COUNT(*) AS unread_count
                FROM notifications_buyer
                WHERE recipient_id = %s AND is_read = FALSE
            """
            cursor.execute(query, (session['user_id'],))
            g.buyer_unread_notifications_count = cursor.fetchone()['unread_count']
        except Exception as e:
            g.buyer_unread_notifications_count = 0  # Default to 0 if an error occurs
        finally:
            cursor.close()
            conn.close()
    else:
        g.buyer_unread_notifications_count = 0  # Default to 0 for non-logged-in users

# Function to get buyer's name
def get_buyer_name(buyer_id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT p.Firstname, p.Lastname, p.Suffix
                FROM buyer_accounts AS b
                JOIN buyer_personal_info AS p ON b.Personal_ID = p.Personal_ID
                WHERE b.Buyer_ID = %s
            """
            cursor.execute(query, (buyer_id,))
            result = cursor.fetchone()
            
            if result:
                full_name = f"{result['Firstname']} {result['Lastname']} {result.get('Suffix', '')}".strip()
                return full_name
            else:
                return None
        except Error as e:
            print(f"Error fetching buyer name: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    return None


from flask import jsonify
import base64
from mysql.connector import connect, Error

# Assuming get_db_connection() is defined elsewhere to handle DB connection
@buyer_bp.route('/product/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT 
                    pi.Product_Name, 
                    pi.Product_Price, 
                    pi.Product_Description, 
                    pi.Product_Main_Picture,
                    p.Product_Category,
                    p.Seller_ID,
                    p.Product_ID,
                    p.Product_Info_ID,  
                    pc.Color_Name,
                    pc.Product_Color_ID, 
                    ps.Stock_Quantity,
                    ps.Product_Stock_ID, 
                    img.Product_Image_ID, 
                    img.Product_Image,
                    specs.Product_Specs_ID,
                    specs.Product_Specs_Type,
                    specs.Product_Specs_Content
                FROM products AS p
                JOIN product_info AS pi ON p.Product_Info_ID = pi.Product_Info_ID
                LEFT JOIN product_color AS pc ON pc.Product_Info_ID = pi.Product_Info_ID
                LEFT JOIN product_stock AS ps ON ps.Product_Color_ID = pc.Product_Color_ID
                LEFT JOIN product_image AS img ON img.Product_Info_ID = pi.Product_Info_ID
                LEFT JOIN product_specs AS specs ON specs.Product_Info_ID = pi.Product_Info_ID
                WHERE p.Product_ID = %s
            """
            cursor.execute(query, (product_id,))
            product = cursor.fetchall()

            if product:
                # Extract base product details
                base_product = product[0]  # Assuming all specs share the same base product info
                
                # Collect product specifications, ensuring no duplicates
                product_specs = []
                seen_specs = set()  # To track already processed specs

                for spec in product:
                    spec_id = spec["Product_Specs_ID"]
                    if spec_id and spec_id not in seen_specs:
                        product_specs.append({
                            "Product_Specs_ID": spec_id,
                            "Product_Specs_Type": spec["Product_Specs_Type"],
                            "Product_Specs_Content": spec["Product_Specs_Content"]
                        })
                        seen_specs.add(spec_id)

                # Convert image data to base64 if available
                product_main_image_base64 = None
                if base_product["Product_Main_Picture"]:
                    product_main_image_base64 = base64.b64encode(base_product["Product_Main_Picture"]).decode('utf-8')

                product_image_base64 = None
                if base_product["Product_Image"]:
                    product_image_base64 = base64.b64encode(base_product["Product_Image"]).decode('utf-8')

                # Return the JSON response
                return jsonify({
                    "Product_Name": base_product["Product_Name"],
                    "Product_Price": base_product["Product_Price"],
                    "Product_Description": base_product["Product_Description"],
                    "Product_Main_Picture": product_main_image_base64,
                    "Product_Category": base_product["Product_Category"],
                    "Product_Color": base_product["Color_Name"] or "N/A",
                    "Product_Stock": base_product["Stock_Quantity"] or 0,
                    "Seller_ID": base_product["Seller_ID"],
                    "Product_ID": base_product["Product_ID"],
                    "Product_Info_ID": base_product["Product_Info_ID"],
                    "Product_Color_ID": base_product["Product_Color_ID"],
                    "Product_Stock_ID": base_product["Product_Stock_ID"],
                    "Product_Image_ID": base_product["Product_Image_ID"],
                    "Product_Image": product_image_base64,
                    "Product_Specifications": product_specs
                })
            else:
                return jsonify({'error': 'Product not found'}), 404
        except Error as e:
            print(f"Error fetching product details: {e}")
            return jsonify({'error': 'Internal Server Error'}), 500
        finally:
            cursor.close()
            conn.close()

    return jsonify({'error': 'Database connection failed'}), 500

def get_category_products(category, min_price=None, max_price=None, page=1, limit=20, sort='recent'):
    conn = get_db_connection()
    products = []
    total_pages = 1  # Initialize total_pages to avoid UnboundLocalError

    if conn:
        try:
            cursor = conn.cursor(dictionary=True)

            # Calculate offset for pagination
            offset = (page - 1) * limit

            # Base query
            query = """
                SELECT p.Product_ID, p.time_added, pi.Product_Name, pi.Product_Price, pi.Product_Main_Picture,
                       p.Seller_ID, ss.Shop_ID, COALESCE(AVG(r.Rating), 0) AS Average_Rating
                FROM products AS p
                JOIN product_info AS pi ON p.Product_Info_ID = pi.Product_Info_ID
                LEFT JOIN shop_rating AS r ON p.Product_ID = r.Product_ID
                JOIN seller_shop AS ss ON p.Seller_ID = ss.Seller_ID
                WHERE p.Product_Category = %s AND p.Status = 'Active'
            """

            # Add price filters to query if provided
            if min_price is not None and min_price > 0 and max_price is not None and max_price > 0:
                # Both min_price and max_price are greater than 0, apply the price range filter
                query += " AND pi.Product_Price >= %s AND pi.Product_Price <= %s"
            elif min_price is not None and min_price > 0:  # Filter only based on min_price
                query += " AND pi.Product_Price >= %s"
            elif max_price is not None and max_price > 0:  # Filter only based on max_price
                query += " AND pi.Product_Price <= %s"

            query += " GROUP BY p.Product_ID, p.time_added, pi.Product_Name, pi.Product_Price, pi.Product_Main_Picture, p.Seller_ID, ss.Shop_ID"

            # Add sorting condition based on the sort parameter (recent or oldest)
            if sort == 'recent':
                query += " ORDER BY p.time_added DESC"  # Sort by most recent first
            elif sort == 'oldest':
                query += " ORDER BY p.time_added ASC"  # Sort by oldest first
            else:
                # Default to recent if the sort value is invalid
                query += " ORDER BY p.time_added DESC"

            query += " LIMIT %s OFFSET %s"

            # Debugging: Print the final query
            print(f"Executing query: {query}")

            # Execute the query with the appropriate filters
            params = [category]
            if min_price is not None and min_price > 0:
                params.append(min_price)
            if max_price is not None and max_price > 0:
                params.append(max_price)
            params.extend([limit, offset])
            
            cursor.execute(query, tuple(params))
            products = cursor.fetchall()

            # Get the total number of products for pagination
            cursor.execute("""
                SELECT COUNT(*)
                FROM products AS p
                JOIN product_info AS pi ON p.Product_Info_ID = pi.Product_Info_ID
                WHERE p.Product_Category = %s AND p.Status = 'Active'
                AND (pi.Product_Price >= %s OR %s = 0)
                AND (pi.Product_Price <= %s OR %s = 0)
            """, (category, min_price, min_price, max_price, max_price))

            total_count = cursor.fetchone()[0]
            total_pages = (total_count + limit - 1) // limit  # Calculate total pages for pagination

        except Exception as e:
            print(f"Error retrieving category products: {e}")
        finally:
            cursor.close()

    return products, total_pages


@buyer_bp.route('/like_product/<int:product_id>/<int:shop_id>/<int:seller_id>', methods=['POST'])
def like_product(product_id, shop_id, seller_id):
    buyer_id = session.get('user_id')
    
    if not buyer_id:
        flash('You need to be logged in to like products.', 'warning')  # Flash the error message
        return redirect(url_for('buyer.buyer_cat_mobilephone'))  # Redirect to the main category or home page

    # Check if the product is already liked
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Check if the buyer has already liked this product
            cursor.execute("""
                SELECT * FROM buyer_likes 
                WHERE Product_ID = %s AND Shop_ID = %s AND Seller_ID = %s AND Buyer_ID = %s
            """, (product_id, shop_id, seller_id, buyer_id))

            result = cursor.fetchone()

            if result:
                flash('You already liked this product.', 'info')  # Flash a message if already liked
            else:
                # Insert the new like into the buyer_likes table
                cursor.execute("""
                    INSERT INTO buyer_likes (Product_ID, Shop_ID, Seller_ID, Buyer_ID, Status) 
                    VALUES (%s, %s, %s, %s, 'Liked')
                """, (product_id, shop_id, seller_id, buyer_id))
                conn.commit()
                flash('Product liked successfully!', 'success')  # Flash the success message

        except Error as e:
            print(f"Error liking the product: {e}")
            flash('An error occurred while liking the product.', 'danger')  # Flash the error message
        finally:
            cursor.close()
            conn.close()
            
    return redirect(url_for('buyer.buyer_cat_mobilephone'))  # Redirect to the main category or home page


# Function to unlike a product
def unlike_product_from_db(buyer_id, product_id, shop_id, seller_id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Delete the like entry from the buyer_likes table
            cursor.execute("""
                DELETE FROM buyer_likes 
                WHERE Product_ID = %s AND Shop_ID = %s AND Seller_ID = %s AND Buyer_ID = %s
            """, (product_id, shop_id, seller_id, buyer_id))
            conn.commit()
        except Error as e:
            print(f"Error unliking the product: {e}")
        finally:
            cursor.close()
            conn.close()

# Route for unliking a product
@buyer_bp.route('/unlike_product/<int:product_id>/<int:shop_id>/<int:seller_id>', methods=['POST'])
def unlike_product(product_id, shop_id, seller_id):
    buyer_id = session.get('user_id')
    
    if not buyer_id:
        flash('You need to be logged in to unlike products.', 'warning')  # Flash a warning if not logged in
        return redirect(url_for('buyer.buyer_homepage'))  # Redirect to homepage or previous page
    
    # Unlike the product (delete the like from the database)
    unlike_product_from_db(buyer_id, product_id, shop_id, seller_id)
    
    flash('Product unliked successfully!', 'success')  # Flash a success message
    return redirect(url_for('buyer.buyer_cat_mobilephone'))  # Redirect to the category page (or any page you want)


def has_liked_product(buyer_id, product_id, shop_id, seller_id):
    conn = get_db_connection()
    liked = False
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM buyer_likes 
                WHERE Product_ID = %s AND Shop_ID = %s AND Seller_ID = %s AND Buyer_ID = %s
            """, (product_id, shop_id, seller_id, buyer_id))
            result = cursor.fetchone()
            if result:
                liked = True
        except Error as e:
            print(f"Error checking if product is liked: {e}")
        finally:
            cursor.close()
            conn.close()
    return liked

@buyer_bp.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    try:
        data = request.get_json()  # Get the JSON data sent from the frontend
        
        # Validate that the required data is present
        required_fields = ['product_id', 'product_info_id', 'product_color_id', 
                           'product_image_id', 'product_specs_id', 'seller_id', 
                           'buyer_id', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({"status": "error", "message": f"Missing field: {field}"}), 400
        
        # Connect to the database using the get_db_connection function
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the product already exists in the cart
        check_query = """
        SELECT Quantity FROM cart_items 
        WHERE Product_ID = %s AND Product_Color_ID = %s AND Buyer_ID = %s
        """
        cursor.execute(check_query, (data['product_id'], data['product_color_id'], data['buyer_id']))
        existing_item = cursor.fetchone()

        if existing_item:
            # If the product already exists, update the quantity
            new_quantity = existing_item[0] + data['quantity']
            update_query = """
            UPDATE cart_items 
            SET Quantity = %s, Added_At = NOW() 
            WHERE Product_ID = %s AND Product_Color_ID = %s AND Buyer_ID = %s
            """
            cursor.execute(update_query, (new_quantity, data['product_id'], data['product_color_id'], data['buyer_id']))
            conn.commit()  # Commit the changes to the database
            cursor.close()
            conn.close()  # Close the connection
            
            # Return a response indicating the product exists and was updated
            return jsonify({
                "status": "success", 
                "message": "Your cart has been updated with new quantity!",
                "is_existing": True  # Indicate the product was already in the cart
            })

        else:
            # If the product doesn't exist, insert it into the cart
            insert_query = """
            INSERT INTO cart_items (Product_ID, Product_Info_ID, Product_Color_ID, Product_Image_ID, 
                                    Product_Specs_ID, Seller_ID, Buyer_ID, Quantity, Added_At)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            values = (
                data['product_id'],
                data['product_info_id'],
                data['product_color_id'],
                data['product_image_id'],
                data['product_specs_id'],
                data['seller_id'],
                data['buyer_id'],
                data['quantity']
            )
            cursor.execute(insert_query, values)
            conn.commit()  # Commit the changes to the database
            cursor.close()
            conn.close()  # Close the connection

            # Return a response indicating the product was added successfully
            return jsonify({
                "status": "success", 
                "message": "Product added in cart successfully!",
                "is_existing": False  # Indicate the product was not in the cart
            })

    except Exception as e:
        # Log the exception for debugging (in production, use proper logging)
        print(f"Error occurred: {e}")
        return jsonify({
            "status": "error", 
            "message": "An error occurred while adding/updating the product in the cart."
        }), 500


@buyer_bp.route('/buyer_cat_mobilephone')
def buyer_cat_mobilephone():
    # Get query parameters for min and max price
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    
    # Get the page number from query parameters
    page = int(request.args.get('page', 1))

    # Get the sort parameter (default to 'recent' if not provided)
    sort = request.args.get('sort', 'recent')

    # Fetch products with price filters and sort applied
    products, total_pages = get_category_products('Mobile Phones', min_price=min_price, max_price=max_price, page=page, sort=sort)
    
    buyer_id = session.get('user_id')  # Get buyer_id from session
    like_status = {}
    
    if buyer_id:
        # Check like status for each product and store in a dictionary
        for product in products:
            liked = has_liked_product(buyer_id, product['Product_ID'], product['Shop_ID'], product['Seller_ID'])
            like_status[product['Product_ID']] = liked

    return render_template(
        'buyer_cat_mobilephone.html', 
        products=products, 
        total_pages=total_pages, 
        current_page=page, 
        like_status=like_status,  # Pass like status to the template
        min_price=min_price,  # Pass the min price filter to the template
        max_price=max_price,  # Pass the max price filter to the template
        sort=sort  # Pass the sort parameter to the template
    )

@buyer_bp.route('/buyer_cat_laptop')
def buyer_cat_laptop():
    # Get query parameters for min and max price
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    
    # Get the page number from query parameters
    page = int(request.args.get('page', 1))

    # Get the sort parameter (default to 'recent' if not provided)
    sort = request.args.get('sort', 'recent')

    # Fetch products with price filters and sort applied
    products, total_pages = get_category_products('Laptop', min_price=min_price, max_price=max_price, page=page, sort=sort)
    
    buyer_id = session.get('user_id')  # Get buyer_id from session
    like_status = {}
    
    if buyer_id:
        # Check like status for each product and store in a dictionary
        for product in products:
            liked = has_liked_product(buyer_id, product['Product_ID'], product['Shop_ID'], product['Seller_ID'])
            like_status[product['Product_ID']] = liked

    return render_template(
        'buyer_cat_laptop.html', 
        products=products, 
        total_pages=total_pages, 
        current_page=page, 
        like_status=like_status,  # Pass like status to the template
        min_price=min_price,  # Pass the min price filter to the template
        max_price=max_price,  # Pass the max price filter to the template
        sort=sort  # Pass the sort parameter to the template
    )
    
    

@buyer_bp.route('/buyer_cat_desktop')
def buyer_cat_desktop():
    # Get query parameters for min and max price
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    
    # Get the page number from query parameters
    page = int(request.args.get('page', 1))

    # Get the sort parameter (default to 'recent' if not provided)
    sort = request.args.get('sort', 'recent')

    # Fetch products with price filters and sort applied
    products, total_pages = get_category_products('Desktop', min_price=min_price, max_price=max_price, page=page, sort=sort)
    
    buyer_id = session.get('user_id')  # Get buyer_id from session
    like_status = {}
    
    if buyer_id:
        # Check like status for each product and store in a dictionary
        for product in products:
            liked = has_liked_product(buyer_id, product['Product_ID'], product['Shop_ID'], product['Seller_ID'])
            like_status[product['Product_ID']] = liked

    return render_template(
        'buyer_cat_desktop.html', 
        products=products, 
        total_pages=total_pages, 
        current_page=page, 
        like_status=like_status,  # Pass like status to the template
        min_price=min_price,  # Pass the min price filter to the template
        max_price=max_price,  # Pass the max price filter to the template
        sort=sort  # Pass the sort parameter to the template
    )
    
    
@buyer_bp.route('/buyer_cat_audio_equipment')
def buyer_cat_audio_equipment():
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    page = int(request.args.get('page', 1))
    sort = request.args.get('sort', 'recent')
    
    products, total_pages = get_category_products('Audio Equipment', min_price=min_price, max_price=max_price, page=page, sort=sort)
    
    buyer_id = session.get('user_id')
    like_status = {}
    
    if buyer_id:
        for product in products:
            liked = has_liked_product(buyer_id, product['Product_ID'], product['Shop_ID'], product['Seller_ID'])
            like_status[product['Product_ID']] = liked

    return render_template(
        'buyer_cat_audio_equipment.html',
        products=products,
        total_pages=total_pages,
        current_page=page,
        like_status=like_status,
        min_price=min_price,
        max_price=max_price,
        sort=sort
    )

@buyer_bp.route('/buyer_cat_video_equipment')
def buyer_cat_video_equipment():
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    page = int(request.args.get('page', 1))
    sort = request.args.get('sort', 'recent')
    
    products, total_pages = get_category_products('Video Equipment', min_price=min_price, max_price=max_price, page=page, sort=sort)
    
    buyer_id = session.get('user_id')
    like_status = {}
    
    if buyer_id:
        for product in products:
            liked = has_liked_product(buyer_id, product['Product_ID'], product['Shop_ID'], product['Seller_ID'])
            like_status[product['Product_ID']] = liked

    return render_template(
        'buyer_cat_video_equipment.html',
        products=products,
        total_pages=total_pages,
        current_page=page,
        like_status=like_status,
        min_price=min_price,
        max_price=max_price,
        sort=sort
    )

@buyer_bp.route('/buyer_cat_smart_devices')
def buyer_cat_smart_devices():
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    page = int(request.args.get('page', 1))
    sort = request.args.get('sort', 'recent')
    
    products, total_pages = get_category_products('Smart Home Devices', min_price=min_price, max_price=max_price, page=page, sort=sort)
    
    buyer_id = session.get('user_id')
    like_status = {}
    
    if buyer_id:
        for product in products:
            liked = has_liked_product(buyer_id, product['Product_ID'], product['Shop_ID'], product['Seller_ID'])
            like_status[product['Product_ID']] = liked

    return render_template(
        'buyer_cat_smart_devices.html',
        products=products,
        total_pages=total_pages,
        current_page=page,
        like_status=like_status,
        min_price=min_price,
        max_price=max_price,
        sort=sort
    )

@buyer_bp.route('/buyer_cat_photography')
def buyer_cat_photography():
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    page = int(request.args.get('page', 1))
    sort = request.args.get('sort', 'recent')
    
    products, total_pages = get_category_products('Photography', min_price=min_price, max_price=max_price, page=page, sort=sort)
    
    buyer_id = session.get('user_id')
    like_status = {}
    
    if buyer_id:
        for product in products:
            liked = has_liked_product(buyer_id, product['Product_ID'], product['Shop_ID'], product['Seller_ID'])
            like_status[product['Product_ID']] = liked

    return render_template(
        'buyer_cat_photography.html',
        products=products,
        total_pages=total_pages,
        current_page=page,
        like_status=like_status,
        min_price=min_price,
        max_price=max_price,
        sort=sort
    )

@buyer_bp.route('/buyer_cat_wearable_tech')
def buyer_cat_wearable_tech():
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    page = int(request.args.get('page', 1))
    sort = request.args.get('sort', 'recent')
    
    products, total_pages = get_category_products('Wearable Technology', min_price=min_price, max_price=max_price, page=page, sort=sort)
    
    buyer_id = session.get('user_id')
    like_status = {}
    
    if buyer_id:
        for product in products:
            liked = has_liked_product(buyer_id, product['Product_ID'], product['Shop_ID'], product['Seller_ID'])
            like_status[product['Product_ID']] = liked

    return render_template(
        'buyer_cat_wearable_tech.html',
        products=products,
        total_pages=total_pages,
        current_page=page,
        like_status=like_status,
        min_price=min_price,
        max_price=max_price,
        sort=sort
    )

@buyer_bp.route('/buyer_cat_digital_accs')
def buyer_cat_digital_accs():
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    page = int(request.args.get('page', 1))
    sort = request.args.get('sort', 'recent')
    
    products, total_pages = get_category_products('Digital Accessories', min_price=min_price, max_price=max_price, page=page, sort=sort)
    
    buyer_id = session.get('user_id')
    like_status = {}
    
    if buyer_id:
        for product in products:
            liked = has_liked_product(buyer_id, product['Product_ID'], product['Shop_ID'], product['Seller_ID'])
            like_status[product['Product_ID']] = liked

    return render_template(
        'buyer_cat_digital_accs.html',
        products=products,
        total_pages=total_pages,
        current_page=page,
        like_status=like_status,
        min_price=min_price,
        max_price=max_price,
        sort=sort
    )

@buyer_bp.route('/buyer_cat_others')
def buyer_cat_others():
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    page = int(request.args.get('page', 1))
    sort = request.args.get('sort', 'recent')
    
    products, total_pages = get_category_products('Others', min_price=min_price, max_price=max_price, page=page, sort=sort)
    
    buyer_id = session.get('user_id')
    like_status = {}
    
    if buyer_id:
        for product in products:
            liked = has_liked_product(buyer_id, product['Product_ID'], product['Shop_ID'], product['Seller_ID'])
            like_status[product['Product_ID']] = liked

    return render_template(
        'buyer_cat_others.html',
        products=products,
        total_pages=total_pages,
        current_page=page,
        like_status=like_status,
        min_price=min_price,
        max_price=max_price,
        sort=sort
    )
    
@buyer_bp.route('/logout')
def logout():
    session.clear()  # Clear the session to reset to guest mode
    return render_template('buyer_homepage.html', buyer_name="Guest")
