# routes/register.py
from flask import Blueprint, render_template, redirect, request, url_for, flash
import sqlite3
from utils.db import get_db
import pymysql # 추가

register_bp = Blueprint('register', __name__)


@register_bp.route('/register', methods=['GET', 'POST'], endpoint='register')
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        nickname = request.form['nickname']
        email = request.form.get('email', '')
        # phone = request.form.get('phone', '')
        # birthdate = request.form.get('birthdate', '')

        if password != password_confirm:
            flash('비밀번호가 일치하지 않습니다.')
            return redirect(url_for('register'))

        # 취약점: 평문 비밀번호 저장
        conn = get_db()
        cursor = conn.cursor()
        try:
            # cursor.execute(
            #     "INSERT INTO users (username, password, nickname, email) VALUES (?, ?, ?, ?)",
            #     (username, password, nickname, email)
            # )
            query = f"INSERT INTO users (username, password, nickname, email) VALUES ('{username}', '{password}', '{nickname}', '{email}')"
            cursor.execute(query)
            conn.commit()
            flash('회원가입이 완료되었습니다. 로그인해주세요.')
            return redirect(url_for('login'))
        except pymysql.err.IntegrityError as e: # sqlite3.IntegrityError:
            if e.args[0] == 1062:
                flash('이미 존재하는 아이디입니다.')
                return redirect(url_for('register'))
            else :
                flash('데이터베이스 오류가 발생했습니다.')
                return render_template('register.html')
        finally:
            conn.close()

    return render_template('register.html')
