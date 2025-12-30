from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from database import init_db
from routes.auth import auth_bp
from routes.mypage import mypage_bp
from routes.inquiry import inquiry_bp

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# CORS 설정
CORS(app, supports_credentials=True, origins=Config.CORS_ORIGINS)

# 데이터베이스 초기화
init_db()

# Blueprint 등록
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(mypage_bp, url_prefix='/api/mypage')
app.register_blueprint(inquiry_bp, url_prefix='/api/inquiry')

# 파일 다운로드
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
