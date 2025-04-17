import subprocess
import time
import threading
import re

# ------------ Configuration ------------

ALERT_LOG = "/var/log/snort/alert"
BLOCK_DURATION = 600  # Duration to block IPs (in seconds)

# Match Snort alerts based on your rule messages (msg field)
TRIGGER_KEYWORDS = [
    "SYN Flood Detected",
    "HTTP GET Flood Detected",
    "HTTP POST Flood Detected",
    "POST Flood on /login Detected"
]

BLOCKED_IPS = set()  # Keep track of already blocked IPs
IP_PATTERN = re.compile(r"\{TCP\}\s+(\d+\.\d+\.\d+\.\d+):\d+\s+->")

# ------------ IP Blocking Logic ------------

def block_ip(ip):
    if ip in BLOCKED_IPS:
        return
    print(f"Blocking IP: {ip}")
    subprocess.run(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
    BLOCKED_IPS.add(ip)
    threading.Thread(target=unblock_ip_after_delay, args=(ip, BLOCK_DURATION)).start()

def unblock_ip_after_delay(ip, delay):
    time.sleep(delay)
    print(f"Unblocking IP: {ip}")
    subprocess.run(["iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"])
    BLOCKED_IPS.discard(ip)

# ------------ Snort Log Monitor ------------

def monitor_snort_alerts():
    print("[🔍] Monitoring Snort alerts...")
    with open(ALERT_LOG, "r") as f:
        f.seek(0, 2)  # Go to the end of file like `tail -f`
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue

            for keyword in TRIGGER_KEYWORDS:
                if keyword in line:
                    print(f"Alert triggered: {keyword}")

                    for _ in range(5):
                        ip_line = f.readline()
                        if not ip_line:
                            break
                        print(f"Scanning line: {ip_line.strip()}")
                        match = IP_PATTERN.search(ip_line)
                        if match:
                            attacker_ip = match.group(1)
                            print(f"Detected IP: {attacker_ip}")
                            block_ip(attacker_ip)
                            break
                    else:
                        print("No IP found in the alert line.")
                    break

# ------------ Entry Point ------------

if __name__ == "__main__":
    try:
        monitor_snort_alerts()
    except KeyboardInterrupt:
        print("\n Stopped monitoring. Exiting...")
