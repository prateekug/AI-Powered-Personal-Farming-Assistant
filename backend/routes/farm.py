from flask import Blueprint, request, jsonify
from models import db
from models.database_models import Farm, PreviousCrop, SoilData, PlantingSchedule
from utils.auth import jwt_user_required
from utils.validators import validate_land_details, validate_soil_details

farm_bp = Blueprint('farm', __name__, url_prefix='/api/farm')

# --- Complete Farm Profile ---
@farm_bp.route('/profile', methods=['GET'])
@jwt_user_required()
def get_farm_profile(current_user):
    farm = Farm.query.filter_by(user_id=current_user.id).first()
    prev_crop = PreviousCrop.query.filter_by(user_id=current_user.id).first()
    soil = SoilData.query.filter_by(user_id=current_user.id).first()
    sched = PlantingSchedule.query.filter_by(user_id=current_user.id).first()
    
    return jsonify({
        'success': True,
        'data': {
            'land_details': farm.to_dict() if farm else None,
            'previous_crop': prev_crop.to_dict() if prev_crop else None,
            'soil_details': soil.to_dict() if soil else None,
            'planting_schedule': sched.to_dict() if sched else None
        }
    }), 200


# --- Land Details ---
@farm_bp.route('/details', methods=['POST'])
@jwt_user_required()
def save_farm_details(current_user):
    data = request.get_json(silent=True) or {}
    
    is_valid, error_msg = validate_land_details(data)
    if not is_valid:
        return jsonify({'success': False, 'error': error_msg}), 400
        
    farm = Farm.query.filter_by(user_id=current_user.id).first()
    if not farm:
        farm = Farm(user_id=current_user.id)
        db.session.add(farm)
        
    farm.land_size = float(data['landSize'])
    farm.location = str(data['location']).strip()
    farm.soil_type = str(data['soilType']).strip()
    farm.irrigation = str(data['irrigation']).strip()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Land details saved successfully',
        'data': farm.to_dict()
    }), 200


@farm_bp.route('/details', methods=['GET'])
@jwt_user_required()
def get_farm_details(current_user):
    farm = Farm.query.filter_by(user_id=current_user.id).first()
    if not farm:
        return jsonify({'success': True, 'data': None}), 200
    return jsonify({'success': True, 'data': farm.to_dict()}), 200


# --- Previous Crop ---
@farm_bp.route('/previous-crop', methods=['POST'])
@jwt_user_required()
def save_previous_crop(current_user):
    data = request.get_json(silent=True) or {}
    
    crop_type = data.get('cropType')
    season = data.get('season')
    
    if not crop_type or not season:
        return jsonify({'success': False, 'error': 'cropType and season are required'}), 400
        
    yield_val = None
    if data.get('yield') is not None and data.get('yield') != "":
        try:
            yield_val = float(data['yield'])
            if yield_val < 0:
                return jsonify({'success': False, 'error': 'Yield cannot be negative'}), 400
        except ValueError:
            return jsonify({'success': False, 'error': 'Yield must be numeric'}), 400
            
    crop_rec = PreviousCrop.query.filter_by(user_id=current_user.id).first()
    if not crop_rec:
        crop_rec = PreviousCrop(user_id=current_user.id)
        db.session.add(crop_rec)
        
    crop_rec.crop_type = str(crop_type).strip()
    crop_rec.yield_amount = yield_val
    crop_rec.season = str(season).strip()
    crop_rec.fertilizer_used = str(data.get('fertilizerUsed', '')).strip()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Previous crop details saved successfully',
        'data': crop_rec.to_dict()
    }), 200


@farm_bp.route('/previous-crop', methods=['GET'])
@jwt_user_required()
def get_previous_crop(current_user):
    crop_rec = PreviousCrop.query.filter_by(user_id=current_user.id).first()
    if not crop_rec:
        return jsonify({'success': True, 'data': None}), 200
    return jsonify({'success': True, 'data': crop_rec.to_dict()}), 200


# --- Soil Details ---
@farm_bp.route('/soil', methods=['POST'])
@jwt_user_required()
def save_soil_details(current_user):
    data = request.get_json(silent=True) or {}
    
    is_valid, error_msg = validate_soil_details(data)
    if not is_valid:
        return jsonify({'success': False, 'error': error_msg}), 400
        
    soil = SoilData.query.filter_by(user_id=current_user.id).first()
    if not soil:
        soil = SoilData(user_id=current_user.id)
        db.session.add(soil)
        
    soil.soil_moisture = float(data['soilMoisture'])
    soil.ph_level = float(data['phLevel'])
    soil.nitrogen = float(data['nitrogen']) if data.get('nitrogen') is not None and data.get('nitrogen') != "" else None
    soil.phosphorus = float(data['phosphorus']) if data.get('phosphorus') is not None and data.get('phosphorus') != "" else None
    soil.potassium = float(data['potassium']) if data.get('potassium') is not None and data.get('potassium') != "" else None
    soil.organic_matter = float(data['organicMatter']) if data.get('organicMatter') is not None and data.get('organicMatter') != "" else None
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Soil details saved successfully',
        'data': soil.to_dict()
    }), 200


@farm_bp.route('/soil', methods=['GET'])
@jwt_user_required()
def get_soil_details(current_user):
    soil = SoilData.query.filter_by(user_id=current_user.id).first()
    if not soil:
        return jsonify({'success': True, 'data': None}), 200
    return jsonify({'success': True, 'data': soil.to_dict()}), 200


# --- Planting Schedule ---
@farm_bp.route('/schedule', methods=['POST'])
@jwt_user_required()
def save_planting_schedule(current_user):
    data = request.get_json(silent=True) or {}
    
    planting_date = data.get('plantingDate')
    season = data.get('season')
    
    if not planting_date or not season:
        return jsonify({'success': False, 'error': 'plantingDate and season are required'}), 400
        
    sched = PlantingSchedule.query.filter_by(user_id=current_user.id).first()
    if not sched:
        sched = PlantingSchedule(user_id=current_user.id)
        db.session.add(sched)
        
    sched.planting_date = str(planting_date).strip()
    sched.season = str(season).strip()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Planting schedule saved successfully',
        'data': sched.to_dict()
    }), 200


@farm_bp.route('/schedule', methods=['GET'])
@jwt_user_required()
def get_planting_schedule(current_user):
    sched = PlantingSchedule.query.filter_by(user_id=current_user.id).first()
    if not sched:
        return jsonify({'success': True, 'data': None}), 200
    return jsonify({'success': True, 'data': sched.to_dict()}), 200
