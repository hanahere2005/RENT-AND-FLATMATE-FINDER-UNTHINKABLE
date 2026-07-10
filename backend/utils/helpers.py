import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename):
    """Check if the uploaded file has an allowed image extension."""
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'webp', 'gif'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed

def save_uploaded_file(file):
    """
    Saves an uploaded file to the upload directory with a unique UUID filename.
    Returns the relative URL path or filename to be stored in the database.
    """
    if not file or not allowed_file(file.filename):
        return None
        
    filename = secure_filename(file.filename)
    # Generate unique filename using UUID to prevent collisions
    ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        
    filepath = os.path.join(upload_folder, unique_filename)
    file.save(filepath)
    
    # Return relative URL path for serving (e.g. /uploads/unique_filename.jpg)
    return f"/uploads/{unique_filename}"
