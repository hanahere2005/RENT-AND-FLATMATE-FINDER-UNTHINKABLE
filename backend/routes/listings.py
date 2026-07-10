from flask import Blueprint
from backend.controllers.listing_controller import (
    create_listing, get_listings, get_listing_details, update_listing, delete_listing, mark_listing_filled
)
from backend.controllers.tenant_controller import send_interest_request

listings_bp = Blueprint('listings', __name__)

listings_bp.route('', methods=['GET'])(get_listings)
listings_bp.route('', methods=['POST'])(create_listing)
listings_bp.route('/<int:listing_id>', methods=['GET'])(get_listing_details)
listings_bp.route('/<int:listing_id>', methods=['PUT'])(update_listing)
listings_bp.route('/<int:listing_id>', methods=['DELETE'])(delete_listing)
listings_bp.route('/<int:listing_id>/fill', methods=['POST'])(mark_listing_filled)
listings_bp.route('/<int:listing_id>/interest', methods=['POST'])(send_interest_request)
