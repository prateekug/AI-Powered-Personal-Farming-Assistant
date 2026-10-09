import os
import io
import sys
from PIL import Image

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
from app import app

def run_tests():
    with app.app_context():
        from models import db
        db.drop_all()
        db.create_all()
    client = app.test_client()
    print("--- Starting FarmAI Backend Verification Suite ---")

    # 1. Test Health Check
    res = client.get('/api/health')
    assert res.status_code == 200
    print("✅ Health Check Passed:", res.get_json())

    # 2. Test User Registration
    signup_data = {
        'fullName': 'Test Farmer',
        'email': 'farmer@example.com',
        'password': 'password123',
        'confirmPassword': 'password123'
    }
    res = client.post('/api/auth/register', json=signup_data)
    assert res.status_code == 201
    token = res.get_json()['data']['token']
    print("✅ Auth Register Passed. Token received.")

    headers = {'Authorization': f'Bearer {token}'}

    # 3. Test User Login
    login_data = {'email': 'farmer@example.com', 'password': 'password123'}
    res = client.post('/api/auth/login', json=login_data)
    assert res.status_code == 200
    print("✅ Auth Login Passed.")

    # 4. Test Land Details API
    land_payload = {
        'landSize': 5.5,
        'location': 'Punjab, India',
        'soilType': 'loamy',
        'irrigation': 'drip'
    }
    res = client.post('/api/farm/details', json=land_payload, headers=headers)
    assert res.status_code == 200
    print("✅ Save Land Details Passed:", res.get_json()['message'])

    res = client.get('/api/farm/details', headers=headers)
    assert res.status_code == 200 and res.get_json()['data']['location'] == 'Punjab, India'
    print("✅ Get Land Details Passed.")

    # Test Complete Farm Profile API
    res = client.get('/api/farm/profile', headers=headers)
    assert res.status_code == 200 and res.get_json()['data']['land_details']['location'] == 'Punjab, India'
    print("✅ Get Complete Farm Profile (GET /api/farm/profile) Passed.")

    # 5. Test Previous Crop API
    crop_payload = {
        'cropType': 'wheat',
        'yield': 4.2,
        'season': 'rabi',
        'fertilizerUsed': 'NPK 12:32:16'
    }
    res = client.post('/api/farm/previous-crop', json=crop_payload, headers=headers)
    assert res.status_code == 200
    print("✅ Save Previous Crop Passed.")

    # 6. Test Soil Details API
    soil_payload = {
        'soilMoisture': 45.0,
        'phLevel': 6.8,
        'nitrogen': 120.0,
        'phosphorus': 45.0,
        'potassium': 180.0,
        'organicMatter': 2.5
    }
    res = client.post('/api/farm/soil', json=soil_payload, headers=headers)
    assert res.status_code == 200
    print("✅ Save Soil Details Passed.")

    # 7. Test Planting Schedule API
    sched_payload = {
        'plantingDate': '2026-10-15',
        'season': 'rabi'
    }
    res = client.post('/api/farm/schedule', json=sched_payload, headers=headers)
    assert res.status_code == 200
    print("✅ Save Planting Schedule Passed.")

    # 8. Test Crop Recommendation API
    res = client.post('/api/crop/recommend', headers=headers)
    assert res.status_code == 200
    print("✅ Crop Recommendation API Passed:", res.get_json()['data']['status'])

    # 9. Test Price Prediction API
    price_payload = {'crop': 'wheat', 'month': 11}
    res = client.post('/api/price/predict', json=price_payload, headers=headers)
    assert res.status_code == 200
    print("✅ Price Prediction API Passed:", res.get_json()['data']['status'])

    # 10. Test Plant Disease Image Upload API
    img = Image.new('RGB', (200, 200), color='green')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    data = {
        'image': (img_byte_arr, 'test_leaf.jpg'),
        'cropType': 'wheat'
    }
    res = client.post('/api/disease/predict', data=data, headers=headers, content_type='multipart/form-data')
    assert res.status_code == 200
    res_json = res.get_json()['data']
    disease_status = res_json.get('disease_name') or res_json.get('status')
    print("✅ Disease Detection API Passed:", disease_status)

    print("\n🎉 ALL BACKEND ENDPOINTS PASSED VERIFICATION VERIFIED SUCCESSFULLY!")

if __name__ == '__main__':
    run_tests()
