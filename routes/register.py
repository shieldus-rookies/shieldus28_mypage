from flask import Blueprint, render_template, redirect, request, url_for, flash
import sqlite3
from utils.db import get_db

register_bp = Blueprint('register', __name__)


@register_bp.route('/register', methods=['GET', 'POST'])
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
