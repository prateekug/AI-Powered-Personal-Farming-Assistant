import os
import json
import numpy as np
from PIL import Image
import io

class DiseasePredictionService:
    """
    Pure Machine Learning Inference Service for Plant Disease Classification.
    Reproduces Krishi_Sakhi_Plant_Disease.ipynb pipeline exactly.
    """
    def __init__(self, models_dir):
        self.models_dir = models_dir
        self.model = None
        self.class_names = []
        self.is_loaded = False
        self._load_model_and_classes()

    def _load_model_and_classes(self):
        model_path = os.path.join(self.models_dir, 'plant_disease_model.keras')
        class_names_path = os.path.join(self.models_dir, 'class_names.json')
        
        if os.path.exists(class_names_path):
            try:
                with open(class_names_path, 'r', encoding='utf-8') as f:
                    self.class_names = json.load(f)
            except Exception as e:
                print(f"[DiseasePredictionService Warning] Failed to read class_names.json: {e}")
                
        if os.path.exists(model_path):
            try:
                import tensorflow as tf
                self.model = tf.keras.models.load_model(model_path)
                self.is_loaded = True
                print("[DiseasePredictionService] TensorFlow Keras Model loaded successfully.")
            except Exception as e:
                print(f"[DiseasePredictionService Warning] Failed to load plant_disease_model.keras: {e}")
        else:
            print(f"[DiseasePredictionService Info] Model binary not found at {model_path}. ML inference pending binary placement.")

    def preprocess_image(self, image_bytes):
        """
        Notebook Preprocessing Pipeline:
        1. Read bytes into PIL Image -> RGB
        2. Resize to target size (160, 160)
        3. Convert to numpy array & expand dims to (1, 160, 160, 3)
        4. Normalize pixels by 255.0
        """
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img = img.resize((160, 160))
        img_array = np.array(img, dtype=np.float32)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0
        return img_array

    def predict(self, image_bytes):
        """
        Returns PURE ML output: predicted_disease and confidence.
        """
        if not self.is_loaded or self.model is None:
            return {
                'model_loaded': False,
                'status': 'Pending Model Binary Placement',
                'message': 'The ML model binary (plant_disease_model.keras) is not present in backend/models/. Place trained model in backend/models/.'
            }

        img_array = self.preprocess_image(image_bytes)
        prediction = self.model.predict(img_array)
        
        predicted_index = int(np.argmax(prediction[0]))
        confidence = float(np.max(prediction[0]) * 100)
        
        if self.class_names and predicted_index < len(self.class_names):
            predicted_disease = self.class_names[predicted_index]
        else:
            predicted_disease = f"Class_{predicted_index}"
            
        return {
            'model_loaded': True,
            'predicted_disease': predicted_disease,
            'confidence': round(confidence, 2)
        }


class DiseaseInformationService:
    """
    Separate Informational Advisory Service for Agricultural Recommendations.
    """
    DISEASE_KNOWLEDGE_BASE = {
        'rust': {
            'disease_name': 'Leaf Rust',
            'description': 'Leaf rust is a fungal disease caused by Puccinia species producing orange-brown pustules on crop leaves.',
            'impact': [
                'Photosynthesis reduction by up to 35%',
                'Premature foliage yellowing and leaf loss',
                'Grain filling reduction up to 40%'
            ],
            'treatments': [
                {'icon': '💊', 'title': 'Fungicide Application', 'description': 'Apply Propiconazole (1ml/liter) or Tebuconazole (1ml/liter) foliar spray.'},
                {'icon': '🌱', 'title': 'Potassium Supplementation', 'description': 'Apply Sulphate of Potash at 50kg/acre to strengthen cell walls.'}
            ],
            'prevention_tips': [
                'Plant rust-resistant crop varieties.',
                'Maintain proper plant spacing for canopy ventilation.',
                'Rotate crops with non-host leguminous crops.'
            ]
        },
        'blight': {
            'disease_name': 'Leaf Blight',
            'description': 'Blight causes rapidly spreading dark lesions on foliage leading to leaf wilting.',
            'impact': [
                'Leaf tissue destruction',
                'Yield loss up to 50%',
                'Stunted plant growth'
            ],
            'treatments': [
                {'icon': '💊', 'title': 'Copper Fungicide Spray', 'description': 'Apply Copper Oxychloride (2.5g/liter) at early sign of symptoms.'}
            ],
            'prevention_tips': [
                'Use certified disease-free seeds.',
                'Avoid excessive nitrogen fertilization.'
            ]
        },
        'healthy': {
            'disease_name': 'Healthy Plant Leaf',
            'description': 'No disease symptoms detected. Leaves show green color and structural integrity.',
            'impact': [
                'Optimal photosynthetic efficiency',
                'Full crop yield potential expected'
            ],
            'treatments': [
                {'icon': '✅', 'title': 'Routine Maintenance', 'description': 'Continue standard balanced fertilization and irrigation.'}
            ],
            'prevention_tips': [
                'Monitor crops weekly for early detection.',
                'Maintain weed-free farm borders.'
            ]
        }
    }

    @classmethod
    def get_info(cls, predicted_disease, crop_type=None):
        clean_class = str(predicted_disease).lower().replace('_', ' ')
        
        if 'healthy' in clean_class:
            key = 'healthy'
        elif 'rust' in clean_class:
            key = 'rust'
        elif 'blight' in clean_class:
            key = 'blight'
        else:
            name = predicted_disease.replace('___', ' - ').replace('_', ' ').title()
            return {
                'disease_name': name,
                'description': f"Fungal or bacterial pathogen affecting {crop_type if crop_type else 'crop'} foliage.",
                'impact': [
                    'Photosynthetic tissue disruption',
                    'Yield reduction if untreated'
                ],
                'treatments': [
                    {'icon': '💊', 'title': 'Targeted Fungicide Spray', 'description': 'Apply broad-spectrum systemic fungicide as advised.'}
                ],
                'prevention_tips': [
                    'Ensure good canopy aeration.',
                    'Rotate crops regularly.'
                ]
            }
            
        info = cls.DISEASE_KNOWLEDGE_BASE[key]
        prefix = f"{crop_type.capitalize()} " if crop_type and key != 'healthy' else ""
        
        return {
            'disease_name': f"{prefix}{info['disease_name']}",
            'description': info['description'],
            'impact': info['impact'],
            'treatments': info['treatments'],
            'prevention_tips': info['prevention_tips']
        }
