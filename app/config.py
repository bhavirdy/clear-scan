#api keys, secret keys, database url, 
import os

# Define base directory of the application
basedir = os.path.abspath(os.path.dirname(__file__))

# Configuration settings
class Config:
    # Secret key for protecting sessions
    SECRET_KEY = 'your_secret_key'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
