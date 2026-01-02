'''
import sqlite3
import config

# 데이터베이스 연결 헬퍼
def get_db():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
'''
import os
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
    
def _load_sql_statements(sql_path: str) -> list[str]:
    # -- 주석 제거 + 세미콜론 기준 분리(간단 버전)
    with open(sql_path, "r", encoding="utf-8") as f:
        lines = []
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("--"):
                continue
            # 라인 중간 주석(-- ...) 제거(최소 처리)
            if "--" in line:
                line = line.split("--", 1)[0]
            lines.append(line)

    sql = "".join(lines)
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    return statements


def init_db(sql_path: str | None = None) -> bool:
    """
    최초 1회만 초기화:
    - users 테이블이 이미 있으면 스킵(데이터 날아가는 것 방지)
    - 없으면 init_db.sql 실행
    """
    conn = get_db()
    if conn is None:
        print("[init_db] DB connection failed")
        return False

    try:
        with conn.cursor() as cur:
            cur.execute("SHOW TABLES LIKE 'users'")
            if cur.fetchone():
                # 이미 초기화되어 있다고 보고 스킵
                return False

        if sql_path is None:
            # 프로젝트 루트에 init_db.sql이 있다고 가정
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            sql_path = os.path.join(project_root, "init_db.sql")

        statements = _load_sql_statements(sql_path)

        with conn.cursor() as cur:
            for stmt in statements:
                cur.execute(stmt)

        conn.commit()
        print("[init_db] DB initialized")
        return True

    except Exception as e:
        conn.rollback()
        print(f"[init_db] failed: {e}")
        return False

    finally:
        conn.close()