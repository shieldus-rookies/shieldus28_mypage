from flask import Blueprint, render_template, redirect, request, url_for, session, flash
import sqlite3
from utils.db import get_db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        name = request.form['name']
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        birthdate = request.form.get('birthdate', '')

        if password != password_confirm:
            flash('비밀번호가 일치하지 않습니다.')
            return redirect(url_for('register'))

        # 취약점: 평문 비밀번호 저장
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (user_id, password, name, email, phone, birthdate) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, password, name, email, phone, birthdate)
            )
            conn.commit()
            flash('회원가입이 완료되었습니다. 로그인해주세요.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('이미 존재하는 아이디입니다.')
            return redirect(url_for('register'))
        finally:
            conn.close()

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
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


@auth_bp.route('/logout')
def logout():
    # 취약점: 세션 관리 미흡 - 세션 쿠키가 완전히 제거되지 않을 수 있음
    session.clear()
    flash('로그아웃되었습니다.')
    return redirect(url_for('index'))
