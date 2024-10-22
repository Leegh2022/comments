# data/user_db.py

import sqlite3
import os

DB_PATH = 'users.db'

def initialize_db():
    """데이터베이스와 테이블을 초기화합니다."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 사용자 테이블 생성 (username을 기본 키로 설정)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY
        )
    ''')
    
    # 식단 테이블 생성 (id, username, 식단 내용)
    c.execute('''
        CREATE TABLE IF NOT EXISTS diets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            diet_content TEXT,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(username):
    """사용자를 추가합니다. 이미 존재하면 False를 반환."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username) VALUES (?)', (username,))
        conn.commit()
    except sqlite3.IntegrityError:
        # 사용자가 이미 존재하는 경우
        conn.close()
        return False
    conn.close()
    return True

def get_user(username):
    """사용자를 조회합니다."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def add_diet(username, diet_content):
    """사용자의 식단 내용을 추가합니다."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO diets (username, diet_content) VALUES (?, ?)', (username, diet_content))
    conn.commit()
    conn.close()

def get_diets(username):
    """사용자의 모든 식단 내용을 조회합니다."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT diet_content FROM diets WHERE username = ?', (username,))
    diets = c.fetchall()
    conn.close()
    return diets
