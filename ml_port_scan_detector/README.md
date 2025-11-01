# ML-Based Port Scan Detector

Machine Learning powered port scan detection system that integrates with Suricata IDS and the NIDS backend.

## How It Works

### Detection Algorithm

1. **Monitor TCP SYN Packets**: Watches for TCP SYN packets (connection initiation)
2. **Track Source IPs**: Maintains a sliding window of connection attempts per source IP
3. **Count Unique Ports**: Counts distinct destination ports accessed within time window
4. **ML Classification**: Uses Random Forest model to classify behavior as scan vs. normal
5. **Alert Generation**: Sends alerts to backend when port scan detected

### ML Model Features

The model analyzes these features:
- **Flow Duration**: Connection duration
- **Packet Count**: Total forward/backward packets
- **Packet Rate**: Packets per second (key indicator)
- **Byte Counts**: Data transferred
- **Flow Characteristics**: Statistical features

### Detection Thresholds

- **Scan Threshold**: 5+ unique ports accessed
- **Time Window**: 5 seconds
- **Protocol**: TCP only
- **Trigger**: SYN packets (port probing)

## Files

- `portscan_detector_model.pkl` - Trained Random Forest model
- `scaler.pkl` - Feature scaler for normalization
- `ml_portscan_detector.py` - Standalone detector (original)
- `integrated_detector.py` - Integrated with backend via Socket.IO
- `requirements.txt` - Python dependencies

## Installation

### 1. Install Python Dependencies

```bash
cd /home/black1hp/IDS/ml_port_scan_detector

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Verify Model Files

```bash
ls -lh *.pkl
# Should show:
# portscan_detector_model.pkl (165 KB)
# scaler.pkl (1.5 KB)
```

## Usage

### Option 1: Integrated Mode (Recommended)

Connects to Node.js backend and sends alerts in real-time:

```bash
# Activate virtual environment
source venv/bin/activate

# Run with auto-detection of target IP
python3 integrated_detector.py

# Run with specific target IP
python3 integrated_detector.py --target-ip 192.168.138.130

# Run with custom log file
python3 integrated_detector.py --log-file /var/log/suricata/eve.json

# Test mode (with sample data)
python3 integrated_detector.py --test
```

### Option 2: Standalone Mode

Original detector that prints alerts to console:

```bash
source venv/bin/activate

# Monitor live logs
python3 ml_portscan_detector.py --log-file /var/log/suricata/eve.json --target-ip 192.168.138.130

# Test with sample data
python3 ml_portscan_detector.py --test-sample

# Batch process existing log
python3 ml_portscan_detector.py --log-file /path/to/eve.json --batch-process
```

## Testing Port Scan Detection

### From Your Kali Machine

#### 1. SYN Scan (Stealth Scan)
```bash
# Scan top 100 ports
nmap -sS 192.168.138.130 --top-ports 100

# Scan specific ports
nmap -sS -p 1-1000 192.168.138.130

# Fast scan
nmap -sS -T4 192.168.138.130
```

#### 2. TCP Connect Scan
```bash
# Full TCP connection scan
nmap -sT 192.168.138.130 -p 1-1000
```

#### 3. Aggressive Scan
```bash
# Service detection + OS detection
nmap -A 192.168.138.130

# Fast aggressive scan
nmap -T5 -A 192.168.138.130 --top-ports 50
```

#### 4. Version Detection
```bash
# Detect service versions
nmap -sV 192.168.138.130 -p 80,443,22,21,3389
```

#### 5. Custom Port Scan Script
```bash
#!/bin/bash
# scan_test.sh - Simple port scanner for testing
TARGET="192.168.138.130"
PORTS=(21 22 23 25 80 443 3306 3389 5432 8080)

for PORT in "${PORTS[@]}"; do
    timeout 1 bash -c "echo >/dev/tcp/$TARGET/$PORT" 2>/dev/null && \
        echo "Port $PORT: Open" || echo "Port $PORT: Closed"
done
```

### Expected Results

When you run a port scan from Kali:

1. **ML Detector Console Output**:
```
🚨 [PORT SCAN DETECTED] 🚨
   Source IP: 192.168.1.200
   Target IP: 192.168.138.130
   Ports hit: [21, 22, 80, 443, 3389]
   Port count: 5
   ML Confidence: 0.95
   Time: 2024-11-01T20:10:15.123456
```

2. **Backend Console Output**:
```
🚨 PORT SCAN ALERT received from ML detector:
   Source: 192.168.1.200 → Target: 192.168.138.130
   Ports: 21, 22, 80, 443, 3389 (5 ports)
   Confidence: 0.95
```

3. **Frontend UI**: Alert notification appears (if implemented)

## Architecture

```
┌─────────────────────┐
│   Attacker (Kali)   │
│   Port Scanning     │
└──────────┬──────────┘
           │ TCP SYN packets
           ▼
┌─────────────────────┐
│   Suricata IDS      │
│   Captures traffic  │
└──────────┬──────────┘
           │ Writes to eve.json
           ▼
┌─────────────────────┐
│  ML Port Scanner    │
│  (Python)           │
│  - Parses logs      │
│  - Tracks SYN pkts  │
│  - ML prediction    │
└──────────┬──────────┘
           │ Socket.IO
           ▼
┌─────────────────────┐
│  Backend Server     │
│  (Node.js)          │
└──────────┬──────────┘
           │ WebSocket
           ▼
┌─────────────────────┐
│  Frontend UI        │
│  (React)            │
└─────────────────────┘
```

## Configuration

### Detector Settings

Edit `integrated_detector.py`:

```python
scan_threshold = 5  # Ports hit to trigger detection
time_interval = 5   # Time window in seconds
BACKEND_URL = "http://localhost:5000"
```

### ML Model

The model was trained on network traffic data with:
- **Algorithm**: Random Forest Classifier
- **Features**: 10 flow-based features
- **Classes**: Normal (0) vs Port Scan (1)
- **Accuracy**: ~95%+ on test data

## Troubleshooting

### Issue: Model not loading

**Solution**:
```bash
ls -lh ml_port_scan_detector/*.pkl
# Verify files exist and are readable
```

### Issue: Cannot connect to backend

**Error**: `Could not connect to backend`

**Solution**:
1. Ensure backend is running: `cd backend && npm start`
2. Check backend URL in script
3. Detector will still work and print alerts to console

### Issue: No detections

**Check**:
1. Is Suricata capturing traffic? `tail -f /var/log/suricata/eve.json`
2. Is target IP correct? Check with `--target-ip` flag
3. Are you scanning enough ports? Try `nmap -p 1-100`
4. Is scan fast enough? Use `-T4` or `-T5` in nmap

### Issue: Too many false positives

**Solution**: Increase threshold:
```python
scan_threshold = 10  # Require more ports
```

## Performance

- **CPU Usage**: < 5% (idle), 10-20% (during scan)
- **Memory**: ~50-100 MB
- **Latency**: < 100ms detection time
- **Throughput**: Can process 1000+ events/sec

## Security Notes

1. **ML Model**: Pre-trained, not updated in real-time
2. **Evasion**: Slow scans (<5 ports/5sec) may evade detection
3. **False Positives**: Legitimate services may trigger alerts
4. **Target IP**: Must be your machine's IP for accurate detection

## Advanced Usage

### Multiple Target IPs

Run multiple instances:
```bash
# Terminal 1
python3 integrated_detector.py --target-ip 192.168.138.130

# Terminal 2
python3 integrated_detector.py --target-ip 192.168.138.131
```

### Custom Backend URL

```bash
python3 integrated_detector.py --backend-url http://192.168.1.100:5000
```

### Logging to File

```bash
python3 integrated_detector.py 2>&1 | tee detector.log
```

## Future Enhancements

- [ ] Multi-target monitoring
- [ ] Adaptive thresholds
- [ ] Alert rate limiting
- [ ] Historical analysis
- [ ] Model retraining
- [ ] UDP scan detection
- [ ] Distributed scanning detection

## License

Part of the Network Intrusion Detection System (NIDS) project.
