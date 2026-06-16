import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def test_chat():
    print("Sending chat request to live server...")
    
    payload = {
        # Using a small model to test onboarding/loading
        "model": "Qwen/Qwen2.5-1.5B-Instruct",
        "messages": [
            {"role": "user", "content": "Write a 2 sentence poem about a server."}
        ],
        "password": "dhruv" # Triggers the dynamic onboarding logic if not present
    }
    
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/chat/completions", json=payload, timeout=300)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nSuccess! (Took {end_time - start_time:.2f} seconds)")
            print(f"Routed to Model: {data.get('route', {}).get('model_id')}")
            print(f"Routed to Deployment: {data.get('route', {}).get('deployment_id')}")
            print(f"Message: {data.get('message')}")
        else:
            print(f"\nError ({response.status_code}): {response.text}")
    except requests.exceptions.ConnectionError:
        print("\nFailed to connect. Is Uvicorn running on localhost:8000?")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    test_chat()
