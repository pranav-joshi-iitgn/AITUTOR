import requests
import json

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

    print(f"\n--- Sending Request for Model: {model} ---")
    
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
            print("✅ API Call Successful!")
            print(f"Generated Text:\n{response_data.get('generated_text')}\n")
        
        # Handle server-side errors (e.g., Missing model or Ollama connection error)
        else:
            print(f"❌ Server Error ({response.status_code}): {response_data.get('error', 'Unknown error')}")
            
    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP error codes like 401 (Unauthorized)
        try:
            error_details = e.response.json()
            print(f"❌ HTTP Error {e.response.status_code}: {error_details.get('error', 'Authentication or Client Error')}")
        except json.JSONDecodeError:
            print(f"❌ HTTP Error {e.response.status_code}: Could not parse error response from server.")
    
    except requests.exceptions.RequestException as e:
        # Handle network issues (e.g., server not running, connection timeout)
        print(f"❌ Connection Error: Could not connect to the server at {SERVER_URL}.")
        print(f"Details: {e}")

# --- TEST CASES ---

if __name__ == '__main__':
    
    # 1. Successful Request
    # print("\nTest 1\n")
    # get_llm_response(
    #     prompt="Write a two-line motivational quote about learning Python.", 
    #     model="qwen3:30B"
    # )

    # 2. Test Model Download/Check (Uses a model that might need to be pulled)
    # The server will initiate the pull and wait before responding.
    print("\nTest 2\n")
    get_llm_response(
        prompt="What is the capital of France?", 
        model="mistral" 
    )

    # 3. Test a different user/pass (You would modify the global variables for a real test)
    # For this demonstration, we'll keep the successful credentials and just show the function call.
    # To truly test the auth failure, you'd change USERNAME/PASSWORD temporarily.
    # The server log will show: ❌ HTTP Error 401: Authentication Failed. Invalid credentials.
    
    # Example of a malformed request (which the server should return a 400 for)
    # The authentication will pass, but the missing 'prompt' will trigger a server error response.
    # You would need to temporarily modify the payload in the function to test this, 
    # but the error handling is ready for it.
    
    print("\n--- Testing complete. Ensure your server (app.py) is running! ---")