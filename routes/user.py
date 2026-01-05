from flask import Blueprint, render_template, redirect, request, url_for, session, flash
import os
from utils.db import get_db
from utils.decorators import login_required
import config

user_bp = Blueprint('user', __name__)


@user_bp.route('/mypage', endpoint='mypage')
@login_required
def mypage():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {session['user_id']}")
    user = cursor.fetchone()
    conn.close()

    return render_template('mypage.html', user=user)


@user_bp.route('/mypage/edit', methods=['GET', 'POST'], endpoint='edit_profile')
@login_required
def edit_profile():
    if request.method == 'POST':
        nickname = request.form['nickname']
        email = request.form['email']

        # 취약점: CSRF - CSRF 토큰 검증 없음
        # 취약점: SQL Injection - 이름/이메일 필드를 통한 SQLi
        query = f"UPDATE users SET nickname='{nickname}', email='{email}' WHERE id={session['user_id']}"

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()

        # 세션 정보 업데이트
        session['username'] = nickname

        flash('회원정보가 수정되었습니다.')
        return redirect(url_for('mypage'))

    # GET 요청
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {session['user_id']}")
    user = cursor.fetchone()
    conn.close()

    return render_template('edit_profile.html', user=user)


@user_bp.route('/mypage/delete', methods=['POST'], endpoint='delete_account')
@login_required
def delete_account():
    # 취약점: CSRF - CSRF 토큰 검증 없음
    user_id = session['user_id']

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM users WHERE id = {user_id}")
    conn.commit()
    conn.close()

    session.clear()
    flash('회원 탈퇴가 완료되었습니다.')
    return redirect(url_for('index'))
