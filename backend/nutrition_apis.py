import os
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class NutritionService:
    def __init__(self):
        # API Keys - Loaded from Environment Variables
        # Use the .env file to set these values!
        self.edamam_app_id = os.getenv("EDAMAM_APP_ID")
        self.edamam_app_key = os.getenv("EDAMAM_APP_KEY")
        self.usda_api_key = os.getenv("USDA_API_KEY")
        self.spoonacular_api_key = os.getenv("SPOONACULAR_API_KEY")
        
        # User Agent for Open Food Facts
        self.user_agent = "FoodSnap/1.0 (test@example.com)"

    def get_nutrition_info(self, food_name: str) -> Dict[str, Any]:
        """
        Orchestrates the fallback logic: Edamam -> USDA -> Spoonacular -> Open Food Facts
        """
        print(f"Fetching nutrition for: {food_name}")
        
        # 1. Try Edamam
        if self.edamam_app_id and self.edamam_app_key:
            data = self._fetch_edamam(food_name)
            if data: return data
        
        # 2. Try USDA
        if self.usda_api_key:
            data = self._fetch_usda(food_name)
            if data: return data
            
        # 3. Try Spoonacular
        if self.spoonacular_api_key:
            data = self._fetch_spoonacular(food_name)
            if data: return data
            
        # 4. Try Open Food Facts (No key required usually)
        data = self._fetch_open_food_facts(food_name)
        if data: return data
        
        # 5. Fallback if all fail
        return self._default_fallback(food_name)

    def _normalize_response(self, food, calories, protein, carbs, fat, serving="1 serving", source="Estimated"):
        return {
            "food": food,
            "serving_size": serving,
            "calories": int(calories) if calories is not None else 0,
            "protein_g": round(protein, 1) if protein is not None else 0.0,
            "carbs_g": round(carbs, 1) if carbs is not None else 0.0,
            "fat_g": round(fat, 1) if fat is not None else 0.0,
            "source": source
        }

    def _fetch_edamam(self, query):
        try:
            url = "https://api.edamam.com/api/food-database/v2/parser"
            params = {
                "app_id": self.edamam_app_id,
                "app_key": self.edamam_app_key,
                "ingr": query
            }
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("parsed"):
                    item = data["parsed"][0]["food"]
                    nutrients = item.get("nutrients", {})
                    return self._normalize_response(
                        food=item.get("label", query),
                        calories=nutrients.get("ENERC_KCAL", 0),
                        protein=nutrients.get("PROCNT", 0),
                        carbs=nutrients.get("CHOCDF", 0),
                        fat=nutrients.get("FAT", 0),
                        serving="1 serving",
                        source="Edamam"
                    )
                elif data.get("hints"):
                    # Fallback to first hint
                    item = data["hints"][0]["food"]
                    nutrients = item.get("nutrients", {})
                    return self._normalize_response(
                        food=item.get("label", query),
                        calories=nutrients.get("ENERC_KCAL", 0),
                        protein=nutrients.get("PROCNT", 0),
                        carbs=nutrients.get("CHOCDF", 0),
                        fat=nutrients.get("FAT", 0),
                        serving="1 serving",
                        source="Edamam"
                    )
        except Exception as e:
            logger.error(f"Edamam API error: {e}")
        return None

    def _fetch_usda(self, query):
        try:
            url = "https://api.nal.usda.gov/fdc/v1/foods/search"
            params = {
                "api_key": self.usda_api_key,
                "query": query,
                "pageSize": 1
            }
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("foods"):
                    food = data["foods"][0]
                    nutrients = food.get("foodNutrients", [])
                    
                    def get_nutrient(name_id):
                        # Helper to find nutrient by id or name
                        for n in nutrients:
                            if n.get("nutrientName") == name_id or n.get("nutrientId") == name_id:
                                return n.get("value", 0)
                        return 0

                    # USDA Nutrient IDs (standard) or names
                    # Energy: 1008 (kcal), Protein: 1003, Fat: 1004, Carbs: 1005
                    calories = next((n['value'] for n in nutrients if n['nutrientId'] == 1008), 0)
                    protein = next((n['value'] for n in nutrients if n['nutrientId'] == 1003), 0)
                    fat = next((n['value'] for n in nutrients if n['nutrientId'] == 1004), 0)
                    carbs = next((n['value'] for n in nutrients if n['nutrientId'] == 1005), 0)
                    
                    return self._normalize_response(
                        food=food.get("description", query),
                        calories=calories,
                        protein=protein,
                        carbs=carbs,
                        fat=fat,
                        serving=food.get("servingSize", "100g"),
                        source="USDA"
                    )
        except Exception as e:
            logger.error(f"USDA API error: {e}")
        return None

    def _fetch_spoonacular(self, query):
        try:
            # Using Quick Answer Endpoint or Search
            url = "https://api.spoonacular.com/recipes/guessNutrition"
            params = {
                "apiKey": self.spoonacular_api_key,
                "title": query
            }
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Returns calories, carbs, fat, protein dicts with value and unit
                return self._normalize_response(
                    food=query,
                    calories=data.get("calories", {}).get("value"),
                    protein=data.get("protein", {}).get("value"),
                    carbs=data.get("carbs", {}).get("value"),
                    fat=data.get("fat", {}).get("value"),
                    serving="1 serving",
                    source="Spoonacular"
                )
        except Exception as e:
            logger.error(f"Spoonacular API error: {e}")
        return None

    def _fetch_open_food_facts(self, query):
        try:
            url = "https://world.openfoodfacts.org/cgi/search.pl"
            params = {
                "search_terms": query,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": 1
            }
            headers = {"User-Agent": self.user_agent}
            response = requests.get(url, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("products"):
                    product = data["products"][0]
                    nutriments = product.get("nutriments", {})
                    
                    return self._normalize_response(
                        food=product.get("product_name", query),
                        calories=nutriments.get("energy-kcal_100g", 0),
                        protein=nutriments.get("proteins_100g", 0),
                        carbs=nutriments.get("carbohydrates_100g", 0),
                        fat=nutriments.get("fat_100g", 0),
                        serving="100g",
                        source="OpenFoodFacts"
                    )
        except Exception as e:
            logger.error(f"OpenFoodFacts API error: {e}")
        return None

    def _default_fallback(self, query):
        # Last resort: generic estimation based on query length/random or just zeros
        # For now, return zeros with a warning
        return {
            "food": query,
            "serving_size": "Unknown",
            "calories": 0,
            "protein_g": 0,
            "carbs_g": 0,
            "fat_g": 0,
            "source": "Not Found"
        }
