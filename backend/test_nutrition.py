import os
import sys
import json
import logging

# Add current directory to path to import backend modules
sys.path.append(os.getcwd())

from backend.nutrition_apis import NutritionService

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_nutrition_lookup():
    print("--- Nutrition API Tester ---")
    print("This script tests your API keys and the fallback logic.")
    print("Ensure you have set the environment variables (USDA_API_KEY, etc.)")
    print("----------------------------")

    service = NutritionService()

    # Check which keys are present
    print("\n[Configuration Check]")
    print(f"Edamam ID/Key: {'OK' if service.edamam_app_id and service.edamam_app_key else 'Missing'}")
    print(f"USDA Key:      {'OK' if service.usda_api_key else 'Missing'}")
    print(f"Spoonacular:   {'OK' if service.spoonacular_api_key else 'Missing'}")
    
    while True:
        food_name = input("\nEnter food name to look up (or 'q' to quit): ").strip()
        if food_name.lower() == 'q':
            break
        
        if not food_name:
            continue

        print(f"\nSearching for '{food_name}'...")
        try:
            result = service.get_nutrition_info(food_name)
            print("\n--- Result ---")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_nutrition_lookup()
