from flask import Blueprint, render_template, redirect, request, url_for, session, flash
import os
from utils.db import get_db
from utils.decorators import login_required
import config

user_bp = Blueprint('user', __name__)


@user_bp.route('/mypage')
@login_required
def mypage():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    conn.close()

    return render_template('mypage.html', user=user)


@user_bp.route('/mypage/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        # 프로필 이미지 업로드
        profile_image = request.files.get('profile_image')
        profile_filename = None

        if profile_image and profile_image.filename:
            # 취약점: File Upload - 확장자/Content-Type 검증 없음
            profile_filename = profile_image.filename
            profile_path = os.path.join(config.PROFILE_FOLDER, profile_filename)
            profile_image.save(profile_path)

        # 취약점: CSRF - CSRF 토큰 검증 없음
        # 취약점: SQL Injection - 이름/이메일 필드를 통한 SQLi
        if profile_filename:
            query = f"UPDATE users SET name='{name}', email='{email}', phone='{phone}', profile_image='{profile_filename}' WHERE id={session['user_id']}"
        else:
            query = f"UPDATE users SET name='{name}', email='{email}', phone='{phone}' WHERE id={session['user_id']}"

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()

        # 세션 정보 업데이트
        session['username'] = name

        flash('회원정보가 수정되었습니다.')
        return redirect(url_for('mypage'))

    # GET 요청
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    conn.close()

    return render_template('edit_profile.html', user=user)


@user_bp.route('/mypage/delete', methods=['POST'])
@login_required
def delete_account():
    # 취약점: CSRF - CSRF 토큰 검증 없음
    user_id = session['user_id']

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    session.clear()
    flash('회원 탈퇴가 완료되었습니다.')
    return redirect(url_for('index'))
