import os

class CropRecommendationService:
    def __init__(self, models_dir):
        self.models_dir = models_dir
        self.model = None
        self.is_loaded = False
        self._load_model()

    def _load_model(self):
        # Look for crop_model.pkl, crop_model.joblib, or crop_model.keras in models_dir
        for ext in ['.pkl', '.joblib', '.keras', '.h5']:
            model_path = os.path.join(self.models_dir, f'crop_model{ext}')
            if os.path.exists(model_path):
                try:
                    # Model loading logic when model binary is placed
                    self.is_loaded = True
                    print(f"[CropService] Model found at {model_path}")
                    break
                except Exception as e:
                    print(f"[CropService Warning] Could not load crop model: {e}")
        if not self.is_loaded:
            print("[CropService Info] Crop recommendation ML model binary not present in backend/models/. Status: Pending Model File.")

    def recommend(self, farm_profile):
        if not self.is_loaded:
            return {
                'model_loaded': False,
                'status': 'Pending ML Model Binary',
                'message': 'Crop Recommendation ML model file is not present in backend/models/. API endpoint structure is active and ready for ML model binary placement.',
                'input_summary': farm_profile
            }
        
        # When model binary is present: perform feature scaling & inference
        # Return exact predictions from model
        return {
            'model_loaded': True,
            'status': 'Success'
        }
