import sqlite3
from config import Config

def init_db():
    conn = sqlite3.connect(Config.DATABASE)
    c = conn.cursor()
    
    # Users 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, 
                  username TEXT, 
                  password TEXT, 
                  email TEXT, 
                  profile_pic TEXT, 
                  nickname TEXT, 
                  status_message TEXT)''')
    
    # Inquiries 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS inquiries
                 (id INTEGER PRIMARY KEY, 
                  user_id INTEGER, 
                  title TEXT, 
                  content TEXT, 
                  attachment TEXT)''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

if __name__ == '__main__':
    init_db()