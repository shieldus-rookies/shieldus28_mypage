from flask import Flask, render_template
import os
import config
from routes import register_blueprints

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# 업로드 폴더 생성
for folder in config.UPLOAD_FOLDERS:
    os.makedirs(folder, exist_ok=True)


# ==================== 메인 페이지 ====================

@app.route('/')
def index():
    return render_template('index.html')


# ==================== 에러 핸들러 ====================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# ==================== Blueprint 등록 ====================

register_blueprints(app)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
