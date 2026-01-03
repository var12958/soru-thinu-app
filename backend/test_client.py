import requests

# URL of the API (Local or Cloud Run)
API_URL = "http://127.0.0.1:8080/predict"

# Path to the image you want to test
IMAGE_PATH = "test_food.jpg" 

def test_predict():
    if not os.path.exists(IMAGE_PATH):
        print(f"Please place a test image at {IMAGE_PATH}")
        return

    print(f"Sending {IMAGE_PATH} to {API_URL}...")
    
    with open(IMAGE_PATH, "rb") as f:
        files = {"file": ("image.jpg", f, "image/jpeg")}
        try:
            response = requests.post(API_URL, files=files)
            
            if response.status_code == 200:
                print("Success!")
                print(response.json())
            else:
                print("Error:")
                print(response.status_code)
                print(response.text)
        except Exception as e:
            print(f"Connection failed: {e}")

if __name__ == "__main__":
    import os
    test_predict()
