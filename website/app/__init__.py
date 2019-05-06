# app/__init__.py

from flask import Flask

# Initialize the app
app = Flask(__name__, instance_relative_config=True)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] =  'uploads' 

# Load the views
from app import main

# Load the config file
app.config.from_object('config')