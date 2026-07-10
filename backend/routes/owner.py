from flask import Blueprint
from backend.controllers.owner_controller import get_owner_listings, get_owner_requests, accept_request, reject_request

owner_bp = Blueprint('owner', __name__)

owner_bp.route('/listings', methods=['GET'])(get_owner_listings)
owner_bp.route('/requests', methods=['GET'])(get_owner_requests)
owner_bp.route('/requests/<int:request_id>/accept', methods=['POST'])(accept_request)
owner_bp.route('/requests/<int:request_id>/reject', methods=['POST'])(reject_request)
