#!/bin/bash

# Start ML Port Scan Detector
echo "🛡️  Starting ML Port Scan Detector..."

cd ml_port_scan_detector

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run the detector
python3 integrated_detector.py --log-file /var/log/suricata/eve.json

deactivate
