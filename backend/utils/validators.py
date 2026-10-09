import re

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def validate_email(email):
    if not email or not isinstance(email, str):
        return False, "Email is required"
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email.strip()):
        return False, "Invalid email address format"
    return True, None

def validate_password(password):
    if not password or not isinstance(password, str):
        return False, "Password is required"
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, None

def validate_land_details(data):
    if not isinstance(data, dict):
        return False, "Invalid payload format"
    
    land_size = data.get('landSize')
    location = data.get('location')
    soil_type = data.get('soilType')
    irrigation = data.get('irrigation')
    
    if land_size is None or location is None or soil_type is None or irrigation is None:
        return False, "All land detail fields (landSize, location, soilType, irrigation) are required"
    
    try:
        land_size_val = float(land_size)
        if land_size_val <= 0:
            return False, "Land size must be a positive number"
    except (ValueError, TypeError):
        return False, "Land size must be a valid numeric value"
        
    if not str(location).strip():
        return False, "Location cannot be empty"
        
    return True, None

def validate_soil_details(data):
    if not isinstance(data, dict):
        return False, "Invalid payload format"
        
    moisture = data.get('soilMoisture')
    ph = data.get('phLevel')
    
    if moisture is None or ph is None:
        return False, "Soil moisture and pH level are required"
        
    try:
        moisture_val = float(moisture)
        if not (0 <= moisture_val <= 100):
            return False, "Soil moisture must be between 0% and 100%"
    except (ValueError, TypeError):
        return False, "Soil moisture must be a valid numeric value"
        
    try:
        ph_val = float(ph)
        if not (0 <= ph_val <= 14):
            return False, "pH level must be between 0 and 14"
    except (ValueError, TypeError):
        return False, "pH level must be a valid numeric value"
        
    for key in ['nitrogen', 'phosphorus', 'potassium', 'organicMatter']:
        val = data.get(key)
        if val is not None and val != "":
            try:
                num = float(val)
                if num < 0:
                    return False, f"{key} cannot be negative"
            except (ValueError, TypeError):
                return False, f"{key} must be a valid numeric value"
                
    return True, None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
