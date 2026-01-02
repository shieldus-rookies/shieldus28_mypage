-- CREATE DATABASE IF NOT EXISTS shieldus_bank
--   CHARACTER SET utf8
--   COLLATE utf8_general_ci;

-- USE shieldus_bank;

USE shieldus_bank;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS post_files, posts, transactions, accounts, users, exchange_rates;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(255) NOT NULL UNIQUE,
  password TEXT NOT NULL,
  email TEXT,
  nickname TEXT,
  role VARCHAR(255) DEFAULT 'user',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS accounts (
  id INT PRIMARY KEY AUTO_INCREMENT,
  account_number VARCHAR(255) NOT NULL UNIQUE,
  balance DOUBLE DEFAULT 0,
  account_type VARCHAR(50) DEFAULT 'SAVINGS',
  users_id INT NOT NULL,
  CONSTRAINT fk_accounts_users FOREIGN KEY (users_id) 
    REFERENCES users (id) ON DELETE CASCADE,
  INDEX idx_accounts_users_id (users_id)
);

CREATE TABLE IF NOT EXISTS transactions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  from_acc VARCHAR(255) NOT NULL,
  to_acc VARCHAR(255) NOT NULL,
  amount DOUBLE,
  balance_after DOUBLE,
  description TEXT,
  xml_log TEXT,
  accounts_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_transactions_accounts FOREIGN KEY (accounts_id) 
    REFERENCES accounts (id) ON DELETE CASCADE,
  INDEX idx_transactions_accounts_id (accounts_id)
);


CREATE TABLE IF NOT EXISTS posts (
  id INT PRIMARY KEY AUTO_INCREMENT,
  type VARCHAR(20) DEFAULT 'qna', 
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  answer TEXT,
  status VARCHAR(20) DEFAULT 'PENDING',
  is_secret INT DEFAULT 0,
  users_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  answered_at TIMESTAMP NULL DEFAULT NULL, 
  CONSTRAINT fk_posts_users FOREIGN KEY (users_id) 
    REFERENCES users (id) ON DELETE NO ACTION,
  INDEX idx_posts_users_id (users_id)
);

CREATE TABLE IF NOT EXISTS post_files (
  id INT PRIMARY KEY AUTO_INCREMENT,
  post_id INT NOT NULL,
  filename TEXT NOT NULL,
  filepath TEXT NOT NULL,
  file_size INT,
  upload_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_post_files_posts FOREIGN KEY (post_id) 
    REFERENCES posts(id) ON DELETE CASCADE,
  INDEX idx_post_files_post_id (post_id)
);

CREATE TABLE IF NOT EXISTS exchange_rates (
  id INT PRIMARY KEY AUTO_INCREMENT,
  currency VARCHAR(20) NOT NULL,
  rate DOUBLE NOT NULL DEFAULT 0,
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