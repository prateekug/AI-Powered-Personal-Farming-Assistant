import os
import json
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from models import db
from models.database_models import DiseasePrediction, PredictionHistory
from utils.auth import jwt_user_required
from utils.validators import allowed_file

disease_bp = Blueprint('disease', __name__, url_prefix='/api/disease')

disease_service_instance = None

def get_disease_service():
    global disease_service_instance
    if disease_service_instance is None:
        from services.disease_service import DiseasePredictionService
        models_dir = current_app.config['MODELS_DIR']
        disease_service_instance = DiseasePredictionService(models_dir)
    return disease_service_instance

@disease_bp.route('/predict', methods=['POST'])
@jwt_user_required()
def predict_disease(current_user):
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file provided in request'}), 400
        
    file = request.files['image']
    crop_type = request.form.get('cropType') or request.form.get('cropSelect') or ''
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No image file selected'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid image file type. Allowed extensions: png, jpg, jpeg, webp'}), 400
        
    try:
        image_bytes = file.read()
        if not image_bytes:
            return jsonify({'success': False, 'error': 'Uploaded file is empty'}), 400
            
        filename = secure_filename(f"user_{current_user.id}_{file.filename}")
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        with open(save_path, 'wb') as f:
            f.write(image_bytes)
            
        # 1. Pure ML Prediction Service
        pred_service = get_disease_service()
        ml_result = pred_service.predict(image_bytes)
        
        if not ml_result.get('model_loaded', True):
            return jsonify({'success': True, 'data': ml_result}), 200

        # 2. Separate Disease Information Service
        from services.disease_service import DiseaseInformationService
        info_result = DiseaseInformationService.get_info(ml_result['predicted_disease'], crop_type)
        
        # Combine ML output + Info advisory for full response payload
        combined_result = {
            'model_loaded': True,
            'predicted_class': ml_result['predicted_disease'],
            'confidence': ml_result['confidence'],
            'disease_name': info_result['disease_name'],
            'description': info_result['description'],
            'impact': info_result['impact'],
            'treatments': info_result['treatments'],
            'prevention_tips': info_result['prevention_tips']
        }
        
        # DB Record
        disease_rec = DiseasePrediction(
            user_id=current_user.id,
            image_path=filename,
            crop_type=crop_type,
            predicted_disease=ml_result['predicted_disease'],
            confidence=ml_result['confidence']
        )
        db.session.add(disease_rec)
        
        history_rec = PredictionHistory(
            user_id=current_user.id,
            prediction_type='disease',
            input_data=json.dumps({'crop_type': crop_type, 'filename': filename}),
            result_data=json.dumps(combined_result)
        )
        db.session.add(history_rec)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': combined_result
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Failed to process disease prediction: {str(e)}'}), 500
