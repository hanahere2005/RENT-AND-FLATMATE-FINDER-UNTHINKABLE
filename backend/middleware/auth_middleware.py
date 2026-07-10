from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from backend.models.user import User
from backend.models import db

def role_required(*roles):
    """
    Decorator to restrict access to specific roles.
    Expects JWT to be verified and role to be present in custom claims.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                user_role = claims.get("role")
                
                if user_role not in roles:
                    return jsonify({"error": "Forbidden: Access denied for this role"}), 403
                    
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({"error": "Unauthorized", "details": str(e)}), 401
        return wrapper
    return decorator

def admin_required(fn):
    return role_required('admin')(fn)

def owner_required(fn):
    return role_required('owner')(fn)

def tenant_required(fn):
    return role_required('tenant')(fn)
