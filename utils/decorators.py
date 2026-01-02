from flask import session, flash, redirect, url_for

# 로그인 체크 데코레이터
def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요합니다.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper
