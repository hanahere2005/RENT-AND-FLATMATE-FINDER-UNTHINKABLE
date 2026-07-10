from flask import Blueprint
from backend.controllers.notification_controller import get_notifications, mark_read, mark_all_read

notifications_bp = Blueprint('notifications', __name__)

notifications_bp.route('', methods=['GET'])(get_notifications)
notifications_bp.route('/read-all', methods=['POST'])(mark_all_read)
notifications_bp.route('/<int:notification_id>/read', methods=['POST'])(mark_read)
