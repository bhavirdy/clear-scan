# ClearScan Flask Application Initialization
from flask import Flask

# Create Flask application
app = Flask(__name__)

# Load configuration from config.py
app.config.from_pyfile('config.py')

# Import routes after initializing app to avoid circular imports
from app import routes








