# app.py

UPLOAD_FOLDER = 'uploads' 

app = Flask(__name__, instance_relative_config=True)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024