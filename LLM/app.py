import os
import json
import sys
from functools import wraps
from flask import Flask, request, jsonify, Response
from waitress import serve
from werkzeug.security import generate_password_hash, check_password_hash
import ollama

# --- CONFIGURATION ---

# 1. Initialize Flask App and Ollama Client
app = Flask(__name__)
# Ollama Client defaults to http://localhost:11434. Adjust the host if necessary.
ollama_client = ollama.Client()

# 2. Mock User Database (Replace with a proper database in production)
# Passwords should ALWAYS be hashed and never stored in plaintext!
# Use generate_password_hash("password123") to create the hash
USER_DB = {
    "pranav": generate_password_hash("PJI-XnbyCv&3")
}

# --- AUTHENTICATION LOGIC ---

def authenticate_user(username, password):
    """Checks if the provided username and password are valid."""
    # 1. Check if the user exists
    if username not in USER_DB:
        return False
    
    # 2. Check the password hash
    hashed_password = USER_DB[username]
    return check_password_hash(hashed_password, password)

def auth_required(f):
    """
    A decorator to enforce authentication based on the JSON payload.
    It expects 'user' and 'pass' fields in the POST request body.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.get_json(silent=True)
        if data is None:
             # Try to get data from form if not JSON, though JSON is preferred
             data = request.form

        username = data.get('user')
        password = data.get('pass')

        if not username or not password or not authenticate_user(username, password):
            # Standard HTTP 401 response for API authentication failure
            return jsonify({"error": "Authentication Failed. Invalid credentials."}), 401
            
        return f(*args, **kwargs)
    return decorated

def ensure_model_available(client: ollama.Client, model_name: str):
    """
    Checks if a model is available locally. If not, it pulls the model.
    """
    try:
        # Check if the model exists locally by listing models and checking for a match.
        # A simpler way is often just attempting to pull it, which is idempotent (only downloads if needed).
        print(f"Checking for model: {model_name}...")
        
        # Use the pull function. Ollama is smart; it only downloads if the model
        # isn't present or is outdated.
        # NOTE: Ollama will block the process until the download is complete.
        print(f"Attempting to pull model '{model_name}'. This may take time...")
        client.pull(model=model_name)
        print(f"Model '{model_name}' is ready.")
        return True
        
    except Exception as e:
        print(f"Error checking or pulling model '{model_name}': {e}")
        # Return False to indicate the model is NOT ready
        return False
    
# --- API ROUTE ---

@app.route('/generate', methods=['POST'])
@auth_required
def generate_llm_response():
    """
    Endpoint to receive request, authenticate, call Ollama, and return response.
    Expected JSON format: {"user": "...", "pass": "...", "model": "...", "prompt": "..."}
    """
    data = request.get_json()
    
    # Data is guaranteed to exist and have 'user'/'pass' because of @auth_required
    model_name = data.get('model')
    prompt_text = data.get('prompt')

    # 1. Validate required LLM fields
    if not model_name or not prompt_text:
        return jsonify({"error": "Missing required fields: 'model' or 'prompt'"}), 400
    
    if not ensure_model_available(ollama_client, model_name):
        return jsonify({
            "error": f"Failed to ensure model '{model_name}' availability. Check server logs."
        }), 503 # Service Unavailable

    # 2. Call Ollama (Using generate() for simplicity as requested)
    try:
        # Use a higher timeout since LLM generation can take time
        # The ollama library automatically handles the HTTP request to the local Ollama server
        response = ollama_client.generate(
            model=model_name,
            prompt=prompt_text,
            stream=False # Wait for the full response
        )
        
        # 3. Extract the generated text
        # Ollama's generate() returns a dict with the key 'response' containing the text
        generated_text = response.get('response', 'Error: No response text received from Ollama.')
        
        # 4. Return the result to the client
        return jsonify({
            "status": "success",
            "model": model_name,
            "generated_text": generated_text
        }), 200

    except ollama.RequestError as e:
        # This catches errors like 'model not found' or Ollama server connection issues
        return jsonify({"error": f"Ollama Request Error: {e}"}), 503
    except Exception as e:
        # Catch any other unexpected error
        return jsonify({"error": f"An internal server error occurred: {e}"}), 500

# --- RUN SERVER ---

if __name__ == '__main__':
    print("--- Starting LLM API Server ---")
    print("Ollama should be running on http://localhost:11434")
    # Using 0.0.0.0 to make it accessible on the local network (if needed)
    STATIC_IP = "0.0.0.0"
    if "--test" in sys.argv:
        print("Test endpoint: POST http://127.0.0.1:8000/generate")
        # app.run(host='127.0.0.1', port=8000, debug=True)
        serve(app,host='127.0.0.1',port=8000)
    else:
        print(f"API endpoint: POST http://{STATIC_IP}:8000/generate")
        # app.run(host=STATIC_IP,port=8000, debug=True)
        serve(app,host=STATIC_IP,port=8000)