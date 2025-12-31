import sqlite3
import config

# 데이터베이스 연결 헬퍼
def get_db():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
