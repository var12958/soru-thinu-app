"""
Food Predictor with Size Estimation and Nutrition Integration
"""
import torch
import timm
from PIL import Image
import torchvision.transforms as transforms
import cv2
import numpy as np

class FoodPredictor:
    def __init__(self, model_path, confidence_threshold=0.1):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load model
        checkpoint = torch.load(model_path, map_location='cpu')
        self.classes = checkpoint['classes']
        self.model = timm.create_model('efficientnet_b4', num_classes=len(self.classes))
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model = self.model.to(self.device)
        self.model.eval()
        
        # Transform
        self.transform = transforms.Compose([
            transforms.Resize((384, 384)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def estimate_size(self, image_path):
        """Estimate food size based on image analysis"""
        if isinstance(image_path, str):
            img = cv2.imread(image_path)
        else:
            # Convert PIL to cv2
            img_array = np.array(Image.open(image_path))
            img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale and find contours
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Find largest contour (assumed to be the food item)
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            
            # Estimate size based on area (rough approximation)
            img_area = img.shape[0] * img.shape[1]
            food_ratio = area / img_area
            
            if food_ratio > 0.3:
                return "large"
            elif food_ratio > 0.15:
                return "medium"
            else:
                return "small"
        
        return "medium"  # default
    
    def predict(self, image_path_or_file):
        """Predict food type and size"""
        # Load and preprocess image
        if isinstance(image_path_or_file, str):
            image = Image.open(image_path_or_file).convert('RGB')
        else:
            image = Image.open(image_path_or_file).convert('RGB')
        
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        # Predict
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted_idx = torch.max(probabilities, 1)
            
            confidence = confidence.item()
            predicted_class = self.classes[predicted_idx.item()]
        
        # Check confidence threshold
        if confidence < self.confidence_threshold:
            return {
                'class': 'Unknown food',
                'confidence': confidence,
                'size': 'unknown',
                'is_unknown': True
            }
        
        # Estimate size
        size = self.estimate_size(image_path_or_file)
        
        return {
            'class': predicted_class,
            'confidence': confidence,
            'size': size,
            'is_unknown': False
        }

def get_nutrition_data(food_name, size):
    """Get nutrition data based on food type and size"""
    
    # Map internal names to display names
    display_names = {
        'chapati': 'Chapati',
        'paneer_butter_masala': 'Paneer Butter Masala'
    }
    
    # Base nutrition data per serving
    nutrition_db = {
        'chapati': {
            'small': {'calories': 80, 'protein_g': 3, 'carbs_g': 15, 'fat_g': 1, 'serving_size': '1 small chapati (6 inch)'},
            'medium': {'calories': 120, 'protein_g': 4, 'carbs_g': 22, 'fat_g': 2, 'serving_size': '1 medium chapati (7 inch)'},
            'large': {'calories': 160, 'protein_g': 5, 'carbs_g': 30, 'fat_g': 3, 'serving_size': '1 large chapati (8 inch)'}
        },
        'paneer_butter_masala': {
            'small': {'calories': 250, 'protein_g': 12, 'carbs_g': 8, 'fat_g': 18, 'serving_size': '1 small bowl (100g)'},
            'medium': {'calories': 350, 'protein_g': 16, 'carbs_g': 12, 'fat_g': 25, 'serving_size': '1 medium bowl (150g)'},
            'large': {'calories': 450, 'protein_g': 20, 'carbs_g': 16, 'fat_g': 32, 'serving_size': '1 large bowl (200g)'}
        }
    }
    
    if food_name in nutrition_db and size in nutrition_db[food_name]:
        data = nutrition_db[food_name][size].copy()
        data['food'] = display_names.get(food_name, food_name)  # Use display name
        data['source'] = 'Database'
        return data
    
    # Default fallback
    return {
        'food': display_names.get(food_name, food_name),
        'calories': 200,
        'protein_g': 8.0,
        'carbs_g': 20.0,
        'fat_g': 10.0,
        'serving_size': '1 serving',
        'source': 'Estimated'
    }