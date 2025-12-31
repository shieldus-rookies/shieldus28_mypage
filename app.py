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

# URL 별칭 추가 (템플릿 호환성을 위해)
# Blueprint의 'blueprint.function' 엔드포인트를 'function'으로도 접근 가능하게 함
app.add_url_rule('/login_alias', endpoint='login', view_func=app.view_functions.get('login.login'), methods=['GET', 'POST'])
app.add_url_rule('/register_alias', endpoint='register', view_func=app.view_functions.get('register.register'), methods=['GET', 'POST'])
app.add_url_rule('/logout_alias', endpoint='logout', view_func=app.view_functions.get('login.logout'))
app.add_url_rule('/dashboard_alias', endpoint='dashboard', view_func=app.view_functions.get('dashboard.dashboard'))
app.add_url_rule('/mypage_alias', endpoint='mypage', view_func=app.view_functions.get('user.mypage'))
app.add_url_rule('/edit_profile_alias', endpoint='edit_profile', view_func=app.view_functions.get('user.edit_profile'), methods=['GET', 'POST'])
app.add_url_rule('/delete_account_alias', endpoint='delete_account', view_func=app.view_functions.get('user.delete_account'), methods=['POST'])
app.add_url_rule('/qna_list_alias', endpoint='qna_list', view_func=app.view_functions.get('qna.qna_list'))
app.add_url_rule('/qna_write_alias', endpoint='qna_write', view_func=app.view_functions.get('qna.qna_write'), methods=['GET', 'POST'])
app.add_url_rule('/qna_detail_alias', endpoint='qna_detail', view_func=app.view_functions.get('qna.qna_detail'))
app.add_url_rule('/qna_delete_alias', endpoint='qna_delete', view_func=app.view_functions.get('qna.qna_delete'), methods=['POST'])
app.add_url_rule('/transactions_alias', endpoint='transactions', view_func=app.view_functions.get('dashboard.transactions'))
app.add_url_rule('/transaction_detail_alias', endpoint='transaction_detail', view_func=app.view_functions.get('dashboard.transaction_detail'))
app.add_url_rule('/create_account_alias', endpoint='create_account', view_func=app.view_functions.get('dashboard.create_account'), methods=['GET', 'POST'])
app.add_url_rule('/deposit_alias', endpoint='deposit', view_func=app.view_functions.get('transfer.deposit'), methods=['GET', 'POST'])
app.add_url_rule('/withdraw_alias', endpoint='withdraw', view_func=app.view_functions.get('transfer.withdraw'), methods=['GET', 'POST'])
app.add_url_rule('/transfer_alias', endpoint='transfer', view_func=app.view_functions.get('transfer.transfer'), methods=['GET', 'POST'])


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
