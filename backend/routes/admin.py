from flask import Blueprint
from backend.controllers.admin_controller import get_analytics, list_users, delete_user, list_listings, delete_listing

admin_bp = Blueprint('admin', __name__)

admin_bp.route('/analytics', methods=['GET'])(get_analytics)
admin_bp.route('/users', methods=['GET'])(list_users)
admin_bp.route('/users/<int:user_id>', methods=['DELETE'])(delete_user)
admin_bp.route('/listings', methods=['GET'])(list_listings)
admin_bp.route('/listings/<int:listing_id>', methods=['DELETE'])(delete_listing)
