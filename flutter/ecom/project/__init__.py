from flask import Flask, g, session
import base64

from blueprints.login import login_bp
from blueprints.registration import registration_bp

from blueprints.buyer import buyer_bp
from blueprints.buyer_product_show import buyer_product_show_bp
from blueprints.buyer_profile import buyer_profile_bp
from blueprints.buyer_notifications import buyer_notifications_bp
from blueprints.buyer_order_tracking import buyer_order_tracking_bp
from blueprints.buyer_viewcart import buyer_viewcart_bp


from blueprints.seller import seller_bp
from blueprints.seller_registration import seller_registration_bp
from blueprints.seller_inventory import seller_inventory_bp
from blueprints.seller_vouchers import seller_vouchers_bp
from blueprints.seller_shop_profile import seller_shop_profile_bp
from blueprints.seller_orders import seller_orders_bp
from blueprints.seller_notifications import seller_notifications_bp
from blueprints.seller_messages import seller_messages_bp
from blueprints.seller_finance import seller_finance_bp
from blueprints.seller_dashboard import seller_dashboard_bp
from blueprints.seller_settings import seller_settings_bp

from blueprints.seller_inventory import check_and_notify_stock_zero_or_nearly_out 
from blueprints.seller_vouchers import check_and_notify_vouchers

from blueprints.admin import admin_bp
from blueprints.admin_buyer_management import admin_buyer_management_bp
from blueprints.admin_seller_management import admin_seller_management_bp
from blueprints.admin_courier_management import admin_courier_management_bp
from blueprints.admin_shipping import admin_shipping_bp
from blueprints.admin_notifications import admin_notifications_bp


def create_app():
    app = Flask(__name__, static_folder='static')
    app.secret_key = 'jsdjhajb12nadkjw' 
    
    # NOTIFICATIONS
    @app.before_request
    def check_stock_notifications():
        """Middleware to check for stock notifications."""
        user_id = session.get('user_id')
        if user_id:
            check_and_notify_stock_zero_or_nearly_out(seller_id=user_id, nearly_out_threshold=10)
            check_and_notify_vouchers(seller_id=user_id)
    
    @app.template_filter('b64encode')
    def b64encode_filter(data):
        """Encodes binary data to base64 for use in Jinja templates."""
        if data:
            return base64.b64encode(data).decode('utf-8')
        return ''
    
    app.jinja_env.filters['b64encode'] = b64encode_filter

    app.register_blueprint(buyer_bp)
    app.register_blueprint(buyer_product_show_bp)
    app.register_blueprint(buyer_profile_bp)
    app.register_blueprint(buyer_notifications_bp)
    app.register_blueprint(buyer_order_tracking_bp)
    app.register_blueprint(buyer_viewcart_bp)


    app.register_blueprint(login_bp)
    app.register_blueprint(registration_bp)
    
    app.register_blueprint(seller_bp)
    app.register_blueprint(seller_registration_bp)
    app.register_blueprint(seller_inventory_bp)
    app.register_blueprint(seller_shop_profile_bp)
    app.register_blueprint(seller_vouchers_bp)
    app.register_blueprint(seller_notifications_bp)
    app.register_blueprint(seller_messages_bp)
    app.register_blueprint(seller_orders_bp)
    app.register_blueprint(seller_finance_bp)
    app.register_blueprint(seller_dashboard_bp)
    app.register_blueprint(seller_settings_bp)
    
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_buyer_management_bp)
    app.register_blueprint(admin_seller_management_bp)
    app.register_blueprint(admin_courier_management_bp)
    app.register_blueprint(admin_shipping_bp)
    app.register_blueprint(admin_notifications_bp)


    return app
