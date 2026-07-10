from flask import Blueprint
from backend.controllers.tenant_controller import (
    get_profile, update_profile, get_sent_requests, get_compatibility, send_interest_request
)

tenant_bp = Blueprint('tenant', __name__)

tenant_bp.route('/profile', methods=['GET'])(get_profile)
tenant_bp.route('/profile', methods=['POST', 'PUT'])(update_profile)
tenant_bp.route('/requests', methods=['GET'])(get_sent_requests)
tenant_bp.route('/compatibility/<int:listing_id>', methods=['GET'])(get_compatibility)
tenant_bp.route('/interest/<int:listing_id>', methods=['POST'])(send_interest_request)
