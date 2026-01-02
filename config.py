import os
from dotenv import load_dotenv

# Get the base directory (where config.py is located)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 취약점: 하드코딩된 secret key
# SECRET_KEY = 'vulnerable-secret-key-12345'
SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key') # 추가

# 데이터베이스 파일 경로
# DB_PATH = os.path.join(BASE_DIR, 'vulnerable_app.db')
DB_HOST = os.getenv('DB_HOST', 'localhost') # 추가
DB_PORT = int(os.getenv('DB_PORT', 3306)) # 추가
DB_USER = os.getenv('DB_USER', 'root') # 추가
DB_PASSWORD = os.getenv('DB_PASSWORD') # 추가
DB_NAME = os.getenv('DB_NAME', 'shieldus_bank') # 추가

# 업로드 폴더 설정
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
PROFILE_FOLDER = os.path.join(UPLOAD_FOLDER, 'profiles')
QNA_FOLDER = os.path.join(UPLOAD_FOLDER, 'qna')
RECEIPT_FOLDER = os.path.join(UPLOAD_FOLDER, 'receipts')

# 폴더 생성을 위한 리스트
UPLOAD_FOLDERS = [UPLOAD_FOLDER, PROFILE_FOLDER, QNA_FOLDER, RECEIPT_FOLDER]
