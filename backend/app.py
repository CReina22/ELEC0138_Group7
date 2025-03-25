from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import webbrowser
import threading

app = Flask(__name__)
CORS(app)

DB_FILE = 'customers.db'

# register port
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return jsonify({"success": True, "message": "Registration successful"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Username already exists"}), 409
    finally:
        conn.close()


# login port
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401


# get transaction port
@app.route('/transactions', methods=['GET'])
def get_transactions():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transactions LIMIT 100")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    results = [dict(zip(columns, row)) for row in rows]
    return jsonify(results)


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5501/front/index.html")

# launch the server
if __name__ == '__main__':
    if not os.path.exists(DB_FILE):
        print("Error: customers.db not found.")
    else:
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            threading.Timer(1.5, open_browser).start()

        print("Backend server is running at http://127.0.0.1:5000")
        app.run(debug=True)

