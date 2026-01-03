import os
import json
import shutil
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Google Cloud & Firebase
from google.cloud import storage
import firebase_admin
from firebase_admin import credentials, firestore

# ML Inference (Importing from sibling directory requires sys.path hack or proper packaging)
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ml.inference import FoodPredictor
from backend.nutrition_apis import NutritionService

# --- Configuration ---
app = FastAPI(title="FoodSnap API", description="Food Recognition Backend")

# CORS
origins = ["*"] # Restrict this in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment Variables
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "food-snap-uploads")
MODEL_BUCKET_NAME = os.getenv("MODEL_BUCKET_NAME", "food-snap-models")
MODEL_FILENAME = os.getenv("MODEL_FILENAME", "latest_model.keras")
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "food-snap-project")

# --- Global State ---
predictor = None
nutrition_service = None
db = None
bucket = None

# --- Schemas ---
class NutritionInfo(BaseModel):
    food: str
    serving_size: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    source: Optional[str] = "Estimated"

class PredictionResponse(BaseModel):
    status: str
    items: List[NutritionInfo]
    total_calories: int
    image_url: Optional[str] = None
    prediction_id: Optional[str] = None

class ErrorResponse(BaseModel):
    detail: str

# --- Startup Events ---
@app.on_event("startup")
async def startup_event():
    global predictor, nutrition_service, db, bucket
    
    # 1. Initialize Firebase/Firestore
    try:
        if not firebase_admin._apps:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                'projectId': PROJECT_ID,
            })
        db = firestore.client()
        print("Firestore initialized.")
    except Exception as e:
        print(f"Warning: Firestore initialization failed (Local dev?): {e}")

    # 2. Initialize GCS
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        print("GCS initialized.")
    except Exception as e:
        print(f"Warning: GCS initialization failed: {e}")

    # 3. Load Model (Local or GCS)
    local_model_path = os.path.join("..", "ml", "models", MODEL_FILENAME)
    if not os.path.exists(local_model_path) and bucket: # Only try download if bucket client exists
        print(f"Model not found locally. Trying GCS...")
        try:
            model_bucket = storage_client.bucket(MODEL_BUCKET_NAME)
            blob = model_bucket.blob(MODEL_FILENAME)
            os.makedirs(os.path.dirname(local_model_path), exist_ok=True)
            blob.download_to_filename(local_model_path)
            print("Model downloaded from GCS.")
            
            # Also try to download class_indices.json
            indices_blob = model_bucket.blob("class_indices.json")
            indices_path = os.path.join(os.path.dirname(local_model_path), "class_indices.json")
            if indices_blob.exists():
                indices_blob.download_to_filename(indices_path)
        except Exception as e:
            print(f"Failed to download model from GCS: {e}")

    # Initialize Predictor (Will default to mock if model missing)
    predictor = FoodPredictor(local_model_path if os.path.exists(local_model_path) else None)
    
    # Initialize Nutrition Service
    nutrition_service = NutritionService()
    print("Services initialized.")

# --- Helper Functions ---
def upload_to_gcs(file_obj, filename, content_type):
    if not bucket:
        return None
    try:
        blob = bucket.blob(filename)
        blob.upload_from_file(file_obj, content_type=content_type)
        return blob.public_url
    except Exception as e:
        print(f"Upload failed: {e}")
        return None

# --- Endpoints ---

@app.get("/")
def health_check():
    return {
        "status": "running", 
        "model_loaded": predictor.model is not None,
        "mock_mode": predictor.mock_mode
    }

@app.post("/predict", response_model=PredictionResponse, responses={400: {"model": ErrorResponse}})
async def predict_food(file: UploadFile = File(...)):
    if not predictor:
        raise HTTPException(status_code=503, detail="System initializing...")

    # Validate Image
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Invalid image type. Only JPEG and PNG allowed.")

    try:
        # Run Inference
        contents = await file.read()
        from io import BytesIO
        image_stream = BytesIO(contents)
        
        prediction_result = predictor.predict(image_stream)
        detected_items = prediction_result.get("items", [prediction_result.get("class", "unknown")])
        confidence = prediction_result.get("confidence", 0.0)

        # Process each detected item
        response_items = []
        total_calories = 0
        
        for food_name in detected_items:
            # Fetch Nutrition Info
            nutrition_data = nutrition_service.get_nutrition_info(food_name)
            
            item = NutritionInfo(
                food=nutrition_data.get("food", food_name),
                serving_size=str(nutrition_data.get("serving_size", "Unknown")),
                calories=int(nutrition_data.get("calories", 0)),
                protein_g=float(nutrition_data.get("protein_g", 0)),
                carbs_g=float(nutrition_data.get("carbs_g", 0)),
                fat_g=float(nutrition_data.get("fat_g", 0)),
                source=nutrition_data.get("source", "Unknown")
            )
            response_items.append(item)
            total_calories += item.calories

        # Upload Image to GCS (Optional, for history)
        image_url = None
        if bucket:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"uploads/{timestamp}_{file.filename}"
            image_stream.seek(0) # Reset stream
            image_url = upload_to_gcs(image_stream, filename, file.content_type)

        # Save to Firestore (History)
        prediction_id = None
        if db:
            doc_ref = db.collection("predictions").document()
            doc_ref.set({
                "timestamp": firestore.SERVER_TIMESTAMP,
                "image_url": image_url,
                "detected_items": [item.dict() for item in response_items],
                "total_calories": total_calories,
                "confidence": confidence,
                "is_mock": predictor.mock_mode
            })
            prediction_id = doc_ref.id

        return PredictionResponse(
            status="success",
            items=response_items,
            total_calories=total_calories,
            image_url=image_url,
            prediction_id=prediction_id
        )

    except Exception as e:
        print(f"Error processing request: {e}")
        # Return structured error even for 500
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/history")
def get_history(limit: int = 10):
    if not db:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        docs = db.collection("predictions")\
                 .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                 .limit(limit)\
                 .stream()
        
        history = []
        for doc in docs:
            data = doc.to_dict()
            if "timestamp" in data and data["timestamp"]:
                data["timestamp"] = data["timestamp"].isoformat()
            history.append(data)
            
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
