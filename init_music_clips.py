import sqlite3

DB_NAME = 'patterns-matter.db'

with sqlite3.connect(DB_NAME) as conn:
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS music_clips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT
        );
    ''')
    conn.commit()

print("music_clips table created (if it didn't exist already).")