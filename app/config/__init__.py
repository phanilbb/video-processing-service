import os

class Config:
    API_TOKEN = os.getenv('API_TOKEN', 'supersecretkey')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///videos')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    VIDEO_DIR = os.getenv('VIDEO_DIR', './uploads')

