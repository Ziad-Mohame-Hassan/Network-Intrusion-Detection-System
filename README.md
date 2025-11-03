# 🛡️ Network Intrusion Detection System (NIDS)

> **ML-Powered Port Scan Detection with Real-Time Alerts and Email Notifications**

A comprehensive Network Intrusion Detection System that combines Suricata for network traffic capture, Machine Learning for port scan detection, real-time web dashboard, and intelligent email alerting with rate limiting.

---

## 📋 Table of Contents

- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [1. Install Node.js and npm](#1-install-nodejs-and-npm)
  - [2. Install Suricata](#2-install-suricata)
  - [3. Install Python and Dependencies](#3-install-python-and-dependencies)
  - [4. Install Project Dependencies](#4-install-project-dependencies)
- [Configuration](#-configuration)
  - [Suricata Configuration](#suricata-configuration)
  - [Email Configuration](#email-configuration)
- [Running the Project](#-running-the-project)
  - [Quick Start (Automated)](#quick-start-automated)
  - [Manual Start (4 Terminals)](#manual-start-4-terminals)
- [Testing](#-testing)
- [Email Rate Limiting](#-email-rate-limiting)
- [Troubleshooting](#-troubleshooting)
- [Project Structure](#-project-structure)
- [Stopping the System](#-stopping-the-system)

---

## 🎯 Features

- ✅ **Real-time Network Monitoring** - Captures and analyzes network traffic using Suricata
- ✅ **ML-Based Port Scan Detection** - Random Forest model with 95%+ accuracy
- ✅ **Live Web Dashboard** - React frontend with real-time updates via Socket.IO
- ✅ **Email Alerts** - Automatic notifications to administrator
- ✅ **Intelligent Rate Limiting** - Sends 1 email per IP every 6 hours to prevent spam
- ✅ **Multiple Attack Detection** - Tracks each unique attacker separately
- ✅ **Activity Classification** - Identifies DNS, HTTP, SSH, FTP, and 20+ protocols
- ✅ **Security Alerts** - Real-time notifications in web interface

---

## 🏗️ System Architecture

```
┌─────────────────┐
│   Suricata      │ ← Captures network traffic
│  (Port Mirror)  │
└────────┬────────┘
         │ eve.json logs
         ↓
┌─────────────────────────────────────────────────────────┐
│                 Node.js Backend                         │
│  - Parses Suricata logs                                 │
│  - Streams data via Socket.IO                           │
│  - Receives ML alerts                                   │
└──────────┬──────────────────────────────────┬───────────┘
           │                                  │
           ↓                                  ↓
┌──────────────────┐              ┌────────────────────────┐
│  React Frontend  │              │  ML Port Scan Detector │
│  (Port 3000)     │              │  - Random Forest Model │
│  - Dashboard     │              │  - Email Alerts        │
│  - Real-time UI  │              │  - Rate Limiting       │
└──────────────────┘              └────────────┬───────────┘
                                               │
                                               ↓
                                    ┌──────────────────────┐
                                    │   Email Alerts       │
                                    │  (Gmail SMTP)        │
                                    └──────────────────────┘
```

---

## 📦 Prerequisites

- **Operating System:** Linux (Ubuntu 20.04+ recommended)
- **Python:** 3.8 or higher
- **Node.js:** 14.x or higher
- **npm:** 6.x or higher
- **Suricata:** 6.x or higher
- **Root/Sudo Access:** Required for Suricata installation and configuration

---

## 🚀 Installation

### 1. Install Node.js and npm

```bash
# Update package list
sudo apt update

# Install Node.js and npm
sudo apt install -y nodejs npm

# Verify installation
node --version   # Should show v14.x or higher
npm --version    # Should show 6.x or higher

# If version is too old, install from NodeSource:
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

---

### 2. Install Suricata

```bash
# Add Suricata repository
sudo add-apt-repository ppa:oisf/suricata-stable
sudo apt update

# Install Suricata
sudo apt install -y suricata

# Verify installation
suricata --version

# Enable Suricata service
sudo systemctl enable suricata
sudo systemctl start suricata

# Check status
sudo systemctl status suricata
```

---

### 3. Install Python and Dependencies

```bash
# Install Python 3 and pip (if not already installed)
sudo apt install -y python3 python3-pip python3-venv

# Verify installation
python3 --version   # Should be 3.8 or higher
pip3 --version
```

---

### 4. Install Project Dependencies

#### Backend Dependencies

```bash
cd /home/black1hp/IDS/backend
npm install
```

**Required packages (automatically installed):**
- `express` - Web server framework
- `socket.io` - Real-time communication
- `tail` - Log file monitoring
- `cors` - Cross-origin resource sharing

#### Frontend Dependencies

```bash
cd /home/black1hp/IDS/frontend
npm install
```

**Required packages (automatically installed):**
- `react` - UI framework
- `socket.io-client` - WebSocket client
- `lucide-react` - Icon library
- `tailwindcss` - Styling framework

#### ML Detector Dependencies

```bash
cd /home/black1hp/IDS/ml_port_scan_detector

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Required packages (from requirements.txt):**
- `pandas>=1.3.0` - Data manipulation
- `scikit-learn>=0.24.0` - ML algorithms
- `joblib>=1.0.0` - Model loading
- `python-socketio[client]>=5.0.0` - Backend communication
- `xgboost>=1.5.0` - ML model dependency
- `requests>=2.28.0` - HTTP requests
- `websocket-client>=1.0.0` - WebSocket support
- `python-dotenv>=1.0.0` - Environment variables

---

## ⚙️ Configuration

### Suricata Configuration

#### 1. Configure Network Interface

```bash
# Find your network interface
ip addr show

# Edit Suricata configuration
sudo nano /etc/suricata/suricata.yaml
```

**Update these settings:**

```yaml
# Network interface to monitor
af-packet:
  - interface: eth0  # Change to your interface (e.g., ens33, eth0)
    threads: auto
    cluster-id: 99
    cluster-type: cluster_flow
    defrag: yes

# Home network configuration
vars:
  address-groups:
    HOME_NET: "[192.168.1.0/24]"  # Change to your network
    EXTERNAL_NET: "!$HOME_NET"

# Enable EVE JSON logging
outputs:
  - eve-log:
      enabled: yes
      filetype: regular
      filename: /var/log/suricata/eve.json
      types:
        - alert
        - http
        - dns
        - tls
        - flow
        - ssh
```

#### 2. Update Suricata Rules

```bash
# Update rules
sudo suricata-update

# Enable rules
sudo suricata-update enable-source et/open
sudo suricata-update
```

#### 3. Set Log File Permissions

```bash
# Create log directory if not exists
sudo mkdir -p /var/log/suricata

# Set permissions
sudo chmod 755 /var/log/suricata
sudo touch /var/log/suricata/eve.json
sudo chmod 644 /var/log/suricata/eve.json

# Allow your user to read logs
sudo usermod -a -G adm $USER

# Restart Suricata
sudo systemctl restart suricata
```

#### 4. Verify Suricata is Working

```bash
# Check Suricata status
sudo systemctl status suricata

# Monitor logs
sudo tail -f /var/log/suricata/eve.json

# Generate test traffic
ping google.com

# You should see JSON log entries appearing
```

---

### Email Configuration

#### 1. Get Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** (if not already enabled)
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Create new app password:
   - Select app: **Mail**
   - Select device: **Other (Custom name)**
   - Name it: **NIDS Alerts**
5. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

#### 2. Configure Environment Variables

```bash
cd /home/black1hp/IDS/ml_port_scan_detector

# Copy example configuration
cp .env.example .env

# Edit configuration
nano .env
```

**Update .env with your credentials:**

```env
# SMTP Server Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Sender Email (the Gmail account that sends alerts)
SENDER_EMAIL=your-alert-email@gmail.com

# Gmail App Password (16 characters from step 1)
SENDER_PASSWORD=abcd efgh ijkl mnop

# Administrator Email (who receives alerts)
ADMIN_EMAIL=ziad.mohamed.hasan2@gmail.com
```

#### 3. Test Email Configuration

```bash
cd /home/black1hp/IDS/ml_port_scan_detector
source venv/bin/activate
python3 email_alerter.py
```

**Expected output:**
```
Testing email configuration...
✅ Test email sent successfully
Test email sent to: ziad.mohamed.hasan2@gmail.com
```

**Check the admin email inbox for the test message.**

---

## 🎮 Running the Project

### Quick Start (Automated)

**Easiest way - Opens 4 terminals automatically:**

```bash
cd /home/black1hp/IDS
./start_full_system.sh 192.168.138.130
```

⚠️ **Replace `192.168.138.130` with your machine's IP address**

```bash
# Find your IP:
ip addr show | grep "inet " | grep -v 127.0.0.1
```

---

### Manual Start (4 Terminals)

If you prefer manual control, follow these steps in **4 separate terminals**:

#### Terminal 1: Start Backend Server

```bash
cd /home/black1hp/IDS/backend
node index.js
```

**✅ Expected output:**
```
Server running on port 5000
Watching log file: /var/log/suricata/eve.json
WebSocket server ready on port 5000
```

**Keep this terminal open**

---

#### Terminal 2: Start Frontend Dashboard

```bash
cd /home/black1hp/IDS/frontend
npm start
```

**✅ Expected output:**
```
Compiled successfully!

You can now view frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

**Browser automatically opens at http://localhost:3000**

**Keep this terminal open**

---

#### Terminal 3: Start ML Port Scan Detector

```bash
cd /home/black1hp/IDS/ml_port_scan_detector
source venv/bin/activate
python3 integrated_detector.py --target-ip 192.168.138.130
```

⚠️ **Replace `192.168.138.130` with your actual IP**

**✅ Expected output:**
```
============================================================
🛡️  ML-Based Port Scan Detector
============================================================
✅ Successfully loaded ML model and scaler
✅ Connected to backend at http://localhost:5000
📊 Scan threshold: 5 ports in 5 seconds
📁 Log file: /var/log/suricata/eve.json
📧 Email rate limit: 1 email per IP every 6 hours
============================================================
🔍 Monitoring for port scans... (Press Ctrl+C to stop)
```

**Keep this terminal open**

---

#### Terminal 4: Check Suricata (Verification)

```bash
# Verify Suricata is running
sudo systemctl status suricata

# Monitor logs (optional)
sudo tail -f /var/log/suricata/eve.json
```

**✅ Expected:** Status shows "active (running)"

---

## 🧪 Testing

### Test from Another Machine (Kali Linux Recommended)

From your attacker/test machine:

```bash
# Quick port scan test
nmap -sS <target-ip> --top-ports 20

# Aggressive scan
nmap -A <target-ip>

# Full port scan
nmap -p- <target-ip>

# Stealth scan
nmap -sS -T2 <target-ip>
```

**Replace `<target-ip>` with your NIDS machine IP**

---

### Expected Results

#### 1. Terminal 3 (ML Detector) Shows:

```
🚨 [PORT SCAN DETECTED] 🚨
   Source IP: 192.168.1.100
   Target IP: 192.168.138.130
   Ports hit: [21, 22, 80, 443, 8080, 3306, 5432]
   Port count: 7
   ML Confidence: 0.95
   Time: 2024-11-03T20:30:00.000000+00:00

✅ Alert sent to backend
📧 Email alert sent successfully
```

#### 2. Terminal 1 (Backend) Shows:

```
🚨 PORT SCAN ALERT received from ML detector:
   Source: 192.168.1.100 → Target: 192.168.138.130
   Ports: 21, 22, 80, 443, 8080, 3306, 5432 (7 ports)
   Confidence: 0.95
```

#### 3. Browser (http://localhost:3000) Shows:

- 🔔 Security alert notification
- 📊 Real-time network packets in table
- 🚨 Alert details with source/target IP
- 📈 Live traffic statistics

#### 4. Email Inbox (Admin) Shows:

**Subject:** `🚨 PORT SCAN DETECTED - High Severity`

**Body includes:**
- Alert timestamp
- Source IP (attacker)
- Target IP (your machine)
- Ports scanned
- ML confidence score
- Recommended actions

---

## 📧 Email Rate Limiting

To prevent inbox spam from continuous attacks, the system implements **intelligent rate limiting**:

### How It Works

- ✅ **First scan from IP** → Email sent immediately
- 🚫 **Same IP scans again** (within 6 hours) → Email blocked
- ✅ **Different IP scans** → Email sent (separate tracking)
- ✅ **After 6 hours pass** → Email sent again for same IP

### Example Scenario

```
10:00 AM - IP 192.168.1.100 scans → ✅ Email sent
10:15 AM - IP 192.168.1.100 scans → 🚫 Blocked (5.75h remaining)
10:30 AM - IP 192.168.1.200 scans → ✅ Email sent (different IP)
4:00 PM  - IP 192.168.1.100 scans → ✅ Email sent (6h passed)
```

### Console Output During Cooldown

```
🚨 [PORT SCAN DETECTED] 🚨
   Source IP: 192.168.1.100
   ...

✅ Alert sent to backend
⏳ Email cooldown active for 192.168.1.100 (5.3 hours remaining)
   Last email sent: 2024-11-03 10:00:00
```

### Configuration

**Change cooldown period (default: 6 hours):**

Edit `/home/black1hp/IDS/ml_port_scan_detector/integrated_detector.py`:

```python
# Line 25
EMAIL_COOLDOWN = 6 * 60 * 60  # 6 hours in seconds

# Change to:
EMAIL_COOLDOWN = 3 * 60 * 60   # 3 hours
EMAIL_COOLDOWN = 12 * 60 * 60  # 12 hours
EMAIL_COOLDOWN = 30 * 60       # 30 minutes (testing)
```

---

## 🔧 Troubleshooting

### Backend Won't Start (Port 5000 Busy)

```bash
# Check what's using port 5000
sudo lsof -i :5000

# Kill the process
sudo kill -9 <PID>

# Or kill all node processes
pkill -f "node index.js"

# Restart backend
cd /home/black1hp/IDS/backend && node index.js
```

---

### Frontend Won't Start (Port 3000 Busy)

```bash
# Check what's using port 3000
sudo lsof -i :3000

# Kill the process
sudo lsof -ti:3000 | xargs kill -9

# Restart frontend
cd /home/black1hp/IDS/frontend && npm start
```

---

### ML Detector Can't Connect to Backend

```bash
# 1. Ensure backend is running first
curl http://localhost:5000
# Should return: "IDS Backend Running"

# 2. Check backend logs in Terminal 1
# Look for: "Server running on port 5000"

# 3. Restart backend if needed
cd /home/black1hp/IDS/backend && node index.js

# 4. Then restart ML detector
cd /home/black1hp/IDS/ml_port_scan_detector
source venv/bin/activate
python3 integrated_detector.py --target-ip <your-ip>
```

---

### Email Not Sending

```bash
# Test email configuration
cd /home/black1hp/IDS/ml_port_scan_detector
source venv/bin/activate
python3 email_alerter.py

# If fails, check .env file exists
cat .env

# Verify credentials are set
python3 << 'EOF'
from dotenv import load_dotenv
import os
load_dotenv()
print(f"SENDER_EMAIL: {os.getenv('SENDER_EMAIL')}")
print(f"ADMIN_EMAIL: {os.getenv('ADMIN_EMAIL')}")
print(f"SENDER_PASSWORD set: {bool(os.getenv('SENDER_PASSWORD'))}")
EOF

# Common issues:
# - Gmail App Password not generated (need 2FA enabled)
# - Wrong app password (16 characters without spaces)
# - SENDER_EMAIL doesn't match the Google account
```

---

### Suricata Not Running or No Logs

```bash
# Check status
sudo systemctl status suricata

# If stopped, start it
sudo systemctl start suricata

# Check logs
sudo tail -20 /var/log/suricata/suricata.log

# If eve.json doesn't exist
sudo touch /var/log/suricata/eve.json
sudo chmod 644 /var/log/suricata/eve.json

# Fix permissions
sudo chmod 755 /var/log/suricata
sudo chown -R suricata:suricata /var/log/suricata

# Restart Suricata
sudo systemctl restart suricata

# Generate test traffic
ping google.com
curl http://example.com

# Check if logs appear
sudo tail -f /var/log/suricata/eve.json
```

---

### Python Dependencies Missing

```bash
cd /home/black1hp/IDS/ml_port_scan_detector

# Activate virtual environment
source venv/bin/activate

# Reinstall all dependencies
pip install -r requirements.txt

# If specific package fails:
pip install pandas scikit-learn joblib python-socketio xgboost python-dotenv

# Verify installation
pip list
```

---

### Frontend Shows No Data

```bash
# 1. Check backend is running and processing logs
curl http://localhost:5000

# 2. Check Suricata is generating logs
sudo tail -5 /var/log/suricata/eve.json

# 3. Generate some network traffic
ping google.com
curl http://example.com

# 4. Check browser console (F12) for errors

# 5. Verify Socket.IO connection in backend logs
# Should show: "Client connected. Total clients: 1"
```

---

### ML Model Not Found

```bash
# Check model files exist
ls -lh /home/black1hp/IDS/ml_port_scan_detector/*.pkl

# Should show:
# portscan_detector_model.pkl (162 KB)
# scaler.pkl (1.5 KB)

# If missing, you need the trained model files
# Contact project maintainer or retrain the model
```

---

## 📁 Project Structure

```
/home/black1hp/IDS/
├── README.md                          # This file
├── start_full_system.sh               # Automated startup script
├── suricata.yaml                      # Suricata configuration backup
│
├── backend/                           # Node.js Backend Server
│   ├── index.js                       # Main server file
│   ├── logParser.js                   # Suricata log parser
│   ├── package.json                   # Backend dependencies
│   └── node_modules/                  # Installed packages
│
├── frontend/                          # React Frontend Dashboard
│   ├── src/
│   │   ├── App.tsx                    # Main React component
│   │   ├── components/
│   │   │   ├── PacketTable.tsx        # Network packets table
│   │   │   ├── Statistics.tsx         # Traffic statistics
│   │   │   └── SecurityAlerts.tsx     # Alert notifications
│   │   └── types/
│   │       └── packet.ts              # TypeScript types
│   ├── package.json                   # Frontend dependencies
│   └── public/                        # Static files
│
└── ml_port_scan_detector/             # ML Detection System
    ├── integrated_detector.py         # Main ML detector
    ├── email_alerter.py               # Email notification system
    ├── portscan_detector_model.pkl    # Trained ML model
    ├── scaler.pkl                     # Feature scaler
    ├── requirements.txt               # Python dependencies
    ├── .env                           # Email credentials (DO NOT COMMIT)
    ├── .env.example                   # Template for .env
    ├── .gitignore                     # Git ignore rules
    ├── test_rate_limiting.py          # Rate limiting test script
    └── venv/                          # Python virtual environment
```

---

## 🛑 Stopping the System

### Stop All Components

Press `Ctrl+C` in each terminal in this order:

1. **Terminal 3** - ML Detector (cleanly closes Socket.IO connection)
2. **Terminal 2** - Frontend (stops React dev server)
3. **Terminal 1** - Backend (stops Node.js server)

### Stop Suricata (Optional)

```bash
# Stop Suricata service
sudo systemctl stop suricata

# Check status
sudo systemctl status suricata
```

### Kill All Processes (Emergency)

```bash
# Kill all Node.js processes
pkill -f node

# Kill all Python processes
pkill -f python3

# Check ports are free
sudo lsof -i :3000
sudo lsof -i :5000
```

---

## 🌐 Access Points

| Component | URL/Location | Purpose |
|-----------|--------------|---------|
| **Frontend Dashboard** | http://localhost:3000 | Web interface |
| **Backend API** | http://localhost:5000 | Server endpoint |
| **Email Alerts** | ziad.mohamed.hasan2@gmail.com | Admin notifications |
| **Suricata Logs** | /var/log/suricata/eve.json | Network traffic logs |
| **System Logs** | /var/log/suricata/suricata.log | Suricata service logs |

---

## 📊 System Requirements

### Minimum Requirements

- **CPU:** 2 cores
- **RAM:** 4 GB
- **Disk:** 10 GB free space
- **Network:** Ethernet adapter for monitoring

### Recommended Requirements

- **CPU:** 4+ cores
- **RAM:** 8 GB
- **Disk:** 20 GB free space (for logs)
- **Network:** Dedicated network interface for monitoring

---

## 🔒 Security Notes

### Email Credentials

- ⚠️ **Never commit `.env` file to Git** (already in .gitignore)
- ✅ Use Gmail App Passwords, not regular passwords
- ✅ Rotate passwords every 90 days
- ✅ Keep `.env` file permissions secure: `chmod 600 .env`

### Network Security

- 🔒 Run on isolated/monitored network
- 🔒 Keep Suricata rules updated: `sudo suricata-update`
- 🔒 Monitor system logs regularly
- 🔒 Use strong authentication for web dashboard (if deployed to production)

---

## 📖 Additional Information

### Machine Learning Model

- **Algorithm:** Random Forest Classifier
- **Accuracy:** 95%+
- **Features:** 10 network flow features
- **Training Data:** CIC-IDS2017 dataset
- **Detection Threshold:** 5+ ports in 5 seconds

### Supported Protocols

The system classifies 25+ protocols including:

- **Web:** HTTP, HTTPS
- **Email:** SMTP, POP3, IMAP
- **File Transfer:** FTP, SFTP, SMB
- **Database:** MySQL, PostgreSQL, MongoDB
- **Remote Access:** SSH, RDP, Telnet
- **DNS, DHCP, NTP, and more**

---

## 🤝 Contributing

This project is for educational and research purposes. For improvements or bug reports, please document issues clearly.

---

## 📄 License

This project is for academic use. Ensure compliance with local laws when monitoring network traffic.

---

## ✅ Quick Reference Card

### Start System
```bash
cd /home/black1hp/IDS && ./start_full_system.sh <your-ip>
```

### Stop System
Press `Ctrl+C` in all terminals

### Test Detection
```bash
nmap -sS <target-ip> --top-ports 20
```

### Check Status
```bash
# Backend
curl http://localhost:5000

# Suricata
sudo systemctl status suricata

# Logs
sudo tail -f /var/log/suricata/eve.json
```

### Test Email
```bash
cd /home/black1hp/IDS/ml_port_scan_detector
source venv/bin/activate && python3 email_alerter.py
```

---

## 🎉 You're All Set!

Your Network Intrusion Detection System is now configured and ready to protect your network. Monitor the dashboard at **http://localhost:3000** and check **ziad.mohamed.hasan2@gmail.com** for security alerts.

**Happy Monitoring! 🛡️**
