from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import db
from models.database_models import User
from utils.validators import validate_email, validate_password

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    
    full_name = data.get('fullName')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')
    
    if not full_name or not str(full_name).strip():
        return jsonify({'success': False, 'error': 'Full name is required'}), 400
        
    is_valid_email, email_error = validate_email(email)
    if not is_valid_email:
        return jsonify({'success': False, 'error': email_error}), 400
        
    is_valid_pw, pw_error = validate_password(password)
    if not is_valid_pw:
        return jsonify({'success': False, 'error': pw_error}), 400
        
    if password != confirm_password:
        return jsonify({'success': False, 'error': 'Passwords do not match'}), 400
        
    # Check if user already exists
    existing_user = User.query.filter_by(email=email.strip().lower()).first()
    if existing_user:
        return jsonify({'success': False, 'error': 'Account with this email already exists'}), 400
        
    new_user = User(
        full_name=full_name.strip(),
        email=email.strip().lower()
    )
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    access_token = create_access_token(identity=str(new_user.id))
    
    return jsonify({
        'success': True,
        'message': 'Registration successful',
        'data': {
            'token': access_token,
            'user': new_user.to_dict()
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password are required'}), 400
        
    user = User.query.filter_by(email=str(email).strip().lower()).first()
    if not user or not user.check_password(password):
        return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
        
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'data': {
            'token': access_token,
            'user': user.to_dict()
        }
    }), 200
