from flask import Blueprint, request, jsonify, session, send_from_directory
import sqlite3
import os
from config import Config

mypage_bp = Blueprint('mypage', __name__)

# 마이페이지 조회 (IDOR 취약)
@mypage_bp.route('/', methods=['GET'])
def mypage_get():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인 필요'}), 401
    
    # IDOR 취약점
    target_user_id = request.args.get('user_id', session['user_id'])
    
    conn = sqlite3.connect(Config.DATABASE)
    c = conn.cursor()
    c.execute(f"SELECT * FROM users WHERE id={target_user_id}")
    user = c.fetchone()
    conn.close()
    
    if not user:
        return jsonify({'success': False, 'message': '사용자 없음'}), 404
    
    return jsonify({
        'success': True,
        'user': {
            'id': user[0],
            'username': user[1],
            'email': user[3],
            'profile_pic': user[4],
            'nickname': user[5] if user[5] else user[1],
            'status_message': user[6] if user[6] else ''
        }
    })

# 회원정보 수정 (CSRF, IDOR, XSS 취약)
@mypage_bp.route('/', methods=['PUT', 'POST'])
def mypage_update():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인 필요'}), 401
    
    data = request.get_json() if request.is_json else request.form.to_dict()
    # IDOR 취약점 - 권한 검증 없음
    target_id = data.get('user_id', session['user_id'])
    email = data.get('email', '')
    nickname = data.get('nickname', '')
    status_message = data.get('status_message', '')
    
    conn = sqlite3.connect(Config.DATABASE)
    c = conn.cursor()
    # XSS 취약점 - 입력값 필터링 없음
    c.execute(f"UPDATE users SET email='{email}', nickname='{nickname}', status_message='{status_message}' WHERE id={target_id}")
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': '수정 완료'})

# 프로필 사진 업로드 (File Upload 취약)
@mypage_bp.route('/upload', methods=['POST'])
def profile_upload():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인 필요'}), 401
    
    target_id = request.form.get('user_id', session['user_id'])
    
    if 'profile_pic' not in request.files:
        return jsonify({'success': False, 'message': '파일 없음'}), 400
    
    file = request.files['profile_pic']
    if file.filename:
        # File Upload 취약점 - 확장자 검증 없음
        filepath = os.path.join(Config.UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        conn = sqlite3.connect(Config.DATABASE)
        c = conn.cursor()
        c.execute(f"UPDATE users SET profile_pic='{file.filename}' WHERE id={target_id}")
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'filename': file.filename})
    
    return jsonify({'success': False, 'message': '파일 저장 실패'}), 400

# 회원탈퇴 (CSRF, IDOR 취약)
@mypage_bp.route('/delete', methods=['DELETE', 'POST'])
def delete_account():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인 필요'}), 401
    
    data = request.get_json() if request.is_json else request.form.to_dict()
    # IDOR 취약점
    target_id = data.get('user_id', session['user_id'])
    
    conn = sqlite3.connect(Config.DATABASE)
    c = conn.cursor()
    c.execute(f"DELETE FROM users WHERE id={target_id}")
    conn.commit()
    conn.close()
    
    if str(target_id) == str(session['user_id']):
        session.clear()
    
    return jsonify({'success': True, 'message': '탈퇴 완료'})