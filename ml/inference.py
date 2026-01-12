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
    def __init__(self, model_path=None, class_names_path=None):
        """
        Initialize predictor. 
        If model_path is None or file doesn't exist, initializes in MOCK mode.
        """
        self.model = None
        self.class_names = None
        self.img_size = (224, 224)
        self.mock_mode = False

        if model_path and os.path.exists(model_path) and TF_AVAILABLE:
            print(f"Loading model from {model_path}...")
            try:
                self.model = tf.keras.models.load_model(model_path)
                
                if class_names_path is None:
                    class_names_path = os.path.join(os.path.dirname(model_path), 'class_indices.json')
                
                if os.path.exists(class_names_path):
                    with open(class_names_path, 'r') as f:
                        self.class_names = json.load(f)
                else:
                    print("Warning: class_indices.json not found. Predictions will return indices.")
            except Exception as e:
                print(f"Error loading model: {e}. Switching to Mock Mode.")
                self.mock_mode = True
        else:
            print("Model not found or TF missing. Initializing in MOCK MODE.")
            self.mock_mode = True
            # Default mock classes
            self.class_names = ["pizza", "burger", "salad", "pasta", "sushi"]

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
        Returns prediction.
        """
        if self.mock_mode:
            return self._mock_predict()

        try:
            img_array = self.preprocess_image(image_path_or_file)
            predictions = self.model.predict(img_array)
            probs = predictions[0]
            # Top-k
            top_k = min(5, len(probs))
            top_idx = np.argsort(probs)[::-1][:top_k]
            results = []
            for idx in top_idx:
                name = self.class_names[idx] if self.class_names else str(idx)
                results.append({"class": name, "score": float(probs[idx])})

            best = results[0]
            return {
                "class": best['class'],
                "confidence": best['score'],
                "top_k": results
            }
        except Exception as e:
            print(f"Prediction failed: {e}. Returning mock result.")
            return self._mock_predict()

    def _mock_predict(self):
        """
        Mock prediction for testing without a trained model.
        Returns a random food item from the list.
        """
        # Simulate processing time
        import time
        time.sleep(0.5)
        
        predicted_class = random.choice(self.class_names)
        return {
            "class": predicted_class,
            "confidence": round(random.uniform(0.7, 0.99), 2),
            "items": [predicted_class], # List for multi-label support
            "is_mock": True
        }

if __name__ == "__main__":
    # Example usage
    import sys
    predictor = FoodPredictor(sys.argv[1] if len(sys.argv) > 1 else None)
    result = predictor.predict("dummy_path")
    print(json.dumps(result, indent=2))
