-- CREATE DATABASE IF NOT EXISTS mydb
--   CHARACTER SET utf8
--   COLLATE utf8_general_ci;

-- USE mydb;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  email TEXT,
  nickname TEXT,
  role TEXT DEFAULT 'user',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS accounts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  account_number TEXT NOT NULL UNIQUE,
  balance NUMERIC DEFAULT 0,
  account_type TEXT DEFAULT 'SAVINGS',
  users_id INTEGER NOT NULL,
  FOREIGN KEY (users_id)
    REFERENCES users (id)
    ON DELETE CASCADE
    ON UPDATE NO ACTION
);

-- MySQL의 INDEX는 SQLite에서 보통 별도 CREATE INDEX로 생성합니다.
CREATE INDEX IF NOT EXISTS idx_accounts_users_id
  ON accounts(users_id);

CREATE TABLE IF NOT EXISTS transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  from_acc TEXT NOT NULL,
  to_acc TEXT NOT NULL,
  amount NUMERIC,
  balance_after NUMERIC,
  description TEXT,
  xml_log TEXT,
  accounts_id INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (accounts_id)
    REFERENCES accounts (id)
    ON DELETE CASCADE
    ON UPDATE NO ACTION
);

CREATE INDEX IF NOT EXISTS idx_transactions_accounts_id
  ON transactions(accounts_id);

-- ENUM('notice','qna') -> CHECK 제약으로 변환
-- TINYINT -> INTEGER(+ CHECK)로 변환
CREATE TABLE IF NOT EXISTS posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  type TEXT DEFAULT 'qna' CHECK (type IN ('notice', 'qna')),
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  answer TEXT,
  status TEXT DEFAULT 'PENDING',
  is_secret INTEGER DEFAULT 0 CHECK (is_secret IN (0, 1)),
  users_id INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  answered_at TIMESTAMP,
  FOREIGN KEY (users_id)
    REFERENCES users (id)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
);

CREATE INDEX IF NOT EXISTS idx_posts_users_id
  ON posts(users_id);

CREATE TABLE IF NOT EXISTS post_files (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id INTEGER NOT NULL,
  filename TEXT NOT NULL,
  filepath TEXT NOT NULL,
  file_size INTEGER,
  upload_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id)
    REFERENCES posts(id)
    ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_post_files_post_id
  ON post_files(post_id);

CREATE TABLE IF NOT EXISTS exchange_rates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  currency TEXT NOT NULL,
  rate NUMERIC NOT NULL DEFAULT 0,
  provider_url TEXT
);


INSERT INTO users (username, password, nickname, email) VALUES
('testuser', 'test1234', '김테스트', 'test@example.com'),
('admin', 'admin1234', '관리자', 'admin@shieldusbank.com'),
('user1', 'pass1234', '박사용자', 'user1@example.com'),
('hacker', 'hack1234', '해커', 'hacker@evil.com');
-- 계좌 데이터
INSERT INTO accounts (account_number, users_id, balance, account_type) VALUES
('110-123-456789', 1, 1000000.00, 'SAVINGS'),
('220-987-654321', 1, 500000.00, 'CHECKING'),
('110-111-111111', 2, 5000000.00, 'SAVINGS'),
('110-222-222222', 3, 750000.00, 'SAVINGS'),
('220-333-333333', 3, 250000.00, 'CHECKING'),
('110-999-999999', 4, 100.00, 'SAVINGS');

-- 거래내역 데이터
INSERT INTO transactions (accounts_id, from_acc, to_acc, amount, balance_after, description, created_at) VALUES
(1, '110-123-456789', '110-222-222222', 50000.00, 750000.00, '생활비 송금', '2024-01-20 14:20:00'),
(1, '110-123-456789', '0', 120000, 100000, 'ATM 입금', '2024-01-25 16:45:00'),
(3, '110-111-111111', '0', 50000, 50000, '초기 입금', '2024-01-31 9:35:38'),
(4, '0', '220-987-654321', 400000, 100000, '초기 출금', '2024-01-31 9:35:39');

-- 문의게시판 데이터
INSERT INTO posts (users_id, title, content, status, created_at) VALUES
(1, '계좌 개설 문의', '새로운 계좌를 개설하고 싶습니다. 필요한 서류가 무엇인가요?', 'ANSWERED', '2024-01-10 10:00:00'),
(3, '송금 한도 문의', '일일 송금 한도를 늘리고 싶습니다.', 'PENDING', '2024-02-01 14:30:00'),
(1, '카드 발급 문의', '체크카드 발급이 가능한가요?', 'PENDING', '2024-02-05 16:20:00');

-- 문의게시판 답변
UPDATE posts SET answer = '신분증과 주소지 확인 서류를 준비해주시면 됩니다. 영업점 방문 또는 온라인으로 신청 가능합니다.',
              answered_at = '2024-01-10 15:00:00'
WHERE id = 1;