-- Shieldus Bank Database Schema
-- 교육용 취약점 포함 은행 시스템

-- 1. 사용자 테이블
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,           -- 로그인 ID
    password TEXT NOT NULL,                  -- 평문 비밀번호 (취약점)
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    birthdate TEXT,
    profile_image TEXT,                      -- 프로필 사진 경로 (File Upload 취약점)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 계좌 테이블
DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_number TEXT UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    balance REAL DEFAULT 0,
    account_type TEXT DEFAULT 'SAVINGS',    -- SAVINGS, CHECKING
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. 거래내역 테이블
DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,         -- DEPOSIT(입금), WITHDRAW(출금), TRANSFER(송금)
    amount REAL NOT NULL,
    balance_after REAL,
    description TEXT,                       -- 거래 메모 (XSS 취약점)
    recipient_account TEXT,                 -- 수취인 계좌번호
    recipient_name TEXT,
    receipt_image TEXT,                     -- 영수증 이미지 (File Upload 취약점)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

-- 4. 문의게시판 테이블
DROP TABLE IF EXISTS qna;
CREATE TABLE qna (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,                    -- 제목 (XSS 취약점)
    question TEXT NOT NULL,                 -- 문의 내용 (XSS 취약점)
    answer TEXT,                            -- 관리자 답변
    status TEXT DEFAULT 'PENDING',          -- PENDING, ANSWERED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    answered_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 5. 문의 첨부파일 테이블
DROP TABLE IF EXISTS qna_files;
CREATE TABLE qna_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    qna_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,                 -- 파일 경로 (File Upload 취약점)
    file_size INTEGER,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (qna_id) REFERENCES qna(id) ON DELETE CASCADE
);

-- 테스트 데이터 삽입

-- 사용자 데이터 (평문 비밀번호)
INSERT INTO users (user_id, password, name, email, phone, birthdate) VALUES
('testuser', 'test1234', '김테스트', 'test@example.com', '010-1234-5678', '1990-01-01'),
('admin', 'admin1234', '관리자', 'admin@shieldusbank.com', '010-9999-9999', '1985-05-15'),
('user1', 'pass1234', '박사용자', 'user1@example.com', '010-1111-2222', '1995-03-20'),
('hacker', 'hack1234', '해커', 'hacker@evil.com', '010-0000-0000', '2000-12-31');

-- 계좌 데이터
INSERT INTO accounts (account_number, user_id, balance, account_type) VALUES
('110-123-456789', 1, 1000000.00, 'SAVINGS'),
('220-987-654321', 1, 500000.00, 'CHECKING'),
('110-111-111111', 2, 5000000.00, 'SAVINGS'),
('110-222-222222', 3, 750000.00, 'SAVINGS'),
('220-333-333333', 3, 250000.00, 'CHECKING'),
('110-999-999999', 4, 100.00, 'SAVINGS');

-- 거래내역 데이터
INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description, recipient_account, recipient_name, created_at) VALUES
(1, 'DEPOSIT', 500000.00, 500000.00, '초기 입금', NULL, NULL, '2024-01-01 09:00:00'),
(1, 'DEPOSIT', 300000.00, 800000.00, '급여 입금', NULL, NULL, '2024-01-15 10:30:00'),
(1, 'TRANSFER', -50000.00, 750000.00, '생활비 송금', '110-222-222222', '박사용자', '2024-01-20 14:20:00'),
(1, 'WITHDRAW', -100000.00, 650000.00, 'ATM 출금', NULL, NULL, '2024-01-25 16:45:00'),
(1, 'DEPOSIT', 200000.00, 850000.00, '보너스 입금', NULL, NULL, '2024-02-01 11:00:00'),
(1, 'TRANSFER', -30000.00, 820000.00, '유틸리티 요금', '220-987-654321', '전기요금', '2024-02-05 09:15:00'),
(1, 'DEPOSIT', 180000.00, 1000000.00, '이자 입금', NULL, NULL, '2024-02-10 00:00:00'),
(2, 'DEPOSIT', 500000.00, 500000.00, '초기 입금', NULL, NULL, '2024-01-01 09:00:00'),
(3, 'DEPOSIT', 5000000.00, 5000000.00, '초기 입금', NULL, NULL, '2024-01-01 09:00:00'),
(4, 'DEPOSIT', 750000.00, 750000.00, '초기 입금', NULL, NULL, '2024-01-01 09:00:00'),
(4, 'TRANSFER', 50000.00, 800000.00, '생활비 수령', '110-123-456789', '김테스트', '2024-01-20 14:20:00');

-- 문의게시판 데이터
INSERT INTO qna (user_id, title, question, status, created_at) VALUES
(1, '계좌 개설 문의', '새로운 계좌를 개설하고 싶습니다. 필요한 서류가 무엇인가요?', 'ANSWERED', '2024-01-10 10:00:00'),
(3, '송금 한도 문의', '일일 송금 한도를 늘리고 싶습니다.', 'PENDING', '2024-02-01 14:30:00'),
(1, '카드 발급 문의', '체크카드 발급이 가능한가요?', 'PENDING', '2024-02-05 16:20:00');

-- 문의게시판 답변
UPDATE qna SET answer = '신분증과 주소지 확인 서류를 준비해주시면 됩니다. 영업점 방문 또는 온라인으로 신청 가능합니다.',
              answered_at = '2024-01-10 15:00:00'
WHERE id = 1;
