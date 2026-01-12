# FoodSnap Backend & ML Pipeline

This repository contains the backend API and Machine Learning pipeline for the FoodSnap application.

## 📂 Project Structure

- `backend/`: FastAPI application code.
- `ml/`: Machine Learning training scripts and model definitions.
- `data/`: (Not included) Placeholder for dataset.
- `Dockerfile`: Configuration for containerizing the backend.

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Google Cloud Platform Account
- `gcloud` CLI installed

### 1. Machine Learning Pipeline

#### Dataset Setup
Prepare your dataset in the `data/` folder with the following structure:
```
data/
  train/
    pizza/
    burger/
    salad/
  val/
    pizza/
    burger/
    salad/
```

#### Training the Model
1. Install ML dependencies:
   ```bash
   pip install -r ml/requirements.txt
   ```
2. Run the training script:
   ```bash
   python ml/train.py --data_dir ./data --model_dir ./ml/models
   ```
   This will save `food_model_YYYYMMDD_HHMMSS.keras` and `class_indices.json` in `ml/models/`.

### 2. Backend API Setup

#### Local Development
1. Install Backend dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Place your trained model in `ml/models/` and update `MODEL_FILENAME` in `backend/main.py` (or set env var).
   *   **Note**: If no model is found, the system runs in **Mock Mode**, returning random predictions for testing.
3. Set Environment Variables (Create a `.env` file or export them):
   ```bash
   export USDA_API_KEY="your_key"
   export EDAMAM_APP_ID="your_id"
   export EDAMAM_APP_KEY="your_key"
   ```
4. Run the server:
   ```bash
   # From the project root
   uvicorn backend.main:app --reload
   ```
5. Access documentation at `http://127.0.0.1:8000/docs`.

### 3. Google Cloud Deployment

#### Step 1: GCP Setup
1. Create a Google Cloud Project.
2. Enable APIs: Cloud Run, Cloud Build, Artifact Registry, Firestore, Cloud Storage.
3. Create a Storage Bucket for models (e.g., `food-snap-models`) and one for uploads (e.g., `food-snap-uploads`).
4. Upload your best `.keras` model and `class_indices.json` to the `food-snap-models` bucket.

#### Step 2: Firestore
1. Go to Firebase Console or GCP Console -> Firestore.
2. Create a database in "Native Mode".

#### Step 3: Build & Deploy (Cloud Run)
1. Authenticate:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
2. Build and Submit Container:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/food-snap-backend
   ```
3. Deploy to Cloud Run:
   ```bash
   gcloud run deploy food-snap-backend \
     --image gcr.io/YOUR_PROJECT_ID/food-snap-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars PROJECT_ID=YOUR_PROJECT_ID,GCS_BUCKET_NAME=food-snap-uploads,MODEL_BUCKET_NAME=food-snap-models,MODEL_FILENAME=food_model_latest.keras,USDA_API_KEY=your_key
   ```

#### Alternative: Firebase Functions (Gen 2)
Firebase Functions Gen 2 is built on Cloud Run. You can deploy this as a function using the `firebase` CLI.
1. Initialize Firebase in the root:
   ```bash
   firebase init functions
   ```
2. Choose Python and overwrite `functions/main.py` with code to wrap FastAPI.
   *   Note: It is generally recommended to use **Cloud Run** directly for full FastAPI applications to avoid adapter complexity.

### 🔑 Environment Variables

To get real nutrition data, you must obtain API keys from the following providers:

1.  **Edamam**: [Get Key Here](https://developer.edamam.com/food-database-api)
    *   Set `EDAMAM_APP_ID` and `EDAMAM_APP_KEY`.
    *   *Note: Requires attribution in the UI.*
2.  **USDA FoodData Central**: [Get Key Here](https://fdc.nal.usda.gov/api-guide.html)
    *   Set `USDA_API_KEY`.
3.  **Spoonacular**: [Get Key Here](https://spoonacular.com/food-api)
    *   Set `SPOONACULAR_API_KEY`.
4.  **Open Food Facts**: [Website](https://world.openfoodfacts.org/)
    *   No key required. Used as fallback.

| Variable | Description | Default |
|----------|-------------|---------|
| `GCS_BUCKET_NAME` | Bucket to store user uploaded images | `food-snap-uploads` |
| `MODEL_BUCKET_NAME` | Bucket where the model is stored | `food-snap-models` |
| `MODEL_FILENAME` | Name of the model file in the bucket | `latest_model.keras` |
| `GOOGLE_CLOUD_PROJECT`| GCP Project ID | `food-snap-project` |
| `USDA_API_KEY` | Key for USDA FoodData Central | None |
| `EDAMAM_APP_ID` | App ID for Edamam API | None |
| `EDAMAM_APP_KEY` | App Key for Edamam API | None |
| `SPOONACULAR_API_KEY` | Key for Spoonacular API | None |

### 🥑 External API Integration
The backend attempts to fetch nutrition data in this order:
1. **Edamam** (Requires App ID & Key)
2. **USDA** (Requires API Key)
3. **Spoonacular** (Requires API Key)
4. **Open Food Facts** (Free, no key required)
