# 🏦 Shieldus Bank - 교육용 취약점 포함 은행 웹 애플리케이션

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)

**⚠️ 경고: 이 프로젝트는 보안 취약점 진단을 위한 교육용 프로젝트입니다. 실제 운영 환경에 절대 배포하지 마세요!**

## 📋 프로젝트 개요

Shieldus Bank는 보안 취약점 진단 교육을 위해 의도적으로 취약점을 포함하여 개발된 인터넷 뱅킹 시스템입니다.
SQL Injection, XSS, CSRF, File Upload, IDOR 등 다양한 웹 취약점을 학습하고 진단하는 데 사용할 수 있습니다.

### 🎯 학습 목표

- 실제 금융 시스템에서 발생할 수 있는 보안 취약점 이해
- 취약점 진단 도구 개발 및 테스트
- 안전한 코딩 방법론 학습 (취약점 수정 연습)

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
pip install flask
```

### 2. 데이터베이스 초기화

```bash
python init_db.py
```

### 3. 애플리케이션 실행

```bash
python app.py
```

### 4. 브라우저 접속

```
http://localhost:5000
```

### 🔑 테스트 계정

| 아이디 | 비밀번호 | 설명 |
|--------|----------|------|
| testuser | test1234 | 일반 사용자 (계좌 2개) |
| admin | admin1234 | 관리자 계정 |
| user1 | pass1234 | 일반 사용자 |
| hacker | hack1234 | 공격 테스트용 계정 |

## 🐛 포함된 취약점

### 1. **SQL Injection (SQLi)**
- **위치**: 로그인 (app.py:92), 거래내역 검색 (app.py:202), 회원정보 수정 (app.py:476)
- **취약한 코드 예시**:
  ```python
  query = f"SELECT * FROM users WHERE user_id='{user_id}' AND password='{password}'"
  ```
- **공격 예시**:
  - 로그인 아이디: `admin' OR '1'='1' --`
  - 거래내역 검색: `' UNION SELECT id,user_id,password,name,email,phone,null,null FROM users--`

### 2. **Stored XSS (Cross-Site Scripting)**
- **위치**: 문의게시판 (app.py:542), 송금 메모 (app.py:386)
- **취약한 코드 예시**:
  ```python
  # 템플릿에서 |safe 필터 사용
  {{ qna.title|safe }}
  ```
- **공격 예시**:
  - 문의 제목: `<script>alert('XSS')</script>`
  - 송금 메모: `<img src=x onerror="alert(document.cookie)">`

### 3. **CSRF (Cross-Site Request Forgery)**
- **위치**: 회원정보 수정 (app.py:458), 출금 (app.py:318), 송금 (app.py:374)
- **취약점**: CSRF 토큰 검증 없음

### 4. **File Upload 취약점**
- **위치**: 프로필 이미지 (app.py:464), 문의 첨부파일 (app.py:555)
- **취약점**: 확장자 검증 없음

### 5. **IDOR (Insecure Direct Object Reference)**
- **위치**: 거래내역 조회 (app.py:211), 문의 조회 (app.py:583)

### 6. **파라미터 변조**
- **위치**: 계좌 개설 (app.py:159), 입금 (app.py:262)

## 📚 주요 기능

### 1. 인증 및 회원 관리
- ✅ 회원가입 (평문 비밀번호 저장)
- ✅ 로그인 (SQL Injection)
- ✅ 로그아웃
- ✅ 마이페이지 조회
- ✅ 회원정보 수정 (CSRF, SQLi, File Upload)
- ✅ 회원 탈퇴 (CSRF)

### 2. 계좌 관리
- ✅ 계좌 개설
- ✅ 계좌 목록 조회
- ✅ 계좌 상세 정보

### 3. 금융 거래
- ✅ 입금
- ✅ 출금 (CSRF)
- ✅ 송금 (CSRF, XSS)
- ✅ 거래내역 조회 (SQLi, IDOR)

### 4. 고객센터
- ✅ 문의 작성 (XSS, File Upload)
- ✅ 문의 목록 조회
- ✅ 문의 상세 조회 (IDOR)

## 🧪 취약점 테스트 가이드

### SQL Injection 테스트

#### 로그인 우회
```
아이디: admin' OR '1'='1' --
비밀번호: (아무거나)
```

### XSS 테스트

#### Stored XSS (문의게시판)
```html
제목: <script>alert('XSS')</script>
```

### CSRF 테스트

악성 HTML 파일 생성:
```html
<form action="http://localhost:5000/transfer" method="POST" id="csrf">
    <input name="from_account_id" value="1">
    <input name="to_account_number" value="110-999-999999">
    <input name="amount" value="100000">
</form>
<script>document.getElementById('csrf').submit();</script>
```

## 🛠 나머지 템플릿 작성 방법

현재 **base.html, index.html, login.html, register.html, dashboard.html**이 완성되었습니다.

나머지 템플릿은 dashboard.html의 패턴을 따라 작성하시면 됩니다!

## ⚖️ 법적 고지

**이 프로젝트는 교육 및 학습 목적으로만 사용되어야 합니다.**

### 절대 금지 사항
- ❌ 실제 운영 환경에 배포
- ❌ 실제 사용자 데이터 입력
- ❌ 공용 네트워크에 노출

### 허용된 사용
- ✅ 로컬 개발 환경에서만 실행
- ✅ 교육 및 학습 목적

---

**© 2024 Shieldus Bank - Educational Project Only**
