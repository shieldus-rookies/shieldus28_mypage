import os

class Config:
    SECRET_KEY = 'weak_secret_key_123'
    UPLOAD_FOLDER = 'uploads'
    DATABASE = 'vulnerable.db'
    
    # CORS 설정
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)