from flask import Blueprint, render_template, redirect, request, url_for, session, flash, abort
import random
from utils.db import get_db
from utils.decorators import login_required

dashboard_bp = Blueprint('dashboard', __name__)


def get_user_id():
    # 수정: session user_id를 정수로 강제 변환
    try:
        return int(session['user_id'])
    except (KeyError, ValueError):
        abort(401)


@dashboard_bp.route('/dashboard', endpoint='dashboard')
@login_required
def dashboard():
    user_id = get_user_id()

    conn = get_db()
    cursor = conn.cursor()

    # 변경: SELECT * 제거, 스키마 의존 컬럼만 명시
    cursor.execute(
        """
        SELECT
            id,
            account_number,
            balance,
            account_type
        FROM accounts
        WHERE user_id = ?
        """,
        (user_id,)
    )
    accounts = cursor.fetchall()

    # 변경: t.* 제거, 필요한 컬럼만 조회
    cursor.execute(
        """
        SELECT
            t.id,
            t.account_id,
            t.amount,
            t.description,
            t.recipient_name,
            t.created_at,
            a.account_number,
            a.account_type
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        WHERE a.user_id = ?
        ORDER BY t.created_at DESC
        LIMIT 10
        """,
        (user_id,)
    )
    recent_transactions = cursor.fetchall()

    conn.close()

    return render_template(
        'dashboard.html',
        accounts=accounts,
        recent_transactions=recent_transactions
    )


@dashboard_bp.route('/account/create', methods=['GET', 'POST'], endpoint='create_account')
@login_required
def create_account():
    user_id = get_user_id()

    if request.method == 'POST':
        # 주의: form name 변경 없음 (HTML 수정 불필요)
        account_type = request.form['account_type']
        initial_balance = request.form.get('initial_balance', 0)

        # 취약점: 파라미터 변조 가능
        # 수정: 서버에서 숫자 변환 및 검증
        try:
            initial_balance = float(initial_balance)
        except ValueError:
            flash('초기 잔액이 올바르지 않습니다.')
            return redirect(url_for('dashboard.create_account'))

        if initial_balance < 0:
            flash('초기 잔액은 0 이상이어야 합니다.')
            return redirect(url_for('dashboard.create_account'))

        if account_type == 'SAVINGS':
            prefix = '110'
        else:
            prefix = '220'

        account_number = f"{prefix}-{random.randint(100, 999)}-{random.randint(100000, 999999)}"

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO accounts (account_number, user_id, balance, account_type)
                VALUES (?, ?, ?, ?)
                """,
                (account_number, user_id, initial_balance, account_type)
            )
            conn.commit()
            flash(f'계좌가 개설되었습니다! 계좌번호: {account_number}')
            return redirect(url_for('dashboard.dashboard'))
        finally:
            conn.close()

    return render_template('create_account.html')


@dashboard_bp.route('/transactions', endpoint='transactions')
@login_required
def transactions():
    user_id = get_user_id()

    search = request.args.get('search', '')
    account_id = request.args.get('account_id', '')

    conn = get_db()
    cursor = conn.cursor()

    # 기본 쿼리
    query = """
        SELECT
            t.id,
            t.account_id,
            t.amount,
            t.description,
            t.recipient_name,
            t.created_at,
            a.account_number
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        WHERE a.user_id = ?
    """
    params = [user_id]

    if account_id:
        # 취약점: IDOR
        # 수정: account_id 사용 시에도 user_id 조건 유지
        try:
            account_id = int(account_id)
            query += " AND a.id = ? "
            params.append(account_id)
        except ValueError:
            flash('계좌 선택이 올바르지 않습니다.')
            return redirect(url_for('dashboard.transactions'))

    if search:
        # 취약점: SQL Injection
        # 수정: LIKE 검색도 바인딩 사용
        query += " AND (t.description LIKE ? OR t.recipient_name LIKE ?) "
        like = f"%{search}%"
        params.extend([like, like])

    query += " ORDER BY t.created_at DESC "

    cursor.execute(query, tuple(params))
    trans_list = cursor.fetchall()
    conn.close()

    return render_template(
        'transactions.html',
        transactions=trans_list,
        search=search
    )


@dashboard_bp.route('/transaction/<int:transaction_id>', endpoint='transaction_detail')
@login_required
def transaction_detail(transaction_id):
    user_id = get_user_id()

    conn = get_db()
    cursor = conn.cursor()

    # 취약점: IDOR
    # 수정: 단건 조회에도 소유자 검증 추가
    cursor.execute(
        """
        SELECT
            t.id,
            t.account_id,
            t.amount,
            t.description,
            t.recipient_name,
            t.created_at,
            a.account_number
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        WHERE t.id = ?
          AND a.user_id = ?
        """,
        (transaction_id, user_id)
    )
    transaction = cursor.fetchone()
    conn.close()

    if not transaction:
        flash('거래내역을 찾을 수 없습니다.')
        return redirect(url_for('dashboard.transactions'))

    # 주의: 템플릿에서 description | safe 사용 금지 (Stored XSS)
    return render_template('transaction_detail.html', transaction=transaction)
