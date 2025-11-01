# 🛡️ ML Port Scan Detector - Complete Setup Guide

## 📋 Quick Overview

The ML Port Scan Detector uses a Random Forest machine learning model to detect port scanning attacks in real-time by analyzing Suricata logs.

## 🎯 How It Works

1. **Suricata** captures network traffic → writes to `eve.json`
2. **Python ML Detector** reads logs → detects TCP SYN patterns
3. **ML Model** classifies: Normal traffic vs Port Scan
4. **Alert System** sends notifications to backend
5. **Frontend** displays security alerts (optional)

## 🚀 Complete Setup Commands

### Step 1: Install Python Dependencies

```bash
cd /home/black1hp/IDS/ml_port_scan_detector

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install required packages
pip install -r requirements.txt

# Verify installation
python3 -c "import pandas, sklearn, socketio; print('✅ All packages installed')"
```

### Step 2: Verify ML Model Files

```bash
# Check if model files exist
ls -lh *.pkl

# Expected output:
# portscan_detector_model.pkl (165 KB)
# scaler.pkl (1.5 KB)
```

### Step 3: Make Scripts Executable

```bash
cd /home/black1hp/IDS
chmod +x start-ml-detector.sh
```

### Step 4: Update Backend (Already Done ✅)

The backend has been updated to receive alerts from the ML detector.

## 🎮 Running the Full System

### Terminal 1: Start Backend

```bash
cd /home/black1hp/IDS/backend
npm start
```

**Expected output:**
```
===========================================
NIDS Backend Server running on port 5000
===========================================
Monitoring Suricata log: /var/log/suricata/eve.json
```

### Terminal 2: Start Frontend

```bash
cd /home/black1hp/IDS/frontend
npm run dev
```

**Expected output:**
```
VITE ready in XXX ms
➜  Local:   http://localhost:5173/
```

### Terminal 3: Start ML Port Scan Detector

```bash
cd /home/black1hp/IDS/ml_port_scan_detector
source venv/bin/activate

# Auto-detect target IP (recommended)
python3 integrated_detector.py

# OR specify your machine's IP
python3 integrated_detector.py --target-ip 192.168.138.130
```

**Expected output:**
```
============================================================
🛡️  ML-Based Port Scan Detector
============================================================
✅ Successfully loaded ML model and scaler
✅ Connected to backend at http://localhost:5000
📊 Scan threshold: 5 ports in 5 seconds
📁 Log file: /var/log/suricata/eve.json
============================================================
🔍 Monitoring for port scans... (Press Ctrl+C to stop)
```

## 🧪 Testing the Port Scan Detection

### From Your Kali Machine

#### Test 1: Simple Port Scan (Quick Test)

```bash
# On Kali machine
nmap -sS 192.168.138.130 --top-ports 20
```

**What happens:**
- Kali sends TCP SYN packets to 20 ports
- Suricata captures the traffic
- ML detector identifies the pattern
- Alert appears in all terminals
- Frontend shows notification

#### Test 2: Aggressive Scan

```bash
# Fast and aggressive
nmap -T5 -sS 192.168.138.130 --top-ports 100
```

#### Test 3: Specific Port Range

```bash
# Scan common service ports
nmap -sS -p 21,22,23,25,80,443,3306,3389,5432,8080 192.168.138.130
```

#### Test 4: Stealth Scan

```bash
# Slower stealth scan
nmap -sS -T2 192.168.138.130 -p 1-1000
```

### Test 5: Using Custom Script

Create this on Kali:

```bash
#!/bin/bash
# port_scan_test.sh
TARGET="192.168.138.130"
PORTS=(21 22 23 80 443 3389 5432 8080)

echo "🔍 Testing port scan detection..."
echo "Target: $TARGET"

for PORT in "${PORTS[@]}"; do
    echo "Scanning port $PORT..."
    timeout 1 bash -c "echo >/dev/tcp/$TARGET/$PORT" 2>/dev/null
    sleep 0.2
done

echo "✅ Scan complete. Check detector for alerts."
```

Run it:
```bash
chmod +x port_scan_test.sh
./port_scan_test.sh
```

## 📊 Expected Detection Output

### ML Detector Terminal:

```
🚨 [PORT SCAN DETECTED] 🚨
   Source IP: 192.168.1.100
   Target IP: 192.168.138.130
   Ports hit: [21, 22, 23, 80, 443, 3389, 5432, 8080]
   Port count: 8
   ML Confidence: 0.97
   Time: 2024-11-01T20:30:15.123456

✅ Alert sent to backend
```

### Backend Terminal:

```
🚨 PORT SCAN ALERT received from ML detector:
   Source: 192.168.1.100 → Target: 192.168.138.130
   Ports: 21, 22, 23, 80, 443, 3389, 5432, 8080 (8 ports)
   Confidence: 0.97
```

### Frontend Browser:

A security alert notification should appear (if alert component is implemented).

## 🎯 Complete Test Sequence

Execute these commands in order:

```bash
# ============================================
# SETUP (One-time)
# ============================================

# 1. Install Python dependencies
cd /home/black1hp/IDS/ml_port_scan_detector
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Verify everything is ready
ls -lh *.pkl  # Check ML models
python3 -c "import pandas, sklearn, socketio; print('✅ Ready')"

# ============================================
# RUN THE SYSTEM
# ============================================

# Terminal 1: Backend
cd /home/black1hp/IDS/backend
npm start

# Terminal 2: Frontend  
cd /home/black1hp/IDS/frontend
npm run dev

# Terminal 3: ML Detector
cd /home/black1hp/IDS/ml_port_scan_detector
source venv/bin/activate
python3 integrated_detector.py --target-ip 192.168.138.130

# ============================================
# TEST FROM KALI MACHINE
# ============================================

# On your Kali machine:
nmap -sS 192.168.138.130 --top-ports 20

# OR for more aggressive test:
nmap -T5 -sS 192.168.138.130 --top-ports 50

# ============================================
# VERIFY DETECTION
# ============================================

# You should see alerts in:
# 1. ML Detector terminal (Terminal 3)
# 2. Backend terminal (Terminal 1)
# 3. Browser at http://localhost:5173 (if alert UI added)
```

## 🐛 Troubleshooting

### Issue: "Module not found" errors

```bash
cd /home/black1hp/IDS/ml_port_scan_detector
source venv/bin/activate
pip install pandas scikit-learn joblib python-socketio
```

### Issue: "Cannot connect to backend"

**Check:**
1. Is backend running? `curl http://localhost:5000/api/health`
2. Is port 5000 free? `lsof -i:5000`

**Solution:**
```bash
# Kill existing backend
pkill -f "node index.js"

# Restart backend
cd /home/black1hp/IDS/backend
npm start
```

### Issue: "Log file not found"

**Check:**
```bash
ls -l /var/log/suricata/eve.json
```

**Solution:**
```bash
# Use test mode instead
python3 integrated_detector.py --test

# Or specify different log file
python3 integrated_detector.py --log-file /path/to/eve.json
```

### Issue: No detections when scanning

**Checklist:**
1. ✅ Is Suricata running? `sudo systemctl status suricata`
2. ✅ Is target IP correct? Check with `ip addr`
3. ✅ Are you scanning from different machine?
4. ✅ Is scan hitting enough ports? Try 10+ ports
5. ✅ Is scan fast enough? Use `-T4` or `-T5`

**Debug:**
```bash
# Watch Suricata logs in real-time
tail -f /var/log/suricata/eve.json | grep -i syn

# Check if traffic is being captured
sudo tcpdump -i any tcp and port 80
```

### Issue: Too many false positives

**Solution:** Adjust threshold in `integrated_detector.py`:

```python
scan_threshold = 10  # Increase from 5 to 10
time_interval = 10   # Increase window to 10 seconds
```

## 📈 Performance Tips

### For High Traffic Networks

```python
# Edit integrated_detector.py
scan_threshold = 15  # Higher threshold
time_interval = 10   # Longer window
```

### For Sensitive Detection

```python
scan_threshold = 3   # Lower threshold (more sensitive)
time_interval = 3    # Shorter window
```

## 🔧 Advanced Configuration

### Monitor Multiple IPs

Run separate instances:

```bash
# Terminal A
python3 integrated_detector.py --target-ip 192.168.138.130

# Terminal B  
python3 integrated_detector.py --target-ip 192.168.138.131
```

### Custom Backend URL

```bash
python3 integrated_detector.py --backend-url http://192.168.1.100:5000
```

### Save Logs to File

```bash
python3 integrated_detector.py 2>&1 | tee ml_detector.log
```

## 📝 Summary of Files

| File | Purpose |
|------|---------|
| `portscan_detector_model.pkl` | Trained ML model |
| `scaler.pkl` | Feature normalization |
| `integrated_detector.py` | Main detector with backend integration |
| `ml_portscan_detector.py` | Standalone detector |
| `requirements.txt` | Python dependencies |
| `README.md` | Detailed documentation |

## 🎓 Understanding the ML Model

### Features Used
- Packets per second (most important)
- Total packet count
- Flow duration
- Byte counts
- Packet lengths

### Detection Logic
```
IF (unique_ports >= 5 in 5 seconds)
AND (ML_model_predicts = SCAN)
THEN Alert!
```

### Confidence Score
- **0.0 - 0.5**: Probably normal
- **0.5 - 0.7**: Suspicious
- **0.7 - 0.9**: Likely scan
- **0.9 - 1.0**: Definitely scan

## 🚦 System Status Check

Run this to verify everything:

```bash
#!/bin/bash
echo "=== System Status Check ==="

# 1. Check backend
echo -n "Backend: "
curl -s http://localhost:5000/api/health > /dev/null && echo "✅ Running" || echo "❌ Not running"

# 2. Check frontend
echo -n "Frontend: "
curl -s http://localhost:5173 > /dev/null && echo "✅ Running" || echo "❌ Not running"

# 3. Check Suricata
echo -n "Suricata: "
sudo systemctl is-active suricata > /dev/null && echo "✅ Running" || echo "❌ Not running"

# 4. Check eve.json
echo -n "Suricata Logs: "
[ -f /var/log/suricata/eve.json ] && echo "✅ Exists" || echo "❌ Not found"

# 5. Check ML models
echo -n "ML Models: "
[ -f /home/black1hp/IDS/ml_port_scan_detector/*.pkl ] && echo "✅ Found" || echo "❌ Not found"

echo "======================="
```

## 🎉 Success Criteria

You'll know it's working when:

1. ✅ ML detector shows "Connected to backend"
2. ✅ Running nmap from Kali triggers alert
3. ✅ Alert appears in ML detector terminal
4. ✅ Backend receives and logs the alert
5. ✅ Detection happens within 1-2 seconds

## 📚 Next Steps

After successful detection:
1. Tune thresholds for your network
2. Add frontend alert notifications
3. Implement alert logging
4. Add email notifications
5. Create alert dashboard

---

**Ready to detect port scans!** 🚀
