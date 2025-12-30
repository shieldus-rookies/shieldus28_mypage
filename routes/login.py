from flask import Blueprint, render_template, redirect, request, url_for, session, flash
from utils.db import get_db

login_bp = Blueprint('login', __name__)


@login_bp.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']

        # 취약점: SQL Injection - 문자열 직접 결합
        query = f"SELECT * FROM users WHERE user_id='{user_id}' AND password='{password}'"

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            user = cursor.fetchone()

            if user:
                # 세션에 사용자 정보 저장
                session['user_id'] = user['id']
                session['username'] = user['name']
                session['login_id'] = user['user_id']
                flash(f'{user["name"]}님, 환영합니다!')
                return redirect(url_for('dashboard'))
            else:
                flash('아이디 또는 비밀번호가 잘못되었습니다.')
                return redirect(url_for('login'))
        finally:
            conn.close()

    return render_template('login.html')


@login_bp.route('/logout', endpoint='logout')
def logout():
    # 취약점: 세션 관리 미흡 - 세션 쿠키가 완전히 제거되지 않을 수 있음
    session.clear()
    flash('로그아웃되었습니다.')
    return redirect(url_for('index'))
