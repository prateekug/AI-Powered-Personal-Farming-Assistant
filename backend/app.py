import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from models import db
from routes.auth import auth_bp
from routes.farm import farm_bp
from routes.crop import crop_bp
from routes.disease import disease_bp
from routes.price import price_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for frontend integration
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # JWT Error handlers
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({'success': False, 'error': 'Authentication token missing or invalid'}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return jsonify({'success': False, 'error': 'Invalid authentication token'}), 401

    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_payload):
        return jsonify({'success': False, 'error': 'Authentication token has expired. Please login again.'}), 401

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(farm_bp)
    app.register_blueprint(crop_bp)
    app.register_blueprint(disease_bp)
    app.register_blueprint(price_bp)

    # Health check route
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'success': True, 'status': 'FarmAI Backend API is running'}), 200

    # Global Error Handlers
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({'success': False, 'error': 'Bad Request: ' + str(error)}), 400

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'success': False, 'error': 'Resource not found'}), 404

    @app.errorhandler(422)
    def unprocessable_entity_error(error):
        return jsonify({'success': False, 'error': 'Unprocessable Entity / Validation error'}), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({'success': False, 'error': 'Internal Server Error'}), 500

    # Create tables automatically
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
