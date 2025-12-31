import pymysql
import config

# 데이터베이스 연결 헬퍼
def get_db():
    conn = pymysql.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        port=getattr(config, "DB_PORT", 3306),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,  # sqlite3.Row 비슷하게 dict로 받기
    )
    return conn
