'''
import sqlite3
import config

# 데이터베이스 연결 헬퍼
def get_db():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
'''

import pymysql
import config

def get_db():
    try:
        # pymysql을 사용하여 MySQL에 접속
        connection = pymysql.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            db=config.DB_NAME,
            port=config.DB_PORT,
            charset='utf8mb4',
            # 결과를 딕셔너리 형태로 받아야 기존 코드(row['username'])가 작동
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"Error connecting to MySQL: {e}")
        return None