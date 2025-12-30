from flask import Blueprint, request, jsonify, session
import sqlite3
from datetime import datetime
from config import Config

auth_bp = Blueprint('auth', __name__)

# 회원가입
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    email = data.get('email', '')
    
    conn = sqlite3.connect(Config.DATABASE)
    c = conn.cursor()
    # SQL Injection 취약점
    query = f"INSERT INTO users (username, password, email) VALUES ('{username}', '{password}', '{email}')"
    try:
        c.execute(query)
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': '회원가입 성공'})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 400

# 로그인
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    conn = sqlite3.connect(Config.DATABASE)
    c = conn.cursor()
    # SQL Injection 취약점
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    c.execute(query)
    user = c.fetchone()
    conn.close()
    
    if user:
        # 세션 관리 미흡
        session['user_id'] = user[0]
        session['username'] = user[1]
        session['login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'success': True,
            'user': {
                'id': user[0],
                'username': user[1],
                'email': user[3]
            }
        })
    
    return jsonify({'success': False, 'message': '로그인 실패'}), 401

# 로그아웃
@auth_bp.route('/logout', methods=['POST'])
def logout():
    # 불완전한 로그아웃 (쿠키 미제거)
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('login_time', None)
    return jsonify({'success': True, 'message': '로그아웃 성공'})

# 현재 사용자 정보
@auth_bp.route('/user', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인 필요'}), 401
    
    return jsonify({
        'success': True,
        'user': {
            'id': session['user_id'],
            'username': session['username']
        }
    })