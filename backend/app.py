from flask import Flask, request, jsonify, render_template, request
from flask_cors import CORS
import sqlite3
import os
import webbrowser
import threading
import random
import smtplib
from email.mime.text import MIMEText


app = Flask(__name__,
            template_folder='../templates', 
            static_folder='../static')     


@app.route('/')
def home():
    return render_template('index.html')


DB_FILE = 'customers.db'

def generate_code():
    return str(random.randint(100000, 999999))

def send_email(to_email, code):
    try:
        msg = MIMEText(f"Your verification code is: {code}")
        msg['Subject'] = "Digital Bank Login Code"
        msg['From'] = "lynzhu12302@gmail.com"
        msg['To'] = to_email

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('lynzhu12302@gmail.com', 'gzjzqyjhzrnmrwlk')
            server.send_message(msg)
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
        
#def send_email_async(to_email, code):
    #threading.Thread(target=send_email, args=(to_email, code)).start()

@app.route('/send-code', methods=['POST'])
def send_code():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify(success=False, message="Email is required"), 400

    code = generate_code()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # check if the email exists in the database
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify(success=False, message="Email not registered"), 404

    # update the verification code in the database
    cursor.execute("UPDATE users SET verification_code_login = ? WHERE email = ?", (code, email))
    conn.commit()
    conn.close()

    send_email(email, code)
    return jsonify(success=True, message="Verification code sent to your email.")


@app.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')

    if not email or not code:
        return jsonify(success=False, message="Email and code required"), 400

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND verification_code_login = ?", (email, code))
        user = cursor.fetchone()
        
        if user:
            # Clear the verification code after successful login
            cursor.execute("UPDATE users SET verification_code_login = NULL WHERE email = ?", (email,))
            conn.commit()
            return jsonify({'success': True, 'message': 'Login successful!'})

        else:
            return jsonify({'success': False, 'message': 'Invalid code or email'}), 401

    except Exception as e:
        print(f"[Error] Verification failed: {e}")
        return jsonify({'success': False, 'message': 'Server error during verification'}), 500

    finally:
        conn.close()



# register port
@app.route('/register_email', methods=['POST'])
def register_email():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'status': 'error', 'message': 'Email is required'}), 400

    code = generate_code()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # check if the email is already registered
    cursor.execute("SELECT username, password FROM users WHERE email = ?", (email,))
    existing_user = cursor.fetchone()

    if existing_user and existing_user[0] and existing_user[1]:
        conn.close()
        return jsonify({'status': 'error', 'message': 'Email already registered'}), 409

    # check if the email exists but not finshed register
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("UPDATE users SET verification_code_register = ? WHERE email = ?", (code, email))
    else:
        cursor.execute("INSERT INTO users (username, password, email, verification_code_register) VALUES (?, ?, ?, ?)", 
                    ('', '', email, code))

    conn.commit()
    conn.close()

    send_email(email, code)
    return jsonify({'status': 'success', 'message': 'Verification code sent'})


@app.route('/verify_register_code', methods=['POST'])
def verify_register_code():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    code = data.get('code')
    password = data.get('password')

    if not username or not email or not code or not password:
        return jsonify({'status': 'error', 'message': 'All fields are required'}), 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # check if the email exists in the database
    cursor.execute("SELECT verification_code_register FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    if not row or row[0] != code:
        return jsonify({'status': 'error', 'message': 'Invalid verification code'}), 401

    # check if the email is already registered
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        return jsonify({'status': 'error', 'message': 'Username already taken'}), 409

    # update the user information
    cursor.execute("UPDATE users SET username = ?, password = ?, verification_code_register = NULL WHERE email = ?", 
                (username, password, email))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': 'Registration successful'})
    



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
        user_id = user[0]       # id
        username = user[1]      # username
        is_fake = user[-1]      # is_fake column

        return jsonify({
            "success": True,
            "user_id": user_id,
            "username": username,
            "is_fake": is_fake
        })
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401


# get transaction port
@app.route('/transactions', methods=['POST'])
def get_transactions():
    data = request.get_json()
    user_id = data.get("user_id")
    is_fake = data.get("is_fake")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if is_fake:
        # testuser: display assigned transactions
        cursor.execute("SELECT * FROM transactions WHERE user_id = ?", (user_id,))
    else:
        # real users：display first 100 transactions
        cursor.execute("SELECT * FROM transactions LIMIT 100")
        
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    results = [dict(zip(columns, row)) for row in rows]
    return jsonify(results)


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

# launch the server
if __name__ == '__main__':
    if not os.path.exists(DB_FILE):
        print("Error: customers.db not found.")
    else:
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            threading.Timer(1.5, open_browser).start()

        host_ip = '0.0.0.0'  # Listen on all available interfaces
        port = 5000
        print(f"Backend server is running at http://{host_ip}:{port}")
        print(f"Access from another device using your computer's IP address and port {port}")
        app.run(debug=True, host=host_ip, port=port)
