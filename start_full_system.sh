#!/bin/bash

# Full IDS System Startup Script
# Run each component in a separate terminal

echo "========================================"
echo "🛡️  Network IDS - Full System Startup"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if target IP is provided
if [ -z "$1" ]; then
    echo -e "${YELLOW}⚠️  Usage: $0 <target-ip>${NC}"
    echo "   Example: $0 192.168.138.130"
    exit 1
fi

TARGET_IP=$1

echo -e "${BLUE}📌 Target IP: ${TARGET_IP}${NC}"
echo ""

# Function to open terminal and run command
open_terminal() {
    local title=$1
    local command=$2
    
    # Try different terminal emulators
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal --title="$title" -- bash -c "$command; exec bash"
    elif command -v xterm &> /dev/null; then
        xterm -T "$title" -e "$command; bash" &
    elif command -v konsole &> /dev/null; then
        konsole --new-tab -e bash -c "$command; exec bash" &
    else
        echo -e "${YELLOW}⚠️  No supported terminal found. Please run manually.${NC}"
        return 1
    fi
}

echo -e "${GREEN}1️⃣  Checking Suricata...${NC}"
if ! sudo systemctl is-active --quiet suricata; then
    echo "   Starting Suricata..."
    sudo systemctl start suricata
    sleep 2
fi
echo "   ✅ Suricata is running"
echo ""

echo -e "${GREEN}2️⃣  Starting Node.js Backend...${NC}"
open_terminal "IDS Backend" "cd /home/black1hp/IDS/backend && node index.js"
echo "   ✅ Backend terminal opened"
sleep 2
echo ""

echo -e "${GREEN}3️⃣  Starting React Frontend...${NC}"
open_terminal "IDS Frontend" "cd /home/black1hp/IDS/frontend && npm start"
echo "   ✅ Frontend terminal opened"
sleep 2
echo ""

echo -e "${GREEN}4️⃣  Starting ML Port Scan Detector...${NC}"
open_terminal "ML Detector" "cd /home/black1hp/IDS/ml_port_scan_detector && source venv/bin/activate && python3 integrated_detector.py --target-ip ${TARGET_IP}"
echo "   ✅ ML Detector terminal opened"
echo ""

echo "========================================"
echo -e "${GREEN}✅ All components started!${NC}"
echo "========================================"
echo ""
echo "🌐 Access points:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:5000"
echo ""
echo "📧 Email alerts: ziad.mohamed.hasan2@gmail.com"
echo "⏱️  Rate limit: 1 email per IP every 6 hours"
echo ""
echo "🛑 To stop all components:"
echo "   - Close all terminal windows"
echo "   - Or press Ctrl+C in each terminal"
echo ""
