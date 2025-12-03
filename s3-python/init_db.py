# Script para inicializar la base de datos sqlite con tabla users
import sqlite3, os
DB_PATH = 'db.sqlite'
if os.path.exists(DB_PATH):
    print("db.sqlite ya existe.")
else:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            otp_secret TEXT,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("Base de datos creada: db.sqlite")
