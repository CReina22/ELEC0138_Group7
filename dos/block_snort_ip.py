import subprocess
import time
import threading
import re

# ------------ Configuration ------------

ALERT_LOG = "/var/log/snort/alert"
BLOCK_DURATION = 300  # secs

# keywords to match Snort alerts (msg field)
TRIGGER_KEYWORDS = [
    "SYN Flood Detected",
    "HTTP GET Flood Detected",
    "HTTP POST Flood Detected",
    "POST Flood on /login Detected"
]


BLOCKED_IPS = set()

# extract IP from Snort log
IP_PATTERN = re.compile(r"\{TCP\}\s+(\d+\.\d+\.\d+\.\d+):\d+\s+->")

# For tracking block timing
ip_first_seen = {}
ip_blocked_at = {}

# ------------ IP Blocking Logic ------------

def block_ip(ip):
    """block ip and unblock it after BLOCK_DURATION seconds"""
    if ip in BLOCKED_IPS:
        return
    now = time.time()
    if ip not in ip_first_seen:
        ip_first_seen[ip] = now  # mark first time this IP appears in alert
    ip_blocked_at[ip] = now
    blocked_after = now - ip_first_seen[ip]


    # check if iptables rule already exists
    check = subprocess.run(
        ["iptables", "-C", "INPUT", "-s", ip, "-j", "DROP"],
        capture_output=True
    ).returncode
    if check == 0:
        print(f"Already exists，：{ip}")
    else:
        print(f"Blocking IP: {ip}")
        subprocess.run(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])

    print(f"[INFO] IP {ip} blocked after {blocked_after:.2f} seconds")
    BLOCKED_IPS.add(ip)

    # unblock IP after BLOCK_DURATION seconds
    t = threading.Thread(
        target=lambda: (time.sleep(BLOCK_DURATION),
                        subprocess.run(["iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"]),
                        BLOCKED_IPS.remove(ip)),
        daemon=True
    )
    t.start()

# ------------ Snort Log Monitor ------------

def monitor_snort_alerts():
    print("Monitoring Snort alerts...")
    with open(ALERT_LOG, "r") as f:
        f.seek(0, 2)  
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue

            # extract IP from the line
            for kw in TRIGGER_KEYWORDS:
                if kw in line:
                    # if keyword found, look ahead several lines to find IP line
                    for _ in range(5):
                        ip_line = f.readline()
                        if not ip_line:
                            break
                        m = IP_PATTERN.search(ip_line)
                        if m:
                            src = m.group(1)
                            # skipping if IP already blocked
                            if src in BLOCKED_IPS:
                                break

                            # alter ip for 1st time
                            print(f"Alert triggered: {kw}")
                            print(f"Detected attacker IP: {src}")
                            block_ip(src)
                            break
                    break  

# ------------ Entry Point ------------

if __name__ == "__main__":
    try:
        monitor_snort_alerts()
    except KeyboardInterrupt:
        print("\nStopped monitoring. Exiting…")