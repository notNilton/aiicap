import requests
import time
import os
import io
from PIL import Image

API_URL = "http://localhost:8000"

def create_test_image():
    img = Image.new('RGB', (100, 100), color = (73, 109, 137))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def test_upload():
    print("Testing image upload...")
    image_data = create_test_image()
    
    files = {
        'file': ('test_image.png', image_data, 'image/png')
    }
    data = {
        'prompt': 'Test upload prompt'
    }
    
    try:
        response = requests.post(f"{API_URL}/upload", files=files, data=data)
        response.raise_for_status()
        result = response.json()
        print(f"Upload successful! Image ID: {result['image_id']}")
        return result['image_id']
    except Exception as e:
        print(f"Upload failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

def verify_correction(image_id):
    print(f"Verifying correction for image {image_id}...")
    max_retries = 10
    retry_interval = 10 # seconds
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{API_URL}/images/{image_id}")
            response.raise_for_status()
            result = response.json()
            
            print(f"Status: {result['status']}, Corrections: {result['corrections']}")
            
            if result['status'] == 'processed':
                print("Success! Image has been corrected.")
                return True
            
            print(f"Waiting for correction... ({i+1}/{max_retries})")
            time.sleep(retry_interval)
        except Exception as e:
            print(f"Verification failed: {e}")
            time.sleep(retry_interval)
            
    print("Verification timed out.")
    return False

if __name__ == "__main__":
    img_id = test_upload()
    if img_id:
        verify_correction(img_id)
