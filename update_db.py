import sqlite3

DB_NAME = "minisocial.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Dodaj kolonu za sliku u posts
try:
    cursor.execute("ALTER TABLE posts ADD COLUMN image TEXT")
    print("✅ Kolona 'image' uspešno dodata u tabelu posts")
except sqlite3.OperationalError as e:
    print("ℹ️ Kolona 'image' već postoji ili tabela ne postoji")
    print(e)

conn.commit()
conn.close()