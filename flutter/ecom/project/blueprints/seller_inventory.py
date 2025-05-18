from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from db_connection import get_db_connection

seller_inventory_bp = Blueprint('seller_inventory', __name__)

@seller_inventory_bp.route('/seller_inventory')
def seller_inventory():
    page = request.args.get('page', 1, type=int)  # Current page, default 1
    limit = 5  # Items per page
    offset = (page - 1) * limit
    category = request.args.get('category', 'All')  # Current category filter, default 'All'
    sort = request.args.get('sort', 'recent')  # Current sort option, default 'recent'
    search = request.args.get('search', '')  # Search query, default empty

    shop_profile = fetch_shop_profile()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch distinct product categories for the filter dropdown
        cursor.execute("""
            SELECT DISTINCT Product_Category 
            FROM products 
            WHERE Seller_ID = %s
        """, (session.get('user_id'),))
        product_categories = [row['Product_Category'] for row in cursor.fetchall()]

        # Base query for distinct Product_Info_IDs
        distinct_query = """
            SELECT p.Product_ID, p.Product_Info_ID, pi.Product_Name, pi.Product_Price, pi.Product_Description,
                   pi.Product_Main_Picture, p.Product_Category, 
                   pc.Product_Color_ID, pc.Color_Name, ps.Stock_Quantity, p.Time_Added
            FROM products p
            JOIN product_info pi ON p.Product_Info_ID = pi.Product_Info_ID
            LEFT JOIN product_color pc ON pi.Product_Info_ID = pc.Product_Info_ID
            LEFT JOIN product_stock ps ON ps.Product_Color_ID = pc.Product_Color_ID
            WHERE p.Seller_ID = %s AND p.Status = 'Active'
        """
        params = [session.get('user_id')]

        # Apply category filter if not 'All'
        if category != 'All':
            distinct_query += " AND p.Product_Category = %s"
            params.append(category)

        # Apply search filter
        if search.strip():
            distinct_query += """
                AND (
                    pi.Product_Name LIKE %s OR 
                    p.Product_Category LIKE %s OR 
                    pi.Product_Description LIKE %s OR
                    pc.Color_Name LIKE %s OR
                    ps.Stock_Quantity LIKE %s OR
                    pi.Product_Price LIKE %s
                )
            """
            params.extend([
                f"%{search}%",  # Product Name
                f"%{search}%",  # Product Category
                f"%{search}%",  # Product Description
                f"%{search}%",  # Color Name
                f"%{search}%",  # Stock Quantity
                f"%{search}%"   # Product Price
            ])

        # Sorting logic
        if sort == 'recent':
            distinct_query += " ORDER BY p.Time_Added DESC"
        elif sort == 'oldest':
            distinct_query += " ORDER BY p.Time_Added ASC"
        elif sort == 'nearly_out_of_stock':
            distinct_query += " AND ps.Stock_Quantity <= 10 AND ps.Stock_Quantity > 0 ORDER BY ps.Stock_Quantity ASC"
        elif sort == 'out_of_stock':
            distinct_query += " AND ps.Stock_Quantity = 0 ORDER BY ps.Stock_Quantity ASC"
        else:
            distinct_query += " ORDER BY p.Time_Added DESC"

        # Pagination limits
        distinct_query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        # Fetch distinct Product_Info_IDs for the current page
        cursor.execute(distinct_query, tuple(params))
        distinct_product_info_ids = [row['Product_Info_ID'] for row in cursor.fetchall()]

        # Fetch product details for these Product_Info_IDs
        if distinct_product_info_ids:
            query = """
                SELECT p.Product_ID, p.Product_Info_ID, pi.Product_Name, pi.Product_Price, pi.Product_Description,
                       pi.Product_Main_Picture, p.Product_Category, 
                       pc.Product_Color_ID, pc.Color_Name, ps.Stock_Quantity, p.Time_Added
                FROM products p
                JOIN product_info pi ON p.Product_Info_ID = pi.Product_Info_ID
                LEFT JOIN product_color pc ON pi.Product_Info_ID = pc.Product_Info_ID
                LEFT JOIN product_stock ps ON ps.Product_Color_ID = pc.Product_Color_ID
                WHERE p.Product_Info_ID IN ({})
                ORDER BY p.Time_Added DESC
            """.format(', '.join(['%s'] * len(distinct_product_info_ids)))
            cursor.execute(query, tuple(distinct_product_info_ids))
            products = cursor.fetchall()
        else:
            products = []

        # Group products by Product_Info_ID
        grouped_products = {}
        for product in products:
            if product['Product_Info_ID'] not in grouped_products:
                grouped_products[product['Product_Info_ID']] = []
            grouped_products[product['Product_Info_ID']].append(product)

        # Get total number of distinct Product_Info_IDs for correct pagination
        cursor.execute("""
            SELECT COUNT(DISTINCT p.Product_Info_ID) AS total 
            FROM products p
            WHERE p.Seller_ID = %s AND p.Status = 'Active'
        """, (session.get('user_id'),))
        total_products = cursor.fetchone()['total']
        total_pages = (total_products // limit) + (1 if total_products % limit else 0)

    except Exception as e:
        flash(f'Error retrieving product data: {e}', 'danger')
        grouped_products = {}
        total_pages = 1
        product_categories = []
    finally:
        cursor.close()
        conn.close()

    return render_template(
        'seller_inventory.html',
        grouped_products=grouped_products,
        page=page,
        total_pages=total_pages,
        limit=limit,
        product_categories=product_categories,
        selected_category=category,
        selected_sort=sort,
        search=search,
        shop_profile=shop_profile
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



@seller_inventory_bp.route('/add_product', methods=['POST'])
def add_product():
    if request.method == 'POST':
        # Get form data
        product_category = request.form['productCategory']
        product_name = request.form['productName']
        product_description = request.form['productDescription']
        product_price = request.form['productPrice']
        main_picture = request.files['productMainPicture']  # Get the main image file
        product_images = request.files.getlist('productImages[]')  # Get the list of images from the form
        specs_types = request.form.getlist('specType[]')
        specs_contents = request.form.getlist('specContent[]')
        color_variants = request.form.getlist('colorVariant[]')
        
        # Example seller ID - should be replaced with session ID
        seller_id = session.get('user_id')  # Replace with session or context-based ID

        # Database connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Check if a product with the same name, category, and color already exists
            for color in color_variants:
                if color:  # Check for non-empty color variant
                    print(f"Checking for existing product with name: {product_name}, category: {product_category}, color: {color}, seller_id: {seller_id}")
                    cursor.execute("""
                        SELECT 1
                        FROM products p
                        JOIN product_info pi ON p.Product_Info_ID = pi.Product_Info_ID
                        JOIN product_color pc ON pi.Product_Info_ID = pc.Product_Info_ID
                        WHERE p.Seller_ID = %s 
                              AND LOWER(TRIM(pi.Product_Name)) = LOWER(TRIM(%s))
                              AND LOWER(TRIM(p.Product_Category)) = LOWER(TRIM(%s))
                              AND LOWER(TRIM(pc.Color_Name)) = LOWER(TRIM(%s))
                    """, (seller_id, product_name, product_category, color))
                    existing_product = cursor.fetchone()

                    if existing_product:
                        flash(f'A product with the name "{product_name}", category "{product_category}", and color "{color}" already exists.', 'danger')
                        return redirect(url_for('seller_inventory.seller_inventory'))

            # Insert product info into product_info table
            if main_picture:  # If a main picture is uploaded
                main_picture_data = main_picture.read()  # Read main picture as BLOB
            else:
                main_picture_data = None  # Default to None if no main picture is provided

            cursor.execute("""
                INSERT INTO product_info (Product_Name, Product_Price, Product_Description, Product_Main_Picture)
                VALUES (%s, %s, %s, %s)
            """, (product_name, product_price, product_description, main_picture_data))
            product_info_id = cursor.lastrowid  # Get the ID of the newly inserted product_info

            # Insert product entry into products table
            cursor.execute("""
                INSERT INTO products (Seller_ID, Product_Info_ID, Product_Category, Total_Stocks, Status)
                VALUES (%s, %s, %s, %s, 'Active')
            """, (seller_id, product_info_id, product_category, 0))

            # Insert specifications into product_specs table
            for spec_type, spec_content in zip(specs_types, specs_contents):
                if spec_type and spec_content:  # Ensure non-empty specifications
                    cursor.execute("""
                        INSERT INTO product_specs (Product_Info_ID, Product_Specs_Type, Product_Specs_Content)
                        VALUES (%s, %s, %s)
                    """, (product_info_id, spec_type, spec_content))

            # Insert color variants into product_color and product_stock table
            for color in color_variants:
                if color:  # Ensure non-empty color variants
                    # Insert color into product_color table
                    cursor.execute("""
                        INSERT INTO product_color (Product_Info_ID, Color_Name)
                        VALUES (%s, %s)
                    """, (product_info_id, color))
                    product_color_id = cursor.lastrowid  # Get the ID of the newly inserted color

                    # Insert stock entry into product_stock table with quantity 0
                    cursor.execute("""
                        INSERT INTO product_stock (Product_Color_ID, Stock_Quantity)
                        VALUES (%s, %s)
                    """, (product_color_id, 0))  # Initial stock quantity is set to 0

            product_images = request.files.getlist('productImages[]')  # Correctly handling multiple files
            # Insert product images into product_image table
            for image in product_images:
                if image:  # Ensure image is selected
                    image_data = image.read()  # Read image data as BLOB
                    cursor.execute("""
                        INSERT INTO product_image (Product_Info_ID, Product_Image)
                        VALUES (%s, %s)
                    """, (product_info_id, image_data))  # Insert image into product_image table

            # Commit the transaction
            conn.commit()
            
             # Add notification for the product addition
            notification_title = "New Product Added"
            notification_message = f"Your product '{product_name}' has been added successfully!'{product_category}'."
            cursor.execute("""
                INSERT INTO notifications_seller 
                (recipient_id, recipient_role, notification_type, title, message, is_read)
                VALUES (%s, 'Seller', 'Product Added', %s, %s, 0)
            """, (seller_id, notification_title, notification_message))
            conn.commit()  

            flash('Product added successfully with specifications, color variants, main picture, and additional images!', 'success')
            return redirect(url_for('seller_inventory.seller_inventory'))

        except Exception as e:
            conn.rollback()
            flash(f'Error adding product: {e}', 'danger')
            return redirect(url_for('seller_inventory.seller_inventory'))

        finally:
            cursor.close()
            conn.close()

        
@seller_inventory_bp.route('/add_stock', methods=['POST'])
def add_stock():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        product_info_id = request.form.get('product_info_id')

        # Database connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Ensure we're using a dictionary cursor

        try:
            # Step 1: Check if the product_id matches the product_info_id in the products table
            cursor.execute(""" 
                SELECT p.Product_Info_ID, pi.Product_Name 
                FROM products p
                JOIN product_info pi ON p.Product_Info_ID = pi.Product_Info_ID
                WHERE p.Product_ID = %s AND p.Product_Info_ID = %s
            """, (product_id, product_info_id))
            product_check = cursor.fetchone()

            if not product_check:
                flash('Product ID and Product Info ID do not match.', 'danger')
                return redirect(url_for('seller_inventory.seller_inventory'))

            product_name = product_check['Product_Name']  # Get the product name from the query

            # Step 2: Loop through each color and update stock for the specific color
            color_ids = request.form.getlist('color_id')  # Get all color_ids
            for color_id in color_ids:
                # Get the quantity to add
                additional_stock = request.form.get(f'additional_stock_{color_id}', 0)
                additional_stock = int(additional_stock) if additional_stock else 0

                if additional_stock > 0:  # Only update if the quantity is greater than 0
                    # Fetch color name for this color_id
                    cursor.execute(""" 
                        SELECT Color_Name 
                        FROM product_color
                        WHERE Product_Color_ID = %s
                    """, (color_id,))
                    color_check = cursor.fetchone()

                    if color_check:
                        color_name = color_check['Color_Name']  # Get the color name

                        # Check if the product_stock entry exists for this color
                        cursor.execute(""" 
                            SELECT Stock_Quantity 
                            FROM product_stock
                            WHERE Product_Color_ID = %s
                        """, (color_id,))
                        stock_check = cursor.fetchone()

                        if stock_check:
                            current_stock = stock_check['Stock_Quantity']
                            new_stock = current_stock + additional_stock

                            # Update the stock quantity for the specific color
                            cursor.execute(""" 
                                UPDATE product_stock
                                SET Stock_Quantity = %s
                                WHERE Product_Color_ID = %s
                            """, (new_stock, color_id))

                            conn.commit()
                            flash(f'Successfully added {additional_stock} units to stock for color {color_name} in product {product_name}.', 'success')
                        else:
                            flash(f'Stock entry for color {color_name} not found in product {product_name}.', 'danger')
                    else:
                        flash(f'Color ID {color_id} not found in product {product_name}.', 'danger')

            return redirect(url_for('seller_inventory.seller_inventory'))

        except Exception as e:
            conn.rollback()
            flash(f'Error updating stock: {e}', 'danger')
            return redirect(url_for('seller_inventory.seller_inventory'))

        finally:
            cursor.close()
            conn.close()


@seller_inventory_bp.route('/archive_product/<int:product_id>', methods=['POST'])
def archive_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update the product status to 'Archived'
        cursor.execute("""
            UPDATE products
            SET Status = 'Archived'
            WHERE Product_ID = %s
        """, (product_id,))
        conn.commit()
        flash('Product archived successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error archiving product: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('seller_inventory.seller_inventory'))


@seller_inventory_bp.route('/unarchive_product/<int:product_id>', methods=['POST'])
def unarchive_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update the product status to 'Active'
        cursor.execute("""
            UPDATE products
            SET Status = 'Active'
            WHERE Product_ID = %s
        """, (product_id,))
        conn.commit()
        flash('Product unarchived successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error unarchiving product: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('seller_inventory.show_archived'))


@seller_inventory_bp.route('/show_archived')
def show_archived():
    page = request.args.get('page', 1, type=int)
    limit = 5
    offset = (page - 1) * limit

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get the total number of archived products
        cursor.execute("""SELECT COUNT(*) FROM products p WHERE p.Seller_ID = %s AND p.Status = 'Archived'""", (session.get('user_id'),))
        total_archived_products = cursor.fetchone()['COUNT(*)']
        total_pages = (total_archived_products // limit) + (1 if total_archived_products % limit else 0)

        # Get the archived products for the current page
        cursor.execute(""" 
            SELECT p.Product_ID, p.Product_Info_ID, pi.Product_Name, pi.Product_Price, pi.Product_Description,
                   pi.Product_Main_Picture, p.Product_Category, 
                   pc.Product_Color_ID, pc.Color_Name, ps.Stock_Quantity
            FROM products p
            JOIN product_info pi ON p.Product_Info_ID = pi.Product_Info_ID
            LEFT JOIN product_color pc ON pi.Product_Info_ID = pc.Product_Info_ID
            LEFT JOIN product_stock ps ON ps.Product_Color_ID = pc.Product_Color_ID
            WHERE p.Seller_ID = %s AND p.Status = 'Archived'
            ORDER BY p.Product_ID, pc.Product_Color_ID
            LIMIT %s OFFSET %s
        """, (session.get('user_id'), limit, offset))

        archived_products = cursor.fetchall()

        # Group archived products by Product_Info_ID
        grouped_archived_products = {}
        for product in archived_products:
            if product['Product_Info_ID'] not in grouped_archived_products:
                grouped_archived_products[product['Product_Info_ID']] = []
            grouped_archived_products[product['Product_Info_ID']].append(product)

    except Exception as e:
        flash(f'Error retrieving archived products: {e}', 'danger')
        grouped_archived_products = {}
        total_pages = 1

    finally:
        cursor.close()
        conn.close()

    return render_template('seller_inventory.html', grouped_products=grouped_archived_products, page=page, total_pages=total_pages, limit=limit, view_archived=True)

@seller_inventory_bp.route('/update_product', methods=['POST'])
def update_product():
    # Retrieve both IDs from the form
    product_id = request.form.get('product_id')  # Product_ID from the `products` table
    product_info_id = request.form.get('product_info_id')  # Product_Info_ID from the `product_info` table
    product_category = request.form.get('productCategory')
    product_name = request.form.get('productName')
    product_description = request.form.get('productDescription')
    product_price = request.form.get('productPrice')
    product_main_picture = request.files.get('productMainPicture')  # Get the main image file if uploaded

    # Debugging to verify received data
    print("Product ID (products table):", product_id)
    print("Product Info ID (product_info table):", product_info_id)
    print("Product Name:", product_name)
    print("Product Category:", product_category)
    print("Product Description:", product_description)
    print("Product Price:", product_price)

    # Database connection
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update product details in the `product_info` table
        if product_main_picture:
            # Read the image file data as BLOB
            main_picture_data = product_main_picture.read()
            cursor.execute("""
                UPDATE product_info 
                SET Product_Name = %s, Product_Price = %s, Product_Description = %s, 
                    Product_Main_Picture = %s 
                WHERE Product_Info_ID = %s
            """, (product_name, product_price, product_description, main_picture_data, product_info_id))
        else:
            # Update without changing the image
            cursor.execute("""
                UPDATE product_info 
                SET Product_Name = %s, Product_Price = %s, Product_Description = %s 
                WHERE Product_Info_ID = %s
            """, (product_name, product_price, product_description, product_info_id))

        # Update the product category in the `products` table
        cursor.execute("""
            UPDATE products 
            SET Product_Category = %s 
            WHERE Product_ID = %s
        """, (product_category, product_id))

        # Commit the transaction
        conn.commit()
        flash('Product updated successfully!', 'success')

    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        flash(f'Error updating product: {e}', 'danger')
        print("Error:", e)  # Debugging information

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

    # Redirect back to the inventory page
    return redirect(url_for('seller_inventory.seller_inventory'))




def check_and_notify_stock_zero_or_nearly_out(seller_id, nearly_out_threshold=10):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Step 1: Fetch products with zero stock
        cursor.execute("""
            SELECT ps.Product_Color_ID, ps.Stock_Quantity, p.Seller_ID, pi.Product_Name, pc.Color_Name
            FROM product_stock ps
            JOIN product_color pc ON ps.Product_Color_ID = pc.Product_Color_ID
            JOIN products p ON p.Product_Info_ID = pc.Product_Info_ID
            JOIN product_info pi ON pi.Product_Info_ID = p.Product_Info_ID
            WHERE p.Seller_ID = %s
        """, (seller_id,))
        products_stock = cursor.fetchall()  # Fetch all results

        if not products_stock:
            print(f"No products found for seller {seller_id}.")
            return  # No further action if no products are found

        print(f"Found {len(products_stock)} product(s) to check for stock notifications.")

        # Step 2: Process each product and create notifications as needed
        for product in products_stock:
            product_name = product['Product_Name']
            product_color_id = product['Product_Color_ID']
            product_color = product['Color_Name']
            stock_quantity = product['Stock_Quantity']

            # Check for "out of stock" condition
            if stock_quantity == 0:
                print(f"Checking 'out of stock' notification for product: {product_name} (Color: {product_color})")
                notification_title = f"Out of Stock: {product_name} ({product_color})"
                notification_message = f"The product {product_name} variant color of {product_color} is out of stock."

            # Check for "nearly out of stock" condition
            elif 0 < stock_quantity <= nearly_out_threshold:
                print(f"Checking 'nearly out of stock' notification for product: {product_name} (Color: {product_color})")
                notification_title = f"Nearly Out of Stock: {product_name} ({product_color})"
                notification_message = (
                    f"The product {product_name} variant color of {product_color} is nearly out of stock "
                    f"with only {stock_quantity} unit(s) remaining."
                )
            else:
                # Skip if stock is above the threshold
                continue

            # Check if a notification already exists for this product and condition
            cursor.execute("""
                SELECT 1
                FROM notifications_seller
                WHERE recipient_id = %s AND recipient_role = 'Seller' AND title = %s
            """, (seller_id, notification_title))
            existing_notification = cursor.fetchone()  # Fetch one result

            if existing_notification:
                print(f"Notification already exists for product: {product_name} (Color: {product_color}). Skipping.")
            else:
                # Insert a new notification
                cursor.execute("""
                    INSERT INTO notifications_seller (recipient_id, recipient_role, notification_type, title, message)
                    VALUES (%s, 'Seller', 'Stock Alert', %s, %s)
                """, (seller_id, notification_title, notification_message))
                print(f"Notification created for product: {product_name} (Color: {product_color}).")

        # Commit the transaction to save notifications
        conn.commit()
        print("Transaction committed successfully.")

    except Exception as e:
        print(f"Error checking stock and sending notifications: {e}")
        conn.rollback()  # Rollback the transaction on error
    finally:
        cursor.close()  # Close the cursor
        conn.close()  # Close the connection



