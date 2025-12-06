import requests
import json
from time import time

# --- CONFIGURATION ---

# IMPORTANT: Replace this with your server's IP address and port (e.g., '127.0.0.1:8000')
# SERVER_URL = "http://127.0.0.1:8000/generate" 
SERVER_URL = "http://10.0.177.29:8000/generate" 

# Credentials (Must match the USER_DB in your server's app.py)
USERNAME = "pranav"
PASSWORD = "PJI-XnbyCv&3"

# --- CLIENT FUNCTION ---

def get_llm_response(prompt: str, model: str):
    """
    Sends a request to the custom Ollama API server and handles the response.
    """
    
    # The payload structure that your Flask server expects
    payload = {
        "user": USERNAME,
        "pass": PASSWORD,
        "model": model,
        "prompt": prompt
    }
    
    try:
        # The 'json=' parameter automatically sets the Content-Type header to application/json
        # and serializes the dictionary into a JSON string.
        response = requests.post(SERVER_URL, json=payload, timeout=60)

        # Check for HTTP status codes (2xx is success)
        response.raise_for_status() 

        # Attempt to parse the JSON response from the server
        response_data = response.json()

        # Handle successful response (Status 200)
        if response.status_code == 200 and response_data.get('status') == 'success':
            # print("API Call Successful!")
            res = response_data.get('generated_text')
            # print(f"Generated Text:\n{res}\n")
            return res
        
        # Handle server-side errors (e.g., Missing model or Ollama connection error)
        else:
            return ConnectionError(f"Server Error ({response.status_code}): {response_data.get('error', 'Unknown error')}")
            
    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP error codes like 401 (Unauthorized)
        try:
            error_details = e.response.json()
            return ConnectionError(f"HTTP Error {e.response.status_code}: {error_details.get('error', 'Authentication or Client Error')}")
        except json.JSONDecodeError:
            return ConnectionError(f"HTTP Error {e.response.status_code}: Could not parse error response from server.")
    
    except requests.exceptions.RequestException as e:
        # Handle network issues (e.g., server not running, connection timeout)
        return ConnectionError(f"Could not connect to the server at {SERVER_URL}.\nDetails: {e}")

def test(test_number:int,model:str,prompt:str):
    print(f"\nTest {test_number}\n")
    print("Prompt:\n",prompt)
    t0 = time()
    res = get_llm_response(prompt=prompt,model=model)
    t1 = time()
    dt = float(t1 - t0)
    if isinstance(res,ConnectionError):raise res
    else: print(f"Response arrived in {dt:.2f} s from model \"{model}\":\n",res)

# --- TEST CASES ---

if __name__ == '__main__':
    test(1,"mistral","What is the capital of France?")
    test(2,"qwen3:0.6B","What is the capital of France?")
    test(3,"qwen3:1.7B","What is the capital of France?")
    test(4,"qwen3","What is the capital of France?") # latest / 8B
    # test(5,"qwen3:30B","Write a two-line motivational quote about learning Python.")
    print("\n\n--- Testing complete ---")