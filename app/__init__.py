from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    app.config['HF_API_TOKEN'] = os.getenv('HF_API_TOKEN')
    app.config['HF_API_URL'] = "https://api-inference.huggingface.co/models/"

    from .routes import main
    app.register_blueprint(main)

    return app