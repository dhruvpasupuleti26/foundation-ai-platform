import sys
import httpx


def query_qwen():
	# Check for valid prompt

	if len(sys.argv) < 2:
		print("Please enter a valid prompt!")
		return

	user_prompt  = " ".join(sys.argv[1:])

	url = "http://localhost:8001/v1/chat/completions"
	payload = {
	    "model": "Qwen/Qwen2.5-7B-Instruct",
	    "messages": [
	        {"role": "user", "content": user_prompt}
	    ],
	    "temperature": 0.7
	}

	try:
	        response = httpx.post(url, json=payload, timeout=60.0)
	        # Check for successful connection status
	        if response.status_code == 200:
	            # Parse the raw network string into a py dict
	            json_data = response.json()
	
	            # Extract the final message text
	            clean_answer = json_data["choices"][0]["message"]["content"]
	            
	            print("\nQwen Response:")
	            print(clean_answer)
	        else:
	            # Server responded but returned an error status code
	            print(f"Error from server (Status {response.status_code}): {response.text}")
	            
	except Exception as e:
	        # Network failed to reach port 8001
	        print(f"Failed to reach the container on port 8001. Is it running? Details: {e}")
	
if __name__ == "__main__":
    query_qwen()
