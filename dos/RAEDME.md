# DoS Attack & Defence Guide

This document provides instructions to perform **HTTP Flood** and **SYN Flood** attacks, and defence.

## 🖥️ Environment Setup
- Launch both **Kali Linux** (attacker) and **Ubuntu** (defender) virtual machines.
- Set the network adapter for both VMs to **Bridge Adapter**.
- Install Snort.
-  'cd backend'
- 'python3 app.py'


## Step 2: Launch DoS Attacks
### 1. HTTP Flood Attack
```bash
cd dos
```
```bash
python3 flooding.py
```

Use `Ctrl + C` to stop the attack.

### 2. SYN Flood Attack (On the **Kali** machine)
First, get the IP address of the Ubuntu server:

```bash
ip a
```

Assume the IP is `172.20.10.9`. Then run:

```bash
sudo hping3 -S --flood -p 5000 172.20.10.9
```

Use `Ctrl + C` to stop the attack.

## Step 3: Configure Snort Detection Rules
On the **Ubuntu** machine, edit the local Snort rule file:

```bash
sudo nano /etc/snort/rules/local.rules
```

Add the following rules:

```snort
# Detect SYN Flood Attack (within 3 seconds receive over 20 SYN packets)
alert tcp any any -> $HOME_NET 5000 (flags:S; threshold:type threshold, track by_src, count 20, seconds 3; msg:"SYN Flood Detected"; sid:1000001;)

# Detect HTTP GET Flood Attack (within 10 seconds receive over 100 GET from same IP)
alert tcp any any -> $HOME_NET 5000 (msg:"HTTP GET Flood Detected"; flow:to_server,established; content:"GET"; http_method; detection_filter:track by_src, count 100, seconds 10; sid:1000002;)

# Detect HTTP POST Flood (within 10 seconds receive over 100 POST requests)
alert tcp any any -> $HOME_NET 5000 (msg:"HTTP POST Flood Detected"; flow:to_server,established; content:"POST"; http_method; detection_filter:track by_src, count 100, seconds 10; sid:1000003;)
Save and exit.
```
Save and exit the file.



## Step 3: Start Snort and Monitor Alerts

Run Snort (replace `enp0s3` with your actual network interface):

```bash
sudo snort -A fast -q -i enp0s3 -c /etc/snort/snort.conf
```

To monitor alerts in real time (optional):

```bash
sudo tail -f /var/log/snort/alert
```

## Step 4: Run the Auto-Blocking Script

In another terminal on **Ubuntu**, run the blocking script:

```bash
sudo python3 block_snort_ip.py
```

## Step 5: Re-Test the Attack and Observe the Defence
Then rerun the SYN Flood attack on **Kali** to test the defence.