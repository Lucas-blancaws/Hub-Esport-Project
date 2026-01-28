import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ta-cle-secrete-dev'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://localhost/hub_esport_db'
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
