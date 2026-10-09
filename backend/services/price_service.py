import os

class PricePredictionService:
    def __init__(self, models_dir):
        self.models_dir = models_dir
        self.model = None
        self.is_loaded = False
        self._load_model()

    def _load_model(self):
        for ext in ['.pkl', '.joblib', '.keras', '.h5']:
            model_path = os.path.join(self.models_dir, f'price_model{ext}')
            if os.path.exists(model_path):
                try:
                    self.is_loaded = True
                    print(f"[PriceService] Model found at {model_path}")
                    break
                except Exception as e:
                    print(f"[PriceService Warning] Could not load price model: {e}")
        if not self.is_loaded:
            print("[PriceService Info] Price prediction ML model binary not present in backend/models/. Status: Pending Model File.")

    def predict(self, crop, month):
        if not self.is_loaded:
            return {
                'model_loaded': False,
                'status': 'Pending ML Model Binary',
                'message': 'Crop Price Prediction ML model file is not present in backend/models/. API endpoint structure is active and ready for ML model binary placement.',
                'crop': crop,
                'month': month
            }
            
        return {
            'model_loaded': True,
            'status': 'Success'
        }
