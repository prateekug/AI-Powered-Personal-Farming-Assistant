from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.database_models import User

def jwt_user_required():
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                user = User.query.get(user_id)
                if not user:
                    return jsonify({'success': False, 'error': 'User not found'}), 401
                return fn(current_user=user, *args, **kwargs)
            except Exception as e:
                return jsonify({'success': False, 'error': 'Unauthorized authentication token required: ' + str(e)}), 401
        return wrapper
    return decorator
