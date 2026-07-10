from .auth import auth_bp
from .listings import listings_bp
from .tenant import tenant_bp
from .owner import owner_bp
from .chat import chat_bp
from .notifications import notifications_bp
from .admin import admin_bp

def register_routes(app):
    # Register blueprints with appropriate url prefixes as requested in user API list
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(listings_bp, url_prefix='/listings')
    app.register_blueprint(tenant_bp, url_prefix='/tenant')
    app.register_blueprint(owner_bp, url_prefix='/owner')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # We can also add a simple endpoint for general compatibility details or recalculations if needed
    @app.route('/compatibility/recalculate', methods=['POST'])
    def compatibility_stub():
        return {"message": "Recalculation occurs dynamically upon profile and listing updates."}, 200
        
    @app.route('/users', methods=['GET'])
    def users_stub():
        return {"message": "Use /auth/me for current user details, or /admin/users for the administration control list."}, 200
