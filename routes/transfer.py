from flask import Blueprint, render_template, redirect, request, url_for, session, flash
import os
from utils.db import get_db
from utils.decorators import login_required
import config

transfer_bp = Blueprint('transfer', __name__)


@transfer_bp.route('/deposit', methods=['GET', 'POST'], endpoint='deposit')
@login_required
def deposit():
    if request.method == 'POST':
        account_id = request.form['account_id']
        amount = float(request.form['amount'])
        description = request.form.get('description', '입금')

        # # 파일 업로드 처리 (영수증)?
        # receipt_file = request.files.get('receipt')
        # receipt_filename = None

        # if receipt_file and receipt_file.filename:
        #     # 취약점: File Upload - 확장자 검증 없음
        #     receipt_filename = receipt_file.filename
        #     receipt_path = os.path.join(config.RECEIPT_FOLDER, receipt_filename)
        #     receipt_file.save(receipt_path)

        # 취약점: 파라미터 변조 - 금액을 클라이언트에서 받아서 그대로 신뢰
        # 취약점: IDOR - account_id 조작으로 타인 계좌에 입금 가능

        conn = get_db()
        cursor = conn.cursor()

        # 현재 잔액 조회
        # cursor.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
        # account = cursor.fetchone()
        query = f"SELECT account_number, balance FROM accounts WHERE id = {account_id}"
        cursor.execute(query)
        account = cursor.fetchone()

        if not account:
            flash('계좌를 찾을 수 없습니다.')
            return redirect(url_for('deposit'))

        new_balance = account['balance'] + amount
        account_number = account['account_number']

        # 잔액 업데이트
        # cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_balance, account_id))
        query = f"UPDATE accounts SET balance = {new_balance} WHERE id = {account_id}"
        cursor.execute(query)

        # 거래내역 저장
        # cursor.execute(
        #     "INSERT INTO transactions (accounts_id, transaction_type, amount, balance_after, description, receipt_image) VALUES (?, ?, ?, ?, ?, ?)",
        #     (account_id, 'DEPOSIT', amount, new_balance, description, receipt_filename)
        # )

        query = f"INSERT INTO transactions (accounts_id, from_acc, to_acc, amount, balance_after, description) VALUES ({account_id}, '0', '{account_number}', {amount}, {new_balance}, '{description}')"
        cursor.execute(query)

        conn.commit()
        conn.close()

        flash(f'{amount:,.0f}원이 입금되었습니다.')
        return redirect(url_for('dashboard'))

    # GET 요청: 사용자 계좌 목록 조회
    conn = get_db()
    cursor = conn.cursor()
    # users_id? user_id?
    query = f"SELECT * FROM accounts WHERE users_id = {session['user_id']}"
    cursor.execute(query)
    accounts = cursor.fetchall()
    conn.close()

    return render_template('deposit.html', accounts=accounts)


@transfer_bp.route('/withdraw', methods=['GET', 'POST'], endpoint='withdraw')
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
        # cursor.execute("SELECT account_number, balance FROM accounts WHERE id = ?", (account_id,))
        # account = cursor.fetchone()
        query = f"SELECT account_number, balance FROM accounts WHERE id = {account_id}"
        cursor.execute(query)
        account = cursor.fetchone()

        if not account:
            flash('계좌를 찾을 수 없습니다.')
            return redirect(url_for('withdraw'))

        # 취약점: Race Condition - 동시 요청 처리 미흡 (간단한 잔액 체크만 함)
        if account['balance'] < amount:
            flash('잔액이 부족합니다.')
            return redirect(url_for('withdraw'))

        new_balance = account['balance'] - amount
        account_number = account['account_number']

        # 잔액 업데이트
        # cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_balance, account_id))
        query = f"UPDATE accounts SET balance = {new_balance} WHERE id = {account_id}"
        cursor.execute(query)

        # 거래내역 저장
        # cursor.execute(
        #     "INSERT INTO transactions (account_id, from_acc, to_acc, amount, balance_after, description) VALUES (?, ?, ?, ?, ?)",
        #     (account_id, account_number, '0', -amount, new_balance, description)
        # )
        query = f"INSERT INTO transactions (accounts_id, from_acc, to_acc, amount, balance_after, description) VALUES ({account_id}, '{account_number}', '0', -{amount}, {new_balance}, '{description}')"
        cursor.execute(query)

        conn.commit()
        conn.close()

        flash(f'{amount:,.0f}원이 출금되었습니다.')
        return redirect(url_for('dashboard'))

    # GET 요청
    conn = get_db()
    cursor = conn.cursor()
    # cursor.execute("SELECT * FROM accounts WHERE user_id = ?", (session['user_id'],))
    # accounts = cursor.fetchall()
    query = f"SELECT * FROM accounts WHERE users_id = {session['user_id']}"
    cursor.execute(query)
    accounts = cursor.fetchall()
    conn.close()

    return render_template('withdraw.html', accounts=accounts)


@transfer_bp.route('/transfer', methods=['GET', 'POST'], endpoint='transfer')
@login_required
def transfer():
    if request.method == 'POST':
        from_account_id = request.form['from_account_id']
        to_account_number = request.form['to_account_number']
        amount = float(request.form['amount'])
        recipient_name = request.form.get('recipient_name', '')
        description = request.form.get('description', '송금')

        # 취약점: CSRF - CSRF 토큰 검증 없음
        # 취약점: 파라미터 변조 - 금액/수취인 서버 검증 미흡
        # 취약점: Stored XSS - description을 필터링 없이 저장
        conn = get_db()
        cursor = conn.cursor()

        # 출금 계좌 조회
        # cursor.execute("SELECT * FROM accounts WHERE id = ?", (from_account_id,))
        # from_account = cursor.fetchone()
        query = f"SELECT * FROM accounts WHERE id = {from_account_id}"
        cursor.execute(query)
        from_account = cursor.fetchone()

        # 입금 계좌 조회
        # cursor.execute("SELECT * FROM accounts WHERE account_number = ?", (to_account_number,))
        # to_account = cursor.fetchone()
        query = f"SELECT * FROM accounts WHERE account_number = '{to_account_number}'"
        cursor.execute(query)
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
        # cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_from_balance, from_account['id']))
        query = f"UPDATE accounts SET balance = {new_from_balance} WHERE id = {from_account['id']}"
        cursor.execute(query)
        # cursor.execute(
        #     "INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description, recipient_account, recipient_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
        #     (from_account['id'], 'TRANSFER', -amount, new_from_balance, memo, to_account_number, recipient_name)
        # )
        query = f"INSERT INTO transactions (accounts_id, from_acc, to_acc, amount, balance_after, description) VALUES ({from_account['id']}, '{from_account['account_number']}', '{to_account['account_number']}', -{amount}, {new_from_balance}, '{description}')"
        cursor.execute(query)

        # 입금 처리
        new_to_balance = to_account['balance'] + amount
        # cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_to_balance, to_account['id']))
        query = f"UPDATE accounts SET balance = {new_to_balance} WHERE id = {to_account['id']}"
        cursor.execute(query)
        # cursor.execute(
        #     "INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description, recipient_account, recipient_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
        #     (to_account['id'], 'TRANSFER', amount, new_to_balance, f'{from_account["account_number"]}에서 받음', from_account['account_number'], session['username'])
        # )
        query = f"INSERT INTO transactions (accounts_id, from_acc, to_acc, amount, balance_after, description) VALUES ({to_account['id']}, '{from_account['account_number']}', '{to_account['account_number']}', {amount}, {new_to_balance}, '{from_account['account_number']}에서 받음')"
        cursor.execute(query)

        conn.commit()
        conn.close()

        flash(f'{to_account_number}로 {amount:,.0f}원을 송금했습니다.')
        return redirect(url_for('dashboard'))

    # GET 요청
    conn = get_db()
    cursor = conn.cursor()
    # cursor.execute("SELECT * FROM accounts WHERE user_id = ?", (session['user_id'],))
    query = f"SELECT * FROM accounts WHERE users_id = {session['user_id']}"
    cursor.execute(query)
    accounts = cursor.fetchall()
    conn.close()

    return render_template('transfer.html', accounts=accounts)
