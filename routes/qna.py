from flask import Blueprint, render_template, redirect, request, url_for, session, flash
import os
from utils.db import get_db
from utils.decorators import login_required
import config

qna_bp = Blueprint('qna', __name__)


@qna_bp.route('/qna', endpoint='qna_list')
@login_required
def qna_list():
    conn = get_db()
    cursor = conn.cursor()

    # 자신이 작성한 문의만 조회 (정상적인 경우)
    cursor.execute("SELECT * FROM qna WHERE user_id = ? ORDER BY created_at DESC", (session['user_id'],))
    qna_items = cursor.fetchall()
    conn.close()

    return render_template('qna_list.html', qna_items=qna_items)


@qna_bp.route('/qna/write', methods=['GET', 'POST'], endpoint='qna_write')
@login_required
def qna_write():
    if request.method == 'POST':
        title = request.form['title']
        question = request.form['question']

        # 취약점: Stored XSS - 제목/내용 필터링 없음

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO qna (user_id, title, question) VALUES (?, ?, ?)",
            (session['user_id'], title, question)
        )
        qna_id = cursor.lastrowid

        # 파일 업로드 처리
        files = request.files.getlist('files')
        for file in files:
            if file and file.filename:
                # 취약점: File Upload - 확장자 검증 없음, 경로 검증 없음
                filename = file.filename
                filepath = os.path.join(config.QNA_FOLDER, filename)
                file.save(filepath)

                # 파일 정보 저장
                file_size = os.path.getsize(filepath)
                cursor.execute(
                    "INSERT INTO qna_files (qna_id, filename, filepath, file_size) VALUES (?, ?, ?, ?)",
                    (qna_id, filename, filepath, file_size)
                )

        conn.commit()
        conn.close()

        flash('문의가 등록되었습니다.')
        return redirect(url_for('qna_list'))

    return render_template('qna_write.html')


@qna_bp.route('/qna/<int:qna_id>', endpoint='qna_detail')
@login_required
def qna_detail(qna_id):
    conn = get_db()
    cursor = conn.cursor()

    # 취약점: IDOR - 작성자 검증 없이 문의 조회
    cursor.execute("SELECT * FROM qna WHERE id = ?", (qna_id,))
    qna = cursor.fetchone()

    if not qna:
        flash('문의를 찾을 수 없습니다.')
        return redirect(url_for('qna_list'))

    # 첨부파일 조회
    cursor.execute("SELECT * FROM qna_files WHERE qna_id = ?", (qna_id,))
    files = cursor.fetchall()
    conn.close()

    # 취약점: Stored XSS - 제목/내용을 템플릿에서 |safe로 출력
    return render_template('qna_detail.html', qna=qna, files=files)


@qna_bp.route('/qna/<int:qna_id>/delete', methods=['POST'], endpoint='qna_delete')
@login_required
def qna_delete(qna_id):
    # 취약점: IDOR - 작성자 검증 없이 삭제
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM qna WHERE id = ?", (qna_id,))
    conn.commit()
    conn.close()

    flash('문의가 삭제되었습니다.')
    return redirect(url_for('qna_list'))
