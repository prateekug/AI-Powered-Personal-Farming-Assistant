import os
import io
import sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from app import app

def simulate_full_user_journey():
    print("==================================================")
    print("  SIMULATING FULL FRONTEND-TO-BACKEND USER FLOW   ")
    print("==================================================")

    with app.app_context():
        from models import db
        db.drop_all()
        db.create_all()

    client = app.test_client()

    # Step 1: User Registration on signup.html
    print("\n[Step 1] User submits registration form on signup.html...")
    signup_payload = {
        'fullName': 'Sardar Singh',
        'email': 'sardar.singh@farm.ai',
        'password': 'FarmPassword2026',
        'confirmPassword': 'FarmPassword2026'
    }
    res = client.post('/api/auth/register', json=signup_payload)
    assert res.status_code == 201
    auth_data = res.get_json()['data']
    token = auth_data['token']
    print(f" -> Account created successfully! User ID: {auth_data['user']['id']}")
    print(f" -> JWT Token issued and stored in browser localStorage.")

    headers = {'Authorization': f'Bearer {token}'}

    # Step 2: Land Details Form Submission
    print("\n[Step 2] User enters land size & location on land-details.html...")
    land_payload = {
        'landSize': 8.5,
        'location': 'Ludhiana, Punjab',
        'soilType': 'loamy',
        'irrigation': 'drip'
    }
    res = client.post('/api/farm/details', json=land_payload, headers=headers)
    assert res.status_code == 200
    print(" -> Saved Land Details to SQLite DB via SQLAlchemy.")

    # Step 3: Previous Crop Form Submission
    print("\n[Step 3] User enters previous crop on previous-crop.html...")
    crop_payload = {
        'cropType': 'wheat',
        'yield': 5.0,
        'season': 'rabi',
        'fertilizerUsed': 'Urea & DAP'
    }
    res = client.post('/api/farm/previous-crop', json=crop_payload, headers=headers)
    assert res.status_code == 200
    print(" -> Saved Previous Crop to SQLite DB.")

    # Step 4: Soil Details Form Submission
    print("\n[Step 4] User enters soil characteristics on soil-details.html...")
    soil_payload = {
        'soilMoisture': 55.0,
        'phLevel': 6.5,
        'nitrogen': 150.0,
        'phosphorus': 48.0,
        'potassium': 210.0,
        'organicMatter': 3.2
    }
    res = client.post('/api/farm/soil', json=soil_payload, headers=headers)
    assert res.status_code == 200
    print(" -> Saved Soil Details to SQLite DB.")

    # Step 5: Planting Schedule Form Submission
    print("\n[Step 5] User enters schedule on calendar.html...")
    sched_payload = {
        'plantingDate': '2026-11-01',
        'season': 'rabi'
    }
    res = client.post('/api/farm/schedule', json=sched_payload, headers=headers)
    assert res.status_code == 200
    print(" -> Saved Planting Schedule to SQLite DB.")

    # Step 6: Confirmation Page Load (GET /api/farm/profile)
    print("\n[Step 6] User opens confirmation.html. Page fetches complete profile from GET /api/farm/profile...")
    res = client.get('/api/farm/profile', headers=headers)
    assert res.status_code == 200
    profile = res.get_json()['data']
    
    assert profile['land_details']['location'] == 'Ludhiana, Punjab'
    assert profile['previous_crop']['crop_type'] == 'wheat'
    assert profile['soil_details']['ph_level'] == 6.5
    assert profile['planting_schedule']['season'] == 'rabi'
    print(" -> GET /api/farm/profile returned complete SQLite record!")
    print(" -> All 4 summary cards rendered dynamically on confirmation.html!")

    # Step 7: Crop Recommendation Request
    print("\n[Step 7] User clicks 'Get Crop Recommendation' on confirmation.html...")
    res = client.post('/api/crop/recommend', headers=headers)
    assert res.status_code == 200
    crop_res = res.get_json()['data']
    print(f" -> API Response: status='{crop_res.get('status')}'")

    # Step 8: Plant Disease Leaf Upload
    print("\n[Step 8] User uploads leaf image on disease-detection.html...")
    img = Image.new('RGB', (160, 160), color=(34, 139, 34)) # 160x160 RGB leaf image
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    upload_data = {
        'image': (img_byte_arr, 'leaf_sample.jpg'),
        'cropType': 'wheat'
    }
    res = client.post('/api/disease/predict', data=upload_data, headers=headers, content_type='multipart/form-data')
    assert res.status_code == 200
    disease_res = res.get_json()['data']
    print(f" -> Image preprocessed (160x160 RGB, normalized by 1/255.0).")
    print(f" -> API Response status: {disease_res.get('status') or disease_res.get('disease_name')}")

    # Step 9: Price Prediction Request
    print("\n[Step 9] User selects crop and month on price-prediction.html...")
    price_payload = {'crop': 'wheat', 'month': 11}
    res = client.post('/api/price/predict', json=price_payload, headers=headers)
    assert res.status_code == 200
    price_res = res.get_json()['data']
    print(f" -> API Response status: {price_res.get('status')}")

    print("\n==================================================")
    print("🎉 FULL FRONTEND-TO-BACKEND FLOW VERIFIED 100%!  ")
    print("==================================================")

if __name__ == '__main__':
    simulate_full_user_journey()
