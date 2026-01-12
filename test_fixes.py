#!/usr/bin/env python3
"""
Test script for the fixed food prediction system
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from ml.fixed_inference import FoodPredictor
import json

def test_predictor():
    print("Testing Fixed Food Predictor...")
    print("=" * 50)
    
    # Test with different confidence thresholds
    thresholds = [0.3, 0.6, 0.8]
    
    for threshold in thresholds:
        print(f"\nTesting with confidence threshold: {threshold}")
        print("-" * 30)
        
        predictor = FoodPredictor(
            model_path=None,  # Will use mock mode
            confidence_threshold=threshold
        )
        
        # Run multiple predictions to see different outcomes
        for i in range(5):
            result = predictor.predict("dummy_image")
            print(f"Prediction {i+1}:")
            print(f"  Food: {result['class']}")
            print(f"  Confidence: {result['confidence']:.2f}")
            print(f"  Is Unknown: {result.get('is_unknown', False)}")
            print()

def test_class_indices():
    print("Testing Class Indices Loading...")
    print("=" * 50)
    
    class_indices_path = os.path.join("ml", "class_indices.json")
    if os.path.exists(class_indices_path):
        with open(class_indices_path, 'r') as f:
            classes = json.load(f)
        print("Available food classes:")
        for idx, food in classes.items():
            print(f"  {idx}: {food}")
    else:
        print("Class indices file not found!")

if __name__ == "__main__":
    test_class_indices()
    test_predictor()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("The system should now:")
    print("1. Return 'Unknown food' for low confidence predictions")
    print("2. Not force predictions to only chapati/paneer butter masala")
    print("3. Show confidence scores in the frontend")
    print("4. Handle unknown foods gracefully")