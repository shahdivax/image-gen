from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import requests
import io
from PIL import Image
import base64
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['HF_API_TOKEN'] = os.getenv('HF_API_TOKEN')
app.config['HF_API_URL'] = "https://api-inference.huggingface.co/models/"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/models', methods=['GET'])
def get_models():
    response = requests.get(
        "https://huggingface.co/api/models",
        params={"search":"flux","limit":500,"full":"True","config":"True"},
        headers={"Authorization": f"Bearer {app.config['HF_API_TOKEN']}"}
    )
    if response.status_code == 200:
        models = response.json()
        lora_models = [model['modelId'] for model in models if ('tags' in model and 'lora' in model['tags']) and model.get('inference') == 'warm']
        return jsonify(lora_models)
    else:
        return jsonify({"error": "Failed to fetch models"}), 500

@app.route('/api/generate', methods=['POST'])
def generate_image():
    data = request.json
    model = data.get('model')
    prompt = data.get('prompt')
    
    if not model or not prompt:
        return jsonify({"error": "Model and prompt are required"}), 400
    
    # Fetch the model's README from Hugging Face
    readme_url = f"https://huggingface.co/{model}/raw/main/README.md"
    response = requests.get(readme_url)
    
    if response.status_code == 200:
        # Parse the README to extract the instance_prompt
        readme = response.text
        instance_prompt = None
        for line in readme.split('\n'):
            if line.startswith('instance_prompt:'):
                instance_prompt = line.split(':')[1].strip()
                break
        
        # Append the instance_prompt to the user's prompt if it exists
        if instance_prompt:
            prompt = f"{prompt}, {instance_prompt}"
    
    api_url = f"{app.config['HF_API_URL']}{model}"
    headers = {"Authorization": f"Bearer {app.config['HF_API_TOKEN']}"}
    print(f"model: {model}, instance: {instance_prompt}")
    response = requests.post(api_url, headers=headers, json={"inputs": prompt})
    
    if response.status_code == 200:
        image = Image.open(io.BytesIO(response.content))
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        print(f"image: {image}")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return jsonify({"image": img_str})
    else:
        return jsonify({"error": "Failed to generate image"}), 500

if __name__ == '__main__':
    app.run(port=5000)