from flask import Blueprint, render_template, session, request, jsonify, redirect, flash, url_for
from db_connection import get_db_connection
from mysql.connector import Error
import base64

buyer_product_show_bp = Blueprint('buyer_product_show', __name__)

@buyer_product_show_bp.route('/buyer_product_show/<int:product_id>')
def buyer_product_show(product_id):
    conn = get_db_connection()
    product = None
    like_status = {}
    product_images = []
    product_colors = []
    product_specs = []
    shop_profile = None
    shop_name = None
    seller_name = None

    if conn:
        try:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(""" 
                SELECT p.Product_ID, pi.Product_Info_ID, pi.Product_Name, pi.Product_Description, pi.Product_Price, pi.Product_Main_Picture,
                    p.Seller_ID, ss.Shop_ID, ss.Shop_Name, ss.Shop_Description, ss.Shop_Profile, 
                    CONCAT(spi.Firstname, ' ', spi.Lastname) AS Seller_Name,
                    COALESCE(AVG(r.Rating), 0) AS Average_Rating
                FROM products AS p
                JOIN product_info AS pi ON p.Product_Info_ID = pi.Product_Info_ID
                LEFT JOIN shop_rating AS r ON p.Product_ID = r.Product_ID
                JOIN seller_shop AS ss ON p.Seller_ID = ss.Seller_ID
                JOIN seller_accounts AS sa ON p.Seller_ID = sa.Seller_ID  -- Corrected join with seller_accounts
                JOIN seller_personal_info AS spi ON sa.Personal_ID = spi.Personal_ID  -- Join with seller_personal_info to get name
                WHERE p.Product_ID = %s AND p.Status = 'Active'
                GROUP BY p.Product_ID, pi.Product_Name, pi.Product_Description, pi.Product_Price, pi.Product_Main_Picture, 
                        ss.Shop_ID, ss.Shop_Profile, spi.Firstname, spi.Lastname
            """, (product_id,))

            product = cursor.fetchone()

            # Get the shop profile, shop name, and seller name
            shop_profile = product.get('Shop_Profile')
            shop_name = product.get('Shop_Name')
            seller_name = product.get('Seller_Name')

            # Query to get product images
            cursor.execute(""" 
                SELECT Product_Image 
                FROM product_image 
                WHERE Product_Info_ID = %s
            """, (product['Product_Info_ID'],))
            product_images = cursor.fetchall()

            # Query to get product colors
            cursor.execute("""
                SELECT Color_Name 
                FROM product_color
                WHERE Product_Info_ID = %s
            """, (product['Product_Info_ID'],))
            product_colors = cursor.fetchall()

            # Query to get product specifications
            cursor.execute("""
                SELECT Product_Specs_Type, Product_Specs_Content
                FROM product_specs
                WHERE Product_Info_ID = %s
            """, (product['Product_Info_ID'],))
            product_specs = cursor.fetchall()

            # Get liked products from session
            if 'liked_products' in session:
                liked_products = session['liked_products']
                like_status = {pid: True for pid in liked_products}

        except Error as e:
            print(f"Error fetching product details: {e}")
        finally:
            cursor.close()
            conn.close()

    if product:

        return render_template(
            'buyer_product_show.html',
            product=product,
            like_status=like_status,
            product_images=product_images,
            product_colors=product_colors,
            product_specs=product_specs,
            shop_profile=shop_profile,
            shop_name=shop_name,
            seller_name=seller_name
        )
    else:
        flash('Product not found.', 'danger')
        return redirect(url_for('buyer.buyer_homepage'))


