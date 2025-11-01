# 🚀 NIDS with ML Port Scan Detection - Quick Start

## 📦 One-Time Setup

```bash
# 1. Install Backend Dependencies
cd /home/black1hp/IDS/backend
npm install

# 2. Install Frontend Dependencies  
cd /home/black1hp/IDS/frontend
npm install

# 3. Install ML Detector Dependencies
cd /home/black1hp/IDS/ml_port_scan_detector
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# 4. Make scripts executable
cd /home/black1hp/IDS
chmod +x start-ml-detector.sh
```

## 🎯 Run Complete System (3 Terminals)

### Terminal 1: Backend Server
```bash
cd /home/black1hp/IDS/backend
npm start
```

### Terminal 2: Frontend UI
```bash
cd /home/black1hp/IDS/frontend
npm run dev
```

### Terminal 3: ML Port Scan Detector
```bash
cd /home/black1hp/IDS/ml_port_scan_detector
source venv/bin/activate
python3 integrated_detector.py --target-ip 192.168.138.130
```

**Access UI:** http://localhost:5173

---

## 🧪 Test Port Scan Detection from Kali

### Quick Test (Recommended)
```bash
nmap -sS 192.168.138.130 --top-ports 20
```

### Aggressive Test
```bash
nmap -T5 -sS 192.168.138.130 --top-ports 50
```

### Specific Ports
```bash
nmap -sS -p 21,22,23,80,443,3389,5432,8080 192.168.138.130
```

### Full Scan
```bash
nmap -A -T4 192.168.138.130 --top-ports 100
```

---

## ✅ Verify Detection

After running nmap, you should see:

**Terminal 3 (ML Detector):**
```
🚨 [PORT SCAN DETECTED] 🚨
   Source IP: <kali-ip>
   Target IP: 192.168.138.130
   Ports hit: [21, 22, 80, 443, ...]
   ML Confidence: 0.95
```

**Terminal 1 (Backend):**
```
🚨 PORT SCAN ALERT received from ML detector
```

---

## 🛑 Stop All Services

```bash
# Press Ctrl+C in each terminal

# Or kill all at once:
pkill -f "node index.js"
pkill -f "npm run dev"  
pkill -f "integrated_detector"
```

---

## 📋 System Status Check

```bash
# Check backend
curl http://localhost:5000/api/health

# Check Suricata
sudo systemctl status suricata

# Check logs
tail -5 /var/log/suricata/eve.json
```

---

## 🔧 Common Issues

### ML Detector won't start
```bash
cd /home/black1hp/IDS/ml_port_scan_detector
source venv/bin/activate
pip install -r requirements.txt
```

### Backend port in use
```bash
pkill -f "node index.js"
cd /home/black1hp/IDS/backend
npm start
```

### No detections
1. Verify target IP: `ip addr | grep inet`
2. Check Suricata: `sudo systemctl status suricata`
3. Scan more ports: `nmap -sS <target> --top-ports 50`

---

## 📁 Important Files

- **Backend:** `/home/black1hp/IDS/backend/`
- **Frontend:** `/home/black1hp/IDS/frontend/`
- **ML Detector:** `/home/black1hp/IDS/ml_port_scan_detector/`
- **Suricata Logs:** `/var/log/suricata/eve.json`
- **ML Models:** `*.pkl` files in ml_port_scan_detector/

---

## 🎓 What Each Component Does

| Component | Purpose | Port |
|-----------|---------|------|
| **Backend** | Processes Suricata logs, receives ML alerts | 5000 |
| **Frontend** | Web UI for visualizing traffic | 5173 |
| **ML Detector** | Detects port scans using ML | - |
| **Suricata** | Captures network traffic | - |

---

**Ready to detect attacks!** 🛡️
