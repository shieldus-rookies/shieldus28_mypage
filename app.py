from flask import Flask, render_template, redirect, request, url_for, session, flash, send_file
import os
import sqlite3
from datetime import datetime
import random
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'vulnerable-secret-key-12345'  # 취약점: 하드코딩된 secret key

# 데이터베이스 파일 경로
DB_PATH = os.path.join(os.path.dirname(__file__), 'vulnerable_app.db')

# 업로드 폴더 설정
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
PROFILE_FOLDER = os.path.join(UPLOAD_FOLDER, 'profiles')
QNA_FOLDER = os.path.join(UPLOAD_FOLDER, 'qna')
RECEIPT_FOLDER = os.path.join(UPLOAD_FOLDER, 'receipts')

# 폴더 생성
for folder in [UPLOAD_FOLDER, PROFILE_FOLDER, QNA_FOLDER, RECEIPT_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# 데이터베이스 연결 헬퍼
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# 로그인 체크 데코레이터
def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요합니다.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


# ==================== 메인 페이지 ====================

@app.route('/')
def index():
    return render_template('index.html')


# ==================== 인증 (로그인/회원가입/로그아웃) ====================

@app.route('/register', methods=['GET', 'POST'])
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


@app.route('/login', methods=['GET', 'POST'])
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


@app.route('/logout')
def logout():
    # 취약점: 세션 관리 미흡 - 세션 쿠키가 완전히 제거되지 않을 수 있음
    session.clear()
    flash('로그아웃되었습니다.')
    return redirect(url_for('index'))


# ==================== 대시보드 ====================

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor()

    # 사용자 계좌 목록 조회
    cursor.execute("SELECT * FROM accounts WHERE user_id = ?", (session['user_id'],))
    accounts = cursor.fetchall()

    # 최근 거래내역 (최근 10건)
    cursor.execute("""
        SELECT t.*, a.account_number, a.account_type
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        WHERE a.user_id = ?
        ORDER BY t.created_at DESC
        LIMIT 10
    """, (session['user_id'],))
    recent_transactions = cursor.fetchall()

    conn.close()

    return render_template('dashboard.html', accounts=accounts, recent_transactions=recent_transactions)


# ==================== 계좌 개설 ====================

@app.route('/account/create', methods=['GET', 'POST'])
@login_required
def create_account():
    if request.method == 'POST':
        account_type = request.form['account_type']
        initial_balance = float(request.form.get('initial_balance', 0))

        # 취약점: 파라미터 변조 - 클라이언트에서 보낸 초기 잔액을 그대로 신뢰
        # 취약점: 입력값 검증 미흡 - 음수 잔액 체크 없음

        # 계좌번호 생성 (랜덤)
        if account_type == 'SAVINGS':
            prefix = '110'
        else:
            prefix = '220'

        account_number = f"{prefix}-{random.randint(100, 999)}-{random.randint(100000, 999999)}"

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO accounts (account_number, user_id, balance, account_type) VALUES (?, ?, ?, ?)",
                (account_number, session['user_id'], initial_balance, account_type)
            )
            conn.commit()
            flash(f'계좌가 개설되었습니다! 계좌번호: {account_number}')
            return redirect(url_for('dashboard'))
        finally:
            conn.close()

    return render_template('create_account.html')


# ==================== 거래내역 조회 ====================

@app.route('/transactions')
@login_required
def transactions():
    conn = get_db()
    cursor = conn.cursor()

    # 검색 기능 (취약점: SQL Injection)
    search = request.args.get('search', '')
    account_id = request.args.get('account_id', '')

    if search:
        # 취약점: SQL Injection - 검색어 직접 결합
        query = f"""
            SELECT t.*, a.account_number
            FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            WHERE a.user_id = {session['user_id']}
            AND (t.description LIKE '%{search}%' OR t.recipient_name LIKE '%{search}%')
            ORDER BY t.created_at DESC
        """
    elif account_id:
        # 취약점: IDOR - account_id 조작 가능
        query = f"""
            SELECT t.*, a.account_number
            FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            WHERE a.id = {account_id}
            ORDER BY t.created_at DESC
        """
    else:
        query = f"""
            SELECT t.*, a.account_number
            FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            WHERE a.user_id = {session['user_id']}
            ORDER BY t.created_at DESC
        """

    cursor.execute(query)
    trans_list = cursor.fetchall()
    conn.close()

    return render_template('transactions.html', transactions=trans_list, search=search)


@app.route('/transaction/<int:transaction_id>')
@login_required
def transaction_detail(transaction_id):
    conn = get_db()
    cursor = conn.cursor()

    # 취약점: IDOR - 소유자 검증 없이 거래내역 조회
    query = f"SELECT t.*, a.account_number FROM transactions t JOIN accounts a ON t.account_id = a.id WHERE t.id = {transaction_id}"
    cursor.execute(query)
    transaction = cursor.fetchone()
    conn.close()

    if not transaction:
        flash('거래내역을 찾을 수 없습니다.')
        return redirect(url_for('transactions'))

    # 취약점: Stored XSS - description을 템플릿에서 |safe로 출력
    return render_template('transaction_detail.html', transaction=transaction)


# ==================== 입금 ====================

@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST':
        account_id = request.form['account_id']
        amount = float(request.form['amount'])
        description = request.form.get('description', '입금')

        # 파일 업로드 처리 (영수증)
        receipt_file = request.files.get('receipt')
        receipt_filename = None

        if receipt_file and receipt_file.filename:
            # 취약점: File Upload - 확장자 검증 없음
            receipt_filename = receipt_file.filename
            receipt_path = os.path.join(RECEIPT_FOLDER, receipt_filename)
            receipt_file.save(receipt_path)

        # 취약점: 파라미터 변조 - 금액을 클라이언트에서 받아서 그대로 신뢰
        # 취약점: IDOR - account_id 조작으로 타인 계좌에 입금 가능

        conn = get_db()
        cursor = conn.cursor()

        # 현재 잔액 조회
        cursor.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
        account = cursor.fetchone()

        if not account:
            flash('계좌를 찾을 수 없습니다.')
            return redirect(url_for('deposit'))

        new_balance = account['balance'] + amount

        # 잔액 업데이트
        cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_balance, account_id))

        # 거래내역 저장
        cursor.execute(
            "INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description, receipt_image) VALUES (?, ?, ?, ?, ?, ?)",
            (account_id, 'DEPOSIT', amount, new_balance, description, receipt_filename)
        )

        conn.commit()
        conn.close()

        flash(f'{amount:,.0f}원이 입금되었습니다.')
        return redirect(url_for('dashboard'))

    # GET 요청: 사용자 계좌 목록 조회
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts WHERE user_id = ?", (session['user_id'],))
    accounts = cursor.fetchall()
    conn.close()

    return render_template('deposit.html', accounts=accounts)


# ==================== 출금 ====================

@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    if request.method == 'POST':
        account_id = request.form['account_id']
        amount = float(request.form['amount'])
        description = request.form.get('description', 'ATM 출금')

        # 취약점: CSRF - CSRF 토큰 검증 없음
        # 취약점: 서버 검증 미흡 - 잔액 부족 검증이 약함

        conn = get_db()
        cursor = conn.cursor()

        # 현재 잔액 조회
        cursor.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
        account = cursor.fetchone()

        if not account:
            flash('계좌를 찾을 수 없습니다.')
            return redirect(url_for('withdraw'))

        # 취약점: Race Condition - 동시 요청 처리 미흡 (간단한 잔액 체크만 함)
        if account['balance'] < amount:
            flash('잔액이 부족합니다.')
            return redirect(url_for('withdraw'))

        new_balance = account['balance'] - amount

        # 잔액 업데이트
        cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_balance, account_id))

        # 거래내역 저장
        cursor.execute(
            "INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description) VALUES (?, ?, ?, ?, ?)",
            (account_id, 'WITHDRAW', -amount, new_balance, description)
        )

        conn.commit()
        conn.close()

        flash(f'{amount:,.0f}원이 출금되었습니다.')
        return redirect(url_for('dashboard'))

    # GET 요청
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts WHERE user_id = ?", (session['user_id'],))
    accounts = cursor.fetchall()
    conn.close()

    return render_template('withdraw.html', accounts=accounts)


# ==================== 송금 ====================

@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    if request.method == 'POST':
        from_account_id = request.form['from_account_id']
        to_account_number = request.form['to_account_number']
        amount = float(request.form['amount'])
        recipient_name = request.form.get('recipient_name', '')
        memo = request.form.get('memo', '송금')

        # 취약점: CSRF - CSRF 토큰 검증 없음
        # 취약점: 파라미터 변조 - 금액/수취인 서버 검증 미흡
        # 취약점: Stored XSS - memo를 필터링 없이 저장

        conn = get_db()
        cursor = conn.cursor()

        # 출금 계좌 조회
        cursor.execute("SELECT * FROM accounts WHERE id = ?", (from_account_id,))
        from_account = cursor.fetchone()

        # 입금 계좌 조회
        cursor.execute("SELECT * FROM accounts WHERE account_number = ?", (to_account_number,))
        to_account = cursor.fetchone()

        if not from_account or not to_account:
            flash('계좌를 찾을 수 없습니다.')
            conn.close()
            return redirect(url_for('transfer'))

        if from_account['balance'] < amount:
            flash('잔액이 부족합니다.')
            conn.close()
            return redirect(url_for('transfer'))

        # 출금 처리
        new_from_balance = from_account['balance'] - amount
        cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_from_balance, from_account['id']))
        cursor.execute(
            "INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description, recipient_account, recipient_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (from_account['id'], 'TRANSFER', -amount, new_from_balance, memo, to_account_number, recipient_name)
        )

        # 입금 처리
        new_to_balance = to_account['balance'] + amount
        cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_to_balance, to_account['id']))
        cursor.execute(
            "INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description, recipient_account, recipient_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (to_account['id'], 'TRANSFER', amount, new_to_balance, f'{from_account["account_number"]}에서 받음', from_account['account_number'], session['username'])
        )

        conn.commit()
        conn.close()

        flash(f'{recipient_name}님에게 {amount:,.0f}원을 송금했습니다.')
        return redirect(url_for('dashboard'))

    # GET 요청
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts WHERE user_id = ?", (session['user_id'],))
    accounts = cursor.fetchall()
    conn.close()

    return render_template('transfer.html', accounts=accounts)


# ==================== 마이페이지 ====================

@app.route('/mypage')
@login_required
def mypage():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    conn.close()

    return render_template('mypage.html', user=user)


@app.route('/mypage/edit', methods=['GET', 'POST'])
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
            profile_path = os.path.join(PROFILE_FOLDER, profile_filename)
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


@app.route('/mypage/delete', methods=['POST'])
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


# ==================== 문의게시판 ====================

@app.route('/qna')
@login_required
def qna_list():
    conn = get_db()
    cursor = conn.cursor()

    # 자신이 작성한 문의만 조회 (정상적인 경우)
    cursor.execute("SELECT * FROM qna WHERE user_id = ? ORDER BY created_at DESC", (session['user_id'],))
    qna_items = cursor.fetchall()
    conn.close()

    return render_template('qna_list.html', qna_items=qna_items)


@app.route('/qna/write', methods=['GET', 'POST'])
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
                filepath = os.path.join(QNA_FOLDER, filename)
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


@app.route('/qna/<int:qna_id>')
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


@app.route('/qna/<int:qna_id>/delete', methods=['POST'])
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


# ==================== 에러 핸들러 ====================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
