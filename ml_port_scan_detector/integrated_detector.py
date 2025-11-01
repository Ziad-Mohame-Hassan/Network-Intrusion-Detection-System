#!/usr/bin/env python3
"""
Integrated ML Port Scan Detector
Connects to the Node.js backend via Socket.IO to send real-time alerts
"""

import json
import time
import pandas as pd
import joblib
import socketio
import os
import sys
from collections import defaultdict
from datetime import datetime
import argparse

# Configuration
target_ip = None  # Will be set via args or auto-detect
scan_threshold = 5  # SYN packets to distinct ports
time_interval = 5  # seconds
BACKEND_URL = "http://localhost:5000"

# Globals
connection_attempts = defaultdict(list)
model = None
scaler = None
sio = socketio.Client()

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, "portscan_detector_model.pkl")
SCALER_PATH = os.path.join(SCRIPT_DIR, "scaler.pkl")

def load_model_and_scaler():
    """Load the ML model and scaler"""
    global model, scaler
    try:
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        print(f"✅ Successfully loaded ML model and scaler")
        return True
    except FileNotFoundError:
        print(f"❌ Error: Model or scaler not found in {SCRIPT_DIR}")
        return False
    except Exception as e:
        print(f"❌ Error loading model/scaler: {e}")
        return False

def connect_to_backend():
    """Connect to the Node.js backend"""
    try:
        sio.connect(BACKEND_URL)
        print(f"✅ Connected to backend at {BACKEND_URL}")
        return True
    except Exception as e:
        print(f"⚠️  Could not connect to backend: {e}")
        print(f"⚠️  Alerts will be printed to console only")
        return False

def send_alert(src_ip, target_ip, ports_hit, prediction_confidence=1.0):
    """Send port scan alert to backend"""
    alert_data = {
        'type': 'port_scan',
        'timestamp': datetime.utcnow().isoformat(),
        'source_ip': src_ip,
        'target_ip': target_ip,
        'ports_scanned': ports_hit,
        'port_count': len(ports_hit),
        'confidence': float(prediction_confidence),
        'severity': 'HIGH'
    }
    
    # Print to console
    print(f"\n🚨 [PORT SCAN DETECTED] 🚨")
    print(f"   Source IP: {src_ip}")
    print(f"   Target IP: {target_ip}")
    print(f"   Ports hit: {ports_hit}")
    print(f"   Port count: {len(ports_hit)}")
    print(f"   ML Confidence: {prediction_confidence:.2f}")
    print(f"   Time: {alert_data['timestamp']}\n")
    
    # Send to backend if connected
    if sio.connected:
        try:
            sio.emit('port_scan_alert', alert_data)
            print("✅ Alert sent to backend")
        except Exception as e:
            print(f"⚠️  Failed to send alert to backend: {e}")

def build_features(src_ip):
    """Build features for ML model"""
    attempts_in_window = connection_attempts[src_ip]
    packet_count = len(attempts_in_window)
    pps = packet_count / time_interval if time_interval > 0 else 0

    features = {
        'Flow Duration': 0,
        'Total Fwd Packets': packet_count,
        'Total Backward Packets': 0,
        'Total Length of Fwd Packets': 0,
        'Total Length of Bwd Packets': 0,
        'Fwd Packet Length Max': 0,
        'Bwd Packet Length Max': 0,
        'Fwd Packet Length Min': 0,
        'Flow Bytes/s': 0,
        'Flow Packets/s': pps
    }
    
    df = pd.DataFrame([features])
    if scaler:
        try:
            return scaler.transform(df)
        except Exception as e:
            print(f"⚠️  Error scaling features: {e}")
            return df.values
    return df.values

def parse_eve_timestamp(timestamp_str):
    """Parse Suricata timestamp"""
    try:
        dt_obj = datetime.fromisoformat(timestamp_str.replace("+0000", "+00:00"))
        return dt_obj.timestamp()
    except:
        return time.time()

def process_eve_event(eve_line_str):
    """Process a single Suricata EVE event"""
    global connection_attempts, target_ip
    
    try:
        event = json.loads(eve_line_str)
    except:
        return

    timestamp_str = event.get("timestamp")
    if not timestamp_str:
        return
    
    current_timestamp = parse_eve_timestamp(timestamp_str)
    
    src_ip_evt = event.get("src_ip")
    dest_ip_evt = event.get("dest_ip")
    dest_port_evt = event.get("dest_port")
    proto_evt = event.get("proto")

    # Filter: Only TCP traffic to target IP
    if proto_evt != "TCP" or not src_ip_evt or not dest_port_evt:
        return
    
    # If target_ip not set, use the first dest_ip we see
    if target_ip is None:
        target_ip = dest_ip_evt
        print(f"🎯 Auto-detected target IP: {target_ip}")
    
    if dest_ip_evt != target_ip:
        return

    # Check for SYN packet
    is_syn_packet = False
    event_type = event.get("event_type")
    tcp_info = event.get("tcp", {})
    
    if event_type == "flow":
        if tcp_info.get("syn") or "S" in tcp_info.get("tcp_flags_ts", ""):
            is_syn_packet = True
    elif event_type == "alert":
        if tcp_info.get("syn") or "S" in tcp_info.get("tcp_flags", ""):
            is_syn_packet = True
    
    if not is_syn_packet:
        return

    # Clean old entries outside time window
    connection_attempts[src_ip_evt] = [
        (p, t) for p, t in connection_attempts[src_ip_evt]
        if t > current_timestamp - time_interval
    ]
    
    # Add new attempt
    connection_attempts[src_ip_evt].append((dest_port_evt, current_timestamp))

    # Check if threshold exceeded
    if len(connection_attempts[src_ip_evt]) >= scan_threshold:
        features_scaled = build_features(src_ip_evt)
        prediction = 0
        confidence = 0.0
        
        if model and scaler:
            try:
                prediction = model.predict(features_scaled)[0]
                # Try to get prediction probability if available
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(features_scaled)[0]
                    confidence = proba[1] if len(proba) > 1 else proba[0]
                else:
                    confidence = 1.0 if prediction == 1 else 0.0
            except Exception as e:
                print(f"⚠️  Prediction error: {e}")

        if prediction == 1:
            ports_hit = sorted(list(set([p for p, t in connection_attempts[src_ip_evt]])))
            send_alert(src_ip_evt, target_ip, ports_hit, confidence)
            connection_attempts[src_ip_evt] = []

def follow(thefile):
    """Tail a file"""
    thefile.seek(0, os.SEEK_END)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def main():
    global target_ip
    
    parser = argparse.ArgumentParser(description="ML Port Scan Detector with Backend Integration")
    parser.add_argument("--log-file", default="/var/log/suricata/eve.json",
                       help="Path to Suricata EVE log file (default: /var/log/suricata/eve.json)")
    parser.add_argument("--target-ip", help="Target IP to monitor (auto-detect if not specified)")
    parser.add_argument("--backend-url", default=BACKEND_URL,
                       help=f"Backend URL (default: {BACKEND_URL})")
    parser.add_argument("--threshold", type=int, default=scan_threshold,
                       help=f"Scan threshold (default: {scan_threshold})")
    parser.add_argument("--test", action="store_true", help="Run with test data")
    
    args = parser.parse_args()
    
    if args.target_ip:
        target_ip = args.target_ip
        print(f"🎯 Monitoring target IP: {target_ip}")
    
    print("="*60)
    print("🛡️  ML-Based Port Scan Detector")
    print("="*60)
    
    # Load ML model
    if not load_model_and_scaler():
        print("❌ Cannot proceed without ML model")
        return 1
    
    # Connect to backend
    connect_to_backend()
    
    print(f"📊 Scan threshold: {args.threshold} ports in {time_interval} seconds")
    print(f"📁 Log file: {args.log_file}")
    print("="*60)
    print("🔍 Monitoring for port scans... (Press Ctrl+C to stop)\n")
    
    if args.test:
        print("🧪 Running test mode with sample data\n")
        test_logs = [
            '{"timestamp": "2024-11-01T20:00:00.000000+0000", "event_type": "flow", "src_ip": "192.168.1.200", "dest_ip": "192.168.138.130", "dest_port": 80, "proto": "TCP", "tcp": {"syn": true, "tcp_flags_ts": "S"}}',
            '{"timestamp": "2024-11-01T20:00:00.500000+0000", "event_type": "flow", "src_ip": "192.168.1.200", "dest_ip": "192.168.138.130", "dest_port": 443, "proto": "TCP", "tcp": {"syn": true, "tcp_flags_ts": "S"}}',
            '{"timestamp": "2024-11-01T20:00:01.000000+0000", "event_type": "flow", "src_ip": "192.168.1.200", "dest_ip": "192.168.138.130", "dest_port": 22, "proto": "TCP", "tcp": {"syn": true, "tcp_flags_ts": "S"}}',
            '{"timestamp": "2024-11-01T20:00:02.000000+0000", "event_type": "flow", "src_ip": "192.168.1.200", "dest_ip": "192.168.138.130", "dest_port": 21, "proto": "TCP", "tcp": {"syn": true, "tcp_flags_ts": "S"}}',
            '{"timestamp": "2024-11-01T20:00:03.000000+0000", "event_type": "flow", "src_ip": "192.168.1.200", "dest_ip": "192.168.138.130", "dest_port": 8080, "proto": "TCP", "tcp": {"syn": true, "tcp_flags_ts": "S"}}',
        ]
        for log in test_logs:
            process_eve_event(log)
            time.sleep(0.2)
        print("\n✅ Test completed")
        return 0
    
    try:
        with open(args.log_file, 'r') as f:
            for line in follow(f):
                process_eve_event(line)
    except FileNotFoundError:
        print(f"❌ Log file not found: {args.log_file}")
        return 1
    except KeyboardInterrupt:
        print("\n\n✋ Stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        if sio.connected:
            sio.disconnect()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
