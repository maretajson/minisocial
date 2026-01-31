import sqlite3

conn = sqlite3.connect("minisocial.db")
c = conn.cursor()

c.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    bio TEXT DEFAULT '',
    profile_pic TEXT DEFAULT 'default.png'
)
""")

c.execute("""
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    content TEXT
)
""")

conn.commit()
conn.close()

print("✅ Database created")