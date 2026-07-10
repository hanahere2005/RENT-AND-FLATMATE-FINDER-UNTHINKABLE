from flask import Blueprint
from backend.controllers.tenant_controller import get_profile, update_profile, get_sent_requests

tenant_bp = Blueprint('tenant', __name__)

tenant_bp.route('/profile', methods=['GET'])(get_profile)
tenant_bp.route('/profile', methods=['POST', 'PUT'])(update_profile)
tenant_bp.route('/requests', methods=['GET'])(get_sent_requests)
