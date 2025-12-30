from flask import Blueprint, request, jsonify, session
import sqlite3
import os
from config import Config

inquiry_bp = Blueprint('inquiry', __name__)

# 문의글 목록 조회
@inquiry_bp.route('/', methods=['GET'])
def inquiry_list():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인 필요'}), 401
    
    conn = sqlite3.connect(Config.DATABASE)
    c = conn.cursor()
    c.execute("SELECT inquiries.*, users.username FROM inquiries LEFT JOIN users ON inquiries.user_id = users.id ORDER BY inquiries.id DESC")
    inquiries = c.fetchall()
    conn.close()
    
    result = []
    for inq in inquiries:
        result.append({
            'id': inq[0],
            'user_id': inq[1],
            'title': inq[2],
            'content': inq[3],
            'attachment': inq[4],
            'username': inq[5] if len(inq) > 5 else '알 수 없음',
            'is_mine': inq[1] == session['user_id']
        })
    
    return jsonify({'success': True, 'inquiries': result})

# 문의글 작성 (SQL Injection, XSS, File Upload 취약)
@inquiry_bp.route('/', methods=['POST'])
def inquiry_create():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인 필요'}), 401
    
    title = request.form.get('title', '')
    content = request.form.get('content', '')
    attached_file = ''
    
    # File Upload 취약점
    if 'attachment' in request.files:
        file = request.files['attachment']
        if file.filename:
            filepath = os.path.join(Config.UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            attached_file = file.filename
    
    conn = sqlite3.connect(Config.DATABASE)
    c = conn.cursor()
    # SQL Injection, Stored XSS 취약점
    query = f"INSERT INTO inquiries (user_id, title, content, attachment) VALUES ({session['user_id']}, '{title}', '{content}', '{attached_file}')"
    c.execute(query)
    conn.commit()
    inquiry_id = c.lastrowid
    conn.close()
    
    return jsonify({'success': True, 'inquiry_id': inquiry_id, 'message': '등록 완료'})

# 문의글 상세 조회 (IDOR 취약)
@inquiry_bp.route('/<int:inquiry_id>', methods=['GET'])
def inquiry_view(inquiry_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인 필요'}), 401
    
    conn = sqlite3.connect(Config.DATABASE)
    c = conn.cursor()
    # IDOR 취약점 - 권한 검증 없음
    c.execute(f"SELECT inquiries.*, users.username FROM inquiries LEFT JOIN users ON inquiries.user_id = users.id WHERE inquiries.id={inquiry_id}")
    inquiry = c.fetchone()
    conn.close()
    
    if not inquiry:
        return jsonify({'success': False, 'message': '문의글 없음'}), 404
    
    return jsonify({
        'success': True,
        'inquiry': {
            'id': inquiry[0],
            'user_id': inquiry[1],
            'title': inquiry[2],
            'content': inquiry[3],
            'attachment': inquiry[4],
            'username': inquiry[5] if len(inquiry) > 5 else '알 수 없음',
            'is_mine': inquiry[1] == session['user_id']
        }
    })

# 문의글 삭제 (IDOR 취약)
@inquiry_bp.route('/<int:inquiry_id>', methods=['DELETE'])
def inquiry_delete(inquiry_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인 필요'}), 401
    
    conn = sqlite3.connect(Config.DATABASE)
    c = conn.cursor()
    
    # 첨부파일 삭제
    c.execute(f"SELECT attachment FROM inquiries WHERE id={inquiry_id}")
    result = c.fetchone()
    if result and result[0]:
        try:
            os.remove(os.path.join(Config.UPLOAD_FOLDER, result[0]))
        except:
            pass
    
    # IDOR 취약점 - 권한 검증 없음
    c.execute(f"DELETE FROM inquiries WHERE id={inquiry_id}")
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': '삭제 완료'})