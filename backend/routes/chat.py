from flask import Blueprint
from backend.controllers.chat_controller import get_chats, get_chat_history

chat_bp = Blueprint('chat', __name__)

chat_bp.route('/list', methods=['GET'])(get_chats)
chat_bp.route('/history/<int:chat_id>', methods=['GET'])(get_chat_history)
