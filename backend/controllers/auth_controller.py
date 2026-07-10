from flask import request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from backend.models import db, User, TenantProfile, OwnerProfile
from datetime import datetime

def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password') or not data.get('role'):
        return jsonify({"error": "Missing required fields: email, password, and role are required."}), 400
        
    email = data.get('email').strip().lower()
    password = data.get('password')
    role = data.get('role').strip().lower()
    
    if role not in ['tenant', 'owner']:
        return jsonify({"error": "Invalid role. Role must be 'tenant' or 'owner'."}), 400
        
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User with this email already exists."}), 400
        
    try:
        new_user = User(email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()  # Retrieve new_user.id
        
        # Initialize profiles based on role
        if role == 'tenant':
            # Create a shell tenant profile (can be updated in details later)
            tenant_profile = TenantProfile(
                user_id=new_user.id,
                preferred_location="Not specified",
                budget_min=0.0,
                budget_max=1000.0,  # Default budget
                move_in_date=datetime.utcnow().date(),
                occupation="Student / Professional",
                bio=""
            )
            db.session.add(tenant_profile)
        elif role == 'owner':
            owner_profile = OwnerProfile(
                user_id=new_user.id,
                company_name=data.get('company_name', ''),
                contact_phone=data.get('contact_phone', '0000000000')
            )
            db.session.add(owner_profile)
            
        db.session.commit()
        return jsonify({"message": "User registered successfully", "user": new_user.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Registration failed", "details": str(e)}), 500


def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing email or password"}), 400
        
    email = data.get('email').strip().lower()
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401
        
    # Standard identity is user.id
    identity = str(user.id)
    
    # Store role in custom claims
    access_token = create_access_token(identity=identity, additional_claims={"role": user.role})
    refresh_token = create_refresh_token(identity=identity, additional_claims={"role": user.role})
    
    # Get profile details if tenant or owner
    profile = None
    if user.role == 'tenant' and user.tenant_profile:
        profile = user.tenant_profile.to_dict()
    elif user.role == 'owner' and user.owner_profile:
        profile = user.owner_profile.to_dict()
        
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict(),
        "profile": profile
    }), 200


def refresh():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    new_access_token = create_access_token(identity=identity, additional_claims={"role": user.role})
    return jsonify({"access_token": new_access_token}), 200


@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    profile = None
    if user.role == 'tenant' and user.tenant_profile:
        profile = user.tenant_profile.to_dict()
    elif user.role == 'owner' and user.owner_profile:
        profile = user.owner_profile.to_dict()
        
    return jsonify({
        "user": user.to_dict(),
        "profile": profile
    }), 200
