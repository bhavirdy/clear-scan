#all imports to application go here,
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# Create Flask application
app = Flask(__name__)

# Load configuration from config.py
app.config.from_pyfile('config.py')

# Initialize SQLAlchemy
#db = SQLAlchemy(app)

# Import routes after initializing app to avoid circular imports
from app import routes








