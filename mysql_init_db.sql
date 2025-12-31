CREATE DATABASE IF NOT EXISTS mydb
  CHARACTER SET utf8
  COLLATE utf8_general_ci;

USE mydb;

CREATE TABLE IF NOT EXISTS users (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  email VARCHAR(100),
  nickname VARCHAR(50),
  role VARCHAR(10) DEFAULT 'user'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS accounts (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  account_number VARCHAR(20) NOT NULL UNIQUE,
  balance DECIMAL(18,2) DEFAULT 0,
  users_id INT NOT NULL,
  INDEX fk_accounts_users1_idx (users_id),
  CONSTRAINT fk_accounts_users1
    FOREIGN KEY (users_id)
    REFERENCES users (id)
    ON DELETE CASCADE
    ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS transactions (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  from_acc INT NOT NULL,
  to_acc INT NOT NULL,
  amount DECIMAL(18,2),
  memo TEXT,
  xml_log TEXT,
  accounts_id INT NOT NULL,
  INDEX fk_transactions_accounts1_idx (accounts_id),
  CONSTRAINT fk_transactions_accounts1
    FOREIGN KEY (accounts_id)
    REFERENCES accounts (id)
    ON DELETE CASCADE
    ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS posts (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  type ENUM('notice', 'qna'),
  title VARCHAR(255),
  content TEXT,
  is_secret TINYINT DEFAULT 0,
  users_id INT NOT NULL,
  INDEX fk_posts_users1_idx (users_id),
  CONSTRAINT fk_posts_users1
    FOREIGN KEY (users_id)
    REFERENCES users (id)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS post_files (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,

  posts_id INT NOT NULL,
  INDEX fk_post_files_posts1_idx (posts_id),

  original_name VARCHAR(255) NOT NULL,   -- 사용자가 업로드한 파일명
  stored_name   VARCHAR(255) NOT NULL,   -- 서버에 저장된 파일명(충돌 방지용 UUID 등)
  mime_type     VARCHAR(100) NULL,       -- 예: image/png
  file_size     BIGINT NULL,             -- bytes
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_post_files_posts1
    FOREIGN KEY (posts_id)
    REFERENCES posts (id)
    ON DELETE CASCADE
    ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS exchange_rates (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  currency VARCHAR(10) NOT NULL,
  rate DECIMAL(10,4) NOT NULL DEFAULT 0,
  provider_url VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

