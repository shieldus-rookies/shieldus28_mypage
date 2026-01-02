import sqlite3
import os

# 데이터베이스 파일 경로
DB_PATH = os.path.join(os.path.dirname(__file__), 'vulnerable_app.db')
SQL_FILE = os.path.join(os.path.dirname(__file__), 'init_db.sql')

# 기존 데이터베이스 파일이 있으면 삭제
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print(f"기존 데이터베이스 파일 삭제: {DB_PATH}")

# SQL 파일 읽기
with open(SQL_FILE, 'r', encoding='utf-8') as f:
    sql_script = f.read()

# 데이터베이스 연결 및 스크립트 실행
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("데이터베이스 초기화 중...")

# SQL 스크립트 실행
cursor.executescript(sql_script)

# 변경사항 저장 및 연결 종료
conn.commit()
conn.close()

print("[OK] 데이터베이스 초기화 완료!")
print(f"[INFO] 데이터베이스 파일: {DB_PATH}")
print("\n[INFO] 생성된 테스트 계정:")
print("  - testuser / test1234")
print("  - admin / admin1234")
print("  - user1 / pass1234")
print("  - hacker / hack1234")
print("\n[INFO] 계좌 정보:")
print("  - testuser: 110-123-456789 (잔액: 1,000,000원)")
print("  - testuser: 220-987-654321 (잔액: 500,000원)")
print("\n[WARNING] 이 데이터베이스는 교육용 취약점을 포함하고 있습니다!")
