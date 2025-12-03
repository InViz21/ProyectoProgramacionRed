"""
S3 - Servidor de recursos (REST)
Endpoints actuales:
 - POST /users
 - GET /users/<username>
 - GET /health

Nuevos endpoints CRUD:
 - GET /items
 - POST /items
 - GET /items/<id>
 - PUT /items/<id>
 - DELETE /items/<id>
"""

from flask import Flask, request, jsonify
import sqlite3, os, hashlib

DB_PATH = 'db.sqlite'

# Función para conectar SQLite
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Verificar existencia de DB
def init_db():
    if not os.path.exists(DB_PATH):
        print("db.sqlite no encontrada. Ejecuta init_db.py para crear la DB.")
    else:
        print("DB encontrada:", DB_PATH)

app = Flask(__name__)
init_db()

# ========================================
# UTILIDADES
# ========================================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ========================================
# USERS
# ========================================

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({'error': 'Faltan campos'}), 400

    ph = hash_password(password)
    otp_secret = os.urandom(16).hex()

    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO users (username, password_hash, otp_secret, email) VALUES (?, ?, ?, ?)',
            (username, ph, otp_secret, email)
        )
        conn.commit()
        return jsonify({'message': 'Usuario creado', 'otp_secret': otp_secret}), 201

    except sqlite3.IntegrityError:
        return jsonify({'error': 'Usuario ya existe'}), 400

    finally:
        conn.close()

@app.route('/users/<username>', methods=['GET'])
def get_user(username):
    conn = get_db()
    cur = conn.execute(
        'SELECT id,username,password_hash,otp_secret,email FROM users WHERE username=?',
        (username,)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({'error': 'No encontrado'}), 404

    return jsonify(dict(row))

# ========================================
# CRUD ITEMS
# ========================================

@app.route('/items', methods=['GET'])
def get_items():
    conn = get_db()
    cur = conn.execute("SELECT * FROM items")
    rows = cur.fetchall()
    conn.close()

    items = [dict(row) for row in rows]
    return jsonify(items), 200

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    conn = get_db()
    cur = conn.execute("SELECT * FROM items WHERE id=?", (item_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({'error': 'Item no encontrado'}), 404

    return jsonify(dict(row)), 200

@app.route('/items', methods=['POST'])
def create_item():
    data = request.json or {}
    name = data.get('name')
    description = data.get('description')

    if not name:
        return jsonify({'error': 'Falta el nombre'}), 400

    conn = get_db()
    cur = conn.execute(
        "INSERT INTO items (name, description) VALUES (?, ?)",
        (name, description)
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return jsonify({'id': new_id, 'name': name, 'description': description}), 201

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.json or {}
    name = data.get('name')
    description = data.get('description')

    conn = get_db()
    conn.execute(
        "UPDATE items SET name=?, description=? WHERE id=?",
        (name, description, item_id)
    )
    conn.commit()
    conn.close()

    return jsonify({'id': item_id, 'name': name, 'description': description}), 200

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    conn = get_db()
    conn.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Item eliminado'}), 200

# ========================================
# HEALTH CHECK
# ========================================

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

# ========================================

if __name__ == '__main__':
    app.run(port=5002)
