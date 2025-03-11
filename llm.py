from flask import Flask, request, jsonify
import ollama
import os

# Define API key directly in the script
API_KEY = "secretkey"

# Dictionary to store API keys and credits
API_KEY_CREDITS = {API_KEY: 10}  # Set initial credits

app = Flask(__name__)  # Create Flask app instance

# Middleware to verify API key
def verify_api_key():
    x_api_key = request.headers.get("x-api-key")
    if not x_api_key or x_api_key != API_KEY:
        return jsonify({"error": "INVALID KEY!"}), 401
    if API_KEY_CREDITS[x_api_key] <= 0:
        return jsonify({"error": "NO CREDITS LEFT!"}), 403
    return x_api_key

@app.route("/generate", methods=["POST"])
def generate():
    x_api_key = verify_api_key()
    if isinstance(x_api_key, tuple):  # Check if an error response was returned
        return x_api_key
    
    data = request.get_json()
    if not data or "prompt" not in data:
        return jsonify({"error": "Missing prompt in request body"}), 400

    prompt = data["prompt"]

    # Deduct one credit
    API_KEY_CREDITS[x_api_key] -= 1

    try:
        response = ollama.chat(
            model="mistral-7b-instruct-v0.3_masid-v1-q4_k_m:latest",
            messages=[{"role": "user", "content": prompt}]
        )
        return jsonify({
            "response": response["message"]["content"],
            "credits_remaining": API_KEY_CREDITS[x_api_key]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Explicitly bind to port 8082
    app.run(debug=True, host="0.0.0.0", port=port)
