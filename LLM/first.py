# I am using Qwen3 30B fom ollama


import ollama

def run_ollama_prompt(model_name: str, prompt: str):
    """
    Runs a prompt against a local Ollama model.
    """
    try:
        # Send the prompt to the Ollama model
        response = ollama.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract and return the model's reply
        return response['message']['content']
    
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    model = "qwen3:30B"  # Change to any model you have pulled
    res = ollama.pull(model)
    print("Result on pulling :",res)
    user_prompt = "Explain quantum computing in simple terms."
    
    reply = run_ollama_prompt(model, user_prompt)
    print("Ollama Response:\n", reply)
