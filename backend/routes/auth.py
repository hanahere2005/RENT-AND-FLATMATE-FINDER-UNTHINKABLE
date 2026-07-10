from flask import Blueprint
from flask_jwt_extended import jwt_required
from backend.controllers.auth_controller import register, login, refresh, get_current_user

auth_bp = Blueprint('auth', __name__)

auth_bp.route('/register', methods=['POST'])(register)
auth_bp.route('/login', methods=['POST'])(login)
auth_bp.route('/refresh', methods=['POST'])(refresh)
auth_bp.route('/me', methods=['GET'])(get_current_user)
