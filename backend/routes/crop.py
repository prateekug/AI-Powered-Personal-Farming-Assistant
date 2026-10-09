import json
from flask import Blueprint, request, jsonify, current_app
from models import db
from models.database_models import Farm, PreviousCrop, SoilData, PlantingSchedule, PredictionHistory
from utils.auth import jwt_user_required

crop_bp = Blueprint('crop', __name__, url_prefix='/api/crop')

crop_service_instance = None

def get_crop_service():
    global crop_service_instance
    if crop_service_instance is None:
        from services.crop_service import CropRecommendationService
        crop_service_instance = CropRecommendationService(current_app.config['MODELS_DIR'])
    return crop_service_instance

@crop_bp.route('/recommend', methods=['POST'])
@jwt_user_required()
def recommend_crop(current_user):
    # Fetch user's stored profile
    farm = Farm.query.filter_by(user_id=current_user.id).first()
    prev_crop = PreviousCrop.query.filter_by(user_id=current_user.id).first()
    soil = SoilData.query.filter_by(user_id=current_user.id).first()
    schedule = PlantingSchedule.query.filter_by(user_id=current_user.id).first()
    
    # Payload input from body (if passed directly) or from stored profile
    body_data = request.get_json(silent=True) or {}
    
    profile = {
        'land_details': farm.to_dict() if farm else body_data.get('landDetails'),
        'previous_crop': prev_crop.to_dict() if prev_crop else body_data.get('previousCrop'),
        'soil_details': soil.to_dict() if soil else body_data.get('soilDetails'),
        'planting_schedule': schedule.to_dict() if schedule else body_data.get('calendar')
    }
    
    service = get_crop_service()
    result = service.recommend(profile)
    
    # Record history
    history = PredictionHistory(
        user_id=current_user.id,
        prediction_type='crop',
        input_data=json.dumps(profile),
        result_data=json.dumps(result)
    )
    db.session.add(history)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': result
    }), 200
