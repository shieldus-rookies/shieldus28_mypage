from flask import Blueprint, render_template, redirect, request, url_for, session, flash
import random
from utils.db import get_db
from utils.decorators import login_required

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard', endpoint='dashboard')
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


@dashboard_bp.route('/account/create', methods=['GET', 'POST'], endpoint='create_account')
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


@dashboard_bp.route('/transactions', endpoint='transactions')
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


@dashboard_bp.route('/transaction/<int:transaction_id>', endpoint='transaction_detail')
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