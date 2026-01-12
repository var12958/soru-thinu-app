import numpy as np
import json
import os
import random

# Optional TensorFlow import
try:
    import tensorflow as tf
    from PIL import Image
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("Warning: TensorFlow/Pillow not installed. Running in Mock Mode only.")

class FoodPredictor:
    def __init__(self, model_path=None, class_names_path=None, confidence_threshold=0.6):
        """
        Initialize predictor with confidence threshold for unknown food detection.
        """
        self.model = None
        self.class_names = None
        self.img_size = (224, 224)
        self.mock_mode = False
        self.confidence_threshold = confidence_threshold

        if model_path and os.path.exists(model_path) and TF_AVAILABLE:
            print(f"Loading model from {model_path}...")
            try:
                self.model = tf.keras.models.load_model(model_path)
                
                if class_names_path is None:
                    class_names_path = os.path.join(os.path.dirname(model_path), 'class_indices.json')
                
                if os.path.exists(class_names_path):
                    with open(class_names_path, 'r') as f:
                        class_data = json.load(f)
                        # Handle both formats: {"0": "class1"} or ["class1", "class2"]
                        if isinstance(class_data, dict):
                            self.class_names = [class_data[str(i)] for i in sorted(map(int, class_data.keys()))]
                        else:
                            self.class_names = class_data
                else:
                    print("Warning: class_indices.json not found. Using default Indian food classes.")
                    # Default Indian food classes for demo
                    self.class_names = [
                        "chapati", "paneer butter masala", "dal", "rice", "biryani",
                        "samosa", "dosa", "idli", "curry", "naan"
                    ]
            except Exception as e:
                print(f"Error loading model: {e}. Switching to Mock Mode.")
                self.mock_mode = True
        else:
            print("Model not found or TF missing. Initializing in MOCK MODE.")
            self.mock_mode = True
            # Default mock classes for demo
            self.class_names = [
                "chapati", "paneer butter masala", "dal", "rice", "biryani",
                "samosa", "dosa", "idli", "curry", "naan"
            ]

    def preprocess_image(self, image_path_or_file):
        """
        Preprocesses an image file or path for the model.
        """
        if not TF_AVAILABLE:
            return None

        if isinstance(image_path_or_file, str):
            img = tf.keras.preprocessing.image.load_img(image_path_or_file, target_size=self.img_size)
        else:
            # Assume it's a file-like object (BytesIO) from API upload
            img = Image.open(image_path_or_file).convert('RGB')
            img = img.resize(self.img_size)
            
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = img_array / 255.0
        img_array = tf.expand_dims(img_array, 0) # Create batch axis
        return img_array

    def predict(self, image_path_or_file):
        """
        Returns prediction with confidence threshold logic.
        """
        if self.mock_mode:
            return self._mock_predict()

        try:
            img_array = self.preprocess_image(image_path_or_file)
            predictions = self.model.predict(img_array)
            probs = tf.nn.softmax(predictions[0]).numpy()  # Apply softmax
            
            max_confidence = float(np.max(probs))
            predicted_idx = int(np.argmax(probs))
            
            # Apply confidence threshold
            if max_confidence < self.confidence_threshold:
                return {
                    "class": "Unknown food",
                    "confidence": max_confidence,
                    "items": ["Unknown food"],
                    "is_unknown": True
                }
            
            predicted_class = self.class_names[predicted_idx] if self.class_names else str(predicted_idx)
            
            return {
                "class": predicted_class,
                "confidence": max_confidence,
                "items": [predicted_class],
                "is_unknown": False
            }
            
        except Exception as e:
            print(f"Prediction failed: {e}. Returning mock result.")
            return self._mock_predict()

    def _mock_predict(self):
        """
        Mock prediction for testing without a trained model.
        """
        import time
        time.sleep(0.5)
        
        # Simulate realistic confidence distribution
        confidence = round(random.uniform(0.3, 0.95), 2)
        
        if confidence < self.confidence_threshold:
            return {
                "class": "Unknown food",
                "confidence": confidence,
                "items": ["Unknown food"],
                "is_mock": True,
                "is_unknown": True
            }
        
        predicted_class = random.choice(self.class_names)
        return {
            "class": predicted_class,
            "confidence": confidence,
            "items": [predicted_class],
            "is_mock": True,
            "is_unknown": False
        }

if __name__ == "__main__":
    # Example usage
    import sys
    predictor = FoodPredictor(sys.argv[1] if len(sys.argv) > 1 else None)
    result = predictor.predict("dummy_path")
    print(json.dumps(result, indent=2))