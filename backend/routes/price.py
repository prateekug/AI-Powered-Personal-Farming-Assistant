import json
from flask import Blueprint, request, jsonify, current_app
from models import db
from models.database_models import PricePrediction, PredictionHistory
from utils.auth import jwt_user_required

price_bp = Blueprint('price', __name__, url_prefix='/api/price')

price_service_instance = None

def get_price_service():
    global price_service_instance
    if price_service_instance is None:
        from services.price_service import PricePredictionService
        price_service_instance = PricePredictionService(current_app.config['MODELS_DIR'])
    return price_service_instance

@price_bp.route('/predict', methods=['POST'])
@jwt_user_required()
def predict_price(current_user):
    data = request.get_json(silent=True) or {}
    
    crop = data.get('crop') or data.get('cropSelect')
    month = data.get('month') or data.get('predictionMonth')
    
    if not crop or month is None:
        return jsonify({'success': False, 'error': 'Both crop and month inputs are required'}), 400
        
    try:
        month_val = int(month)
        if not (1 <= month_val <= 12):
            return jsonify({'success': False, 'error': 'Prediction month must be an integer between 1 and 12'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Prediction month must be a valid numeric integer (1-12)'}), 400
        
    service = get_price_service()
    result = service.predict(str(crop).strip().lower(), month_val)
    
    price_rec = PricePrediction(
        user_id=current_user.id,
        crop_name=str(crop).strip().lower(),
        target_month=month_val,
        predicted_price=result.get('predicted_price'),
        confidence=result.get('confidence')
    )
    db.session.add(price_rec)
    
    history = PredictionHistory(
        user_id=current_user.id,
        prediction_type='price',
        input_data=json.dumps({'crop': crop, 'month': month_val}),
        result_data=json.dumps(result)
    )
    db.session.add(history)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': result
    }), 200
