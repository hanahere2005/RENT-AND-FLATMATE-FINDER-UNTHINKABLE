import os
import sys

# Resolve module paths so it works whether run from root or backend directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

from backend.config import Config
from backend.models import db
from backend.routes import register_routes
from backend.sockets import register_socket_events

# Initialize SocketIO without app first
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Initialize Database
    db.init_app(app)
    
    # Initialize JWT Manager
    jwt = JWTManager(app)
    
    # Custom JWT claims loader to attach roles to token payloads
    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        # identity is the user id
        from backend.models.user import User
        user = User.query.get(identity)
        if user:
            return {"role": user.role}
        return {"role": "tenant"}
        
    # Register blueprints/routes
    register_routes(app)
    
    # Serve uploaded property photos
    @app.route('/uploads/<filename>', methods=['GET'])
    def serve_uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        
    @app.route('/', methods=['GET'])
    def api_root():
        return jsonify({"message": "Staylio API is running successfully.", "status": "online"}), 200
        
    # Standard Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Resource not found"}), 404
        
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500
        
    # Initialize SocketIO with app
    socketio.init_app(app)
    register_socket_events(socketio)
    
    # Automatically create tables and seed default admin user
    with app.app_context():
        # Ensure uploads folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
            
        db.create_all()
        try:
            db.session.execute(db.text("ALTER TABLE tenant_profiles ADD COLUMN lifestyle_habits TEXT"))
            db.session.commit()
            print("Successfully added lifestyle_habits column to tenant_profiles table.")
        except Exception:
            db.session.rollback()
        
        # Create a default admin user if it does not exist
        from backend.models.user import User
        for email in ["admin@staylio.com", "admin@rentflatmate.com"]:
            admin_user = User.query.filter_by(email=email).first()
            if not admin_user:
                admin = User(email=email, role="admin")
                admin.set_password("admin123")
                db.session.add(admin)
        db.session.commit()
            
    return app

app = create_app()

if __name__ == '__main__':
    # Run the application using socketio runner which supports websockets
    # Run on port 5000 by default
    socketio.run(app, host='0.0.0.0', port=5050, debug=True, allow_unsafe_werkzeug=True)
