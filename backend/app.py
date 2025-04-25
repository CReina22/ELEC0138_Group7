from flask import Flask, request, jsonify, render_template, request, session
from flask_cors import CORS
import sqlite3
import os
import webbrowser
import threading
import random
import smtplib
from email.mime.text import MIMEText
from flask import make_response
import secrets
import werkzeug.serving
import ssl
import OpenSSL
import hashlib
from joblib import load, dump
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
from sklearn.neighbors import LocalOutlierFactor
import requests
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import csv

## TLS Start

class PeerCertWSGIRequestHandler( werkzeug.serving.WSGIRequestHandler ):
        """
        We subclass this class so that we can gain access to the connection
        property. self.connection is the underlying client socket. When a TLS
        connection is established, the underlying socket is an instance of
        SSLSocket, which in turn exposes the getpeercert() method.
        The output from that method is what we want to make available elsewhere
        in the application.
        """
        def make_environ(self):
            """
            The superclass method develops the environ hash that eventually
            forms part of the Flask request object.
            We allow the superclass method to run first, then we insert the
            peer certificate into the hash. That exposes it to us later in
            the request variable that Flask provides
            """
            environ = super(PeerCertWSGIRequestHandler, self).make_environ()
            x509_binary = self.connection.getpeercert(True)
            # Check if the user has chosen to provide a certificate
            if x509_binary is not None:
                x509 = OpenSSL.crypto.load_certificate( OpenSSL.crypto.FILETYPE_ASN1, x509_binary )
            else:
                x509 = None
            environ['peercert'] = x509
            return environ

# Provide the server key and certificate
app_key = 'Certificates\\server.key'
app_key_password = None # None
app_cert = 'Certificates\\server.cer'

# List the certificates of trusted CAs that have signed client certificates
ca_cert = 'Certificates\\root.cer'

# create_default_context establishes a new SSLContext object that
# aligns with the purpose we provide as an argument. Here we provide
# Purpose.CLIENT_AUTH, so the SSLContext is set up to handle validation
# of client certificates.
ssl_context = ssl.create_default_context( purpose=ssl.Purpose.CLIENT_AUTH, cafile=ca_cert )

# Load the server certificate and client key to show to clients
ssl_context.load_cert_chain( certfile=app_cert, keyfile=app_key, password=app_key_password )
ssl_context.load_verify_locations(cafile=ca_cert)

# Allow clients to provide a certificate. Also allow clients to not present a certificate.
# High-level access bank staff must present a valid certificate to use the API.
ssl_context.verify_mode = ssl.CERT_OPTIONAL

## TLS End

session_tokens = {}

app = Flask(__name__,
            template_folder='../templates', 
            static_folder='../static')   

limiter = Limiter(get_remote_address, app=app)
#CORS(app, resources={r"/*": {"origins": "*"}})

## API Start

def to_fields(line):
    return line.rstrip().split(",")

customers = []
with open("bank_transactions.csv") as f:
    line = next(f)
    header = to_fields(line)

    for line in f:
        fields = to_fields(line)
        row = dict(zip(header, fields))
        customers.append(row)

@app.route('/customers/<string:TransactionID>', methods=['GET'])
def get_employee_by_id(TransactionID: str):
 # Only allow clients with a valid certificate to use the API
 if not request.environ['peercert']:
    print("Client certificate trusted")
    return jsonify({"success": False, "message": "Unauthorized"}), 401
 customer = get_employee(TransactionID)
 if customer is None:
   return jsonify({ 'error': 'Customer does not exist'}), 404
 return jsonify(customer)

def get_employee(TransactionID):
 return next((e for e in customers if e['TransactionID'] == TransactionID), None)

def employee_is_valid(customer):
    for key in customer.keys():
        if key != 'name':
            return False
    return True

## API End

@app.route('/')
def home():
    return render_template('index.html')
    # return render_template('index.html', client_cert=request.environ['peercert'])

#DB_FILE = 'customers.db'
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
            print("Connecting to Gmail SMTP server...")
            server.login('lynzhu12302@gmail.com', 'gzjzqyjhzrnmrwlk')
            print("Login successful")
            server.send_message(msg)
            print(f"Email sent successfully to {to_email}")
    except smtplib.SMTPException as e:
        print(f"[ERROR] SMTP error: {e}")
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
            user_id = user[0]
            username = user[1]
            is_fake = user[-1]
            
            # Clear the verification code after successful login
            cursor.execute("UPDATE users SET verification_code_login = NULL WHERE email = ?", (email,))
            conn.commit()
            
            # generate a session token
            token = f"{username}_{random.randint(1000,9999)}"
            session_tokens[token] = {
                'user_id': user_id,
                'username': username,
                'is_fake': is_fake
            }

            # setting cookie
            resp = make_response(jsonify({'success': True, 'message': 'Login successful!'}))
            resp.set_cookie("session_token", token)
            return resp
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
@limiter.limit("5 per minute") # Limit login attempts to 5 per minute
def login():
    
    try:
        data = request.get_json(force=True)  # force JSON parsing (test with Postman)
    except Exception as e:
        print("[ERROR] Failed to parse JSON:", e)
        return jsonify({"success": False, "message": "Invalid request format"}), 400

    print("[DEBUG] Raw data received:", data)
    
    #data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    ########################################################################################
    #######################    hCaptcha part below  ########################################
    captcha_token = data.get('h-captcha-response')
    print(f"[DEBUG] Username: {username}, Captcha token: {captcha_token}")

    if not captcha_token:
        return jsonify({"success": False, "message": "Captcha missing"}), 400

    
    secret = "ES_f5d1dffba9c24052a8d78644839598e4"
    verify_url = "https://hcaptcha.com/siteverify" 

    captcha_result = requests.post(verify_url, data={
        'secret': secret,
        'response': captcha_token
    }).json()
    print("[DEBUG] Captcha verify result:", captcha_result)

    if not captcha_result.get("success"):
        return jsonify({"success": False, "message": "Captcha verification failed"}), 403
    ################################## hCaptcha part above #####################################
    ############################################################################################


    ###########################################################
    #                    Anomaly Detection                    #
    ###########################################################
    fingerprint = data.get('fingerprint')
    fingerprint_data = json.loads(fingerprint)
    ###########################################################
    ###########################################################
    

    if not username or not password:
        return jsonify({"success": False, "message": "Username, password."}), 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()


    ###########################################################
    #                    Anomaly Detection                    #
    ###########################################################
    if user:
        user_id = user[0]
        is_fake = user[-2]

        if FINGERPRINTING == True:
            # Prepare fingerprint details for comparison and encode features
            fingerprint_vector = [
                hash(fingerprint_data.get('browser')),
                hash(fingerprint_data.get('os')),
                hash(fingerprint_data.get('screenResolution')),
                hash(fingerprint_data.get('timezone')),
                hash(fingerprint_data.get('language')),
                hash(json.dumps(fingerprint_data.get('plugins'))),
            ]

            # Check for existing fingerprints
            cursor.execute("SELECT browser, os, screen_resolution, \
                            timezone, language, plugins FROM fingerprints WHERE user_id = ?", 
                            (user_id,))
            existing_fingerprints = cursor.fetchall()

            if existing_fingerprints:
                # Convert existing fingerprints to encoded vectors for comparison
                existing_vectors = [
                    [
                        hash(fp[0]), hash(fp[1]), hash(fp[2]), hash(fp[3]), hash(fp[4]), hash(fp[5]) 
                    ] for fp in existing_fingerprints
                ]
                x_train = np.array(existing_vectors)

                # Use LocalOutlierFactor model for more than five prints
                if len(existing_fingerprints) > 5:
                    try:
                        model = LocalOutlierFactor(n_neighbors=20, novelty=True, contamination=0.1)
                        model.fit(x_train)
                        print('ML Model')

                        is_anomaly = model.predict([fingerprint_vector]) == -1
                        if is_anomaly:
                            print("ML Suspicious Fingerprint Detected")
                            
                            # Generate and send OTP
                            otp = generate_code()
                            cursor.execute("UPDATE users SET otp = ? WHERE email = ?", (otp, user[3])) 
                            conn.commit()
                            send_email(user[3], otp)
                            
                            return jsonify({
                                "success": False,
                                "message": "Suspicious login pattern detected. OTP sent to your email.",
                                "requires_otp": True,
                                "email": user[3]
                            }), 403
                        
                        else: 
                            print("Fingerprint Verified")

                    except Exception as e:
                        print(f"Error in anomaly detection: {e}")
                
        
            

            # Store fingerprint for this login when successful, store additional metrics for future use
            cursor.execute('''
                INSERT INTO fingerprints (
                user_id, fingerprint_hash, browser, os, screen_resolution, timezone, language, 
                color_depth, pixel_ratio, cookies_enabled, do_not_track, plugins, cpu_cores, 
                connection_type, canvas_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ''', (
                user_id, int(hashlib.sha256(fingerprint.encode()).hexdigest(), 16) % (10 ** 8),
                fingerprint_data.get('browser'), fingerprint_data.get('os'),
                fingerprint_data.get('screenResolution'), fingerprint_data.get('timezone'),
                fingerprint_data.get('language'), fingerprint_data.get('colorDepth'),
                fingerprint_data.get('pixelRatio'), fingerprint_data.get('cookiesEnabled'),
                fingerprint_data.get('doNotTrack'), json.dumps(fingerprint_data.get('plugins')),
                fingerprint_data.get('cpuCores'), fingerprint_data.get('connectionType'),
                fingerprint_data.get('canvasHash')
            ))
            conn.commit()
        ###########################################################
        ###########################################################



        # Generate a session token
        token = f"{username}_{random.randint(1000,9999)}"
        session_tokens[token] = {
            'user_id': user_id,
            'username': username,
            'is_fake': is_fake
        }

        # Set the session token in the response cookie
        resp = make_response(jsonify({
            "success": True,
            "message": "Login successful"
        }))
        resp.set_cookie("session_token", token)
        return resp

    conn.close()
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

# transactions page
@app.route('/transactions')
def transactions_page():
    username = session_tokens.get(request.cookies.get('session_token'), {}) \
                                .get('username', '')
    return render_template('transactions.html', username=username)

# get transactions API
@app.route('/api/transactions', methods=['GET'])
@limiter.limit("5 per minute") # Limit transaction requests to 5 per minute
def get_transactions_api():
    token = request.cookies.get("session_token")
    print("token from cookie:", token)
    print("current session_tokens:", session_tokens.keys())  # effective session tokens
    print("user info:", session_tokens.get(token))  # if no , means clear

    # check if the token is valid
    if not token or token not in session_tokens:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    # get user info from the session token
    user_info = session_tokens[token]
    user_id = user_info['user_id']
    is_fake = user_info['is_fake']
    
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


@app.route('/logout', methods=['POST'])
def logout():
    token = request.cookies.get("session_token")

    if token and token in session_tokens:
        session_tokens.pop(token)  # delete the session token from the server
    # clear the session token cookie
    resp = make_response(jsonify({"success": True, "message": "Logged out"}))
    resp.set_cookie(
        "session_token", 
        "", 
        path="/",      
        max_age=0      
    )
    return resp


###########################################################
#                    Anomaly Detection                    #
###########################################################
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    fingerprint = data.get('fingerprint')  # Get fingerprint data from the request

    if not email or not otp:
        return jsonify({'success': False, 'message': 'Email and OTP are required'}), 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ? AND otp = ?", (email, otp))
    user = cursor.fetchone()

    if user:
        # Clear the OTP after successful verification
        cursor.execute("UPDATE users SET otp = NULL WHERE email = ?", (email,))
        conn.commit()

        # Save the fingerprint to the database
        if fingerprint:
            try:
                fingerprint_data = json.loads(fingerprint)
                user_id = user[0]  # Get user_id from the found user

                cursor.execute('''
                    INSERT INTO fingerprints (
                    user_id, fingerprint_hash, browser, os, screen_resolution, timezone, language, 
                    color_depth, pixel_ratio, cookies_enabled, do_not_track, plugins, cpu_cores, 
                    connection_type, canvas_hash, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ''', (
                    user_id, int(hashlib.sha256(fingerprint.encode()).hexdigest(), 16) % (10 ** 8),
                    fingerprint_data.get('browser'), fingerprint_data.get('os'),
                    fingerprint_data.get('screenResolution'), fingerprint_data.get('timezone'),
                    fingerprint_data.get('language'), fingerprint_data.get('colorDepth'),
                    fingerprint_data.get('pixelRatio'), fingerprint_data.get('cookiesEnabled'),
                    fingerprint_data.get('doNotTrack'), json.dumps(fingerprint_data.get('plugins')),
                    fingerprint_data.get('cpuCores'), fingerprint_data.get('connectionType'),
                    fingerprint_data.get('canvasHash')
                ))
                conn.commit()
            except Exception as e:
                print(f"[Error] Failed to save fingerprint: {e}")
                return jsonify({'success': False, 'message': 'Failed to save fingerprint'}), 500

        conn.close()
        return jsonify({'success': True, 'message': 'OTP verified successfully. Please log in again.'})
    else:
        conn.close()
        return jsonify({'success': False, 'message': 'Invalid OTP'}), 401
###########################################################
###########################################################

def open_browser():    
    #webbrowser.open_new("http://127.0.0.1:5000/")
    webbrowser.open_new("https://127.0.0.1:5000/") # Option for TLS handshaking
 
# Launch Website    
if __name__ == '__main__':
    if not os.path.exists(DB_FILE):
        print("Error: customers.db not found.")
    else:
        #if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        #    threading.Timer(1.5, open_browser).start()

        host_ip = '127.0.0.1'  # Listen on all available interfaces
        port = 5000
        print(f"Backend server is running at https://{host_ip}:{port}")
        print(f"Access from another device using your computer's IP address and port {port}")
        ssl_easy = ('../certs/cert.pem', '../certs/key.pem')
        ssl_easy_raven = ('Certificates\\server.cer', 'Certificates\\server.key')
        
        #To enable the use of fingerprinting authentication change this variable to True
        FINGERPRINTING = True 

        #app.run(debug=True, host=host_ip, port=port)
        #app.run(debug=True, host=host_ip, port=port, ssl_context=ssl_easy_raven) # Option for TLS handshaking with Dummy Certificate
        app.run( debug=True, host=host_ip, port=port, ssl_context=ssl_context, request_handler=PeerCertWSGIRequestHandler ) # Option for TLS handshaking with Client Authentication

