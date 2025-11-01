# Network Intrusion Detection System - Setup Guide

## System Overview

This NIDS consists of two main components:
1. **Backend Server** - Processes Suricata EVE logs and streams data via Socket.IO
2. **Frontend Application** - React-based UI for visualizing network traffic

## Architecture

```
┌─────────────────────┐
│   Suricata IDS      │
│   Monitors Network  │
└──────────┬──────────┘
           │ Writes logs
           ▼
┌─────────────────────┐
│  /var/log/suricata/ │
│     eve.json        │
└──────────┬──────────┘
           │ Tailed by
           ▼
┌─────────────────────┐
│  Backend Server     │
│  (Node.js/Express)  │
│  Port: 5000         │
└──────────┬──────────┘
           │ Socket.IO
           ▼
┌─────────────────────┐
│  Frontend UI        │
│  (React/Vite)       │
│  Port: 5173         │
└─────────────────────┘
```

## Installation Steps

### 1. Install Backend

```bash
cd /home/black1hp/IDS/backend
npm install
```

**Dependencies installed:**
- `express` - Web server framework
- `socket.io` - Real-time communication
- `cors` - Cross-origin resource sharing
- `tail` - File watching library

### 2. Install Frontend

```bash
cd /home/black1hp/IDS/frontend
npm install
```

**Dependencies installed:**
- `react` - UI framework
- `socket.io-client` - WebSocket client
- `tailwindcss` - CSS framework
- `lucide-react` - Icons
- `date-fns` - Date formatting

### 3. Configure Backend

Edit `/home/black1hp/IDS/backend/config.js`:

```javascript
module.exports = {
  PORT: 5000,
  EVE_LOG_PATH: '/var/log/suricata/eve.json',
  CORS_ORIGIN: 'http://localhost:5173',
  MAX_PACKETS_IN_MEMORY: 100,
  BATCH_SIZE: 10,
  BATCH_INTERVAL_MS: 1000
};
```

**Environment Variables (Optional):**
```bash
export PORT=5000
export EVE_LOG_PATH=/var/log/suricata/eve.json
export CORS_ORIGIN=http://localhost:5173
```

## Running the System

### Option 1: Using Shell Scripts

**Terminal 1 - Start Backend:**
```bash
cd /home/black1hp/IDS
./start-backend.sh
```

**Terminal 2 - Start Frontend:**
```bash
cd /home/black1hp/IDS
./start-frontend.sh
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd /home/black1hp/IDS/backend
npm start
```

Expected output:
```
===========================================
NIDS Backend Server running on port 5000
===========================================
Health check: http://localhost:5000/api/health
Stats: http://localhost:5000/api/stats
===========================================
Monitoring Suricata log: /var/log/suricata/eve.json
Log watcher initialized successfully
```

**Terminal 2 - Frontend:**
```bash
cd /home/black1hp/IDS/frontend
npm run dev
```

Expected output:
```
VITE ready in XXX ms
➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### Accessing the Application

Open your browser and navigate to:
```
http://localhost:5173
```

## Connecting to Suricata

### Check Suricata Status

```bash
sudo systemctl status suricata
```

### Verify Log File

```bash
sudo ls -l /var/log/suricata/eve.json
```

### Grant Permissions (if needed)

```bash
sudo chmod +r /var/log/suricata/eve.json
```

### Start Suricata (if not running)

```bash
sudo systemctl start suricata
```

## Testing Without Suricata

The system includes sample logs for testing. The backend will automatically use the sample log file if the main Suricata log is not found:

1. Backend detects `/var/log/suricata/eve.json` doesn't exist
2. Falls back to `../sample eve.log`
3. Parses existing log entries

**Current sample log location:**
```
/home/black1hp/IDS/sample eve.log
```

The sample file contains real Suricata EVE JSON logs captured from network traffic.

## Data Flow

### 1. Log Parsing

The backend's `logParser.js` processes each log line:

```javascript
{
  "timestamp": "2025-11-01T17:19:31.594498+0200",
  "event_type": "dns",
  "src_ip": "192.168.138.130",
  "src_port": 49492,
  "dest_ip": "192.168.138.2",
  "dest_port": 53,
  "proto": "UDP",
  "app_proto": "dns"
}
```

### 2. Packet Transformation

Transformed into frontend-compatible format:

```javascript
{
  id: "uuid",
  timestamp: Date,
  sourceIP: "192.168.138.130",
  sourcePort: 49492,
  destinationIP: "192.168.138.2",
  destinationPort: 53,
  protocol: "UDP",
  application_protocol: "DNS",
  size: 64,
  isSuspicious: false,
  activity: "DNS Query",
  risk_level: "LOW",
  features: {...}
}
```

### 3. Real-time Streaming

- Backend emits `new_packet` event via Socket.IO
- Frontend's `usePackets` hook receives the packet
- React updates the UI instantly
- Maximum 100 packets kept in memory

## API Endpoints

### Health Check
```bash
GET http://localhost:5000/api/health
```

Response:
```json
{
  "status": "ok",
  "clients": 1,
  "timestamp": "2025-11-01T15:44:00.000Z"
}
```

### Statistics
```bash
GET http://localhost:5000/api/stats
```

Response:
```json
{
  "connected_clients": 1,
  "buffer_size": 10,
  "log_path": "/var/log/suricata/eve.json"
}
```

## Frontend Features

### Filtering Options

1. **Protocol Filter**: Filter by TCP, UDP, HTTP, HTTPS, DNS, etc.
2. **Status Filter**: Show only suspicious packets
3. **Search**: Search by source or destination IP

### Table Columns

- **Time**: HH:mm:ss.SSS format
- **Source Port**: Origin port number
- **Dest Port**: Destination port number
- **Source IP**: Origin IP address
- **Dest IP**: Destination IP address
- **Protocol**: Application protocol badge
- **Activity**: Activity type with icon
- **Size**: Bytes and packet rate
- **Risk Level**: Color-coded badge (GREEN/YELLOW/RED)
- **Status**: Normal or Suspicious indicator

## Troubleshooting

### Backend Won't Start

**Error:** `Error: ENOENT: no such file or directory`
- **Solution:** Check EVE_LOG_PATH in config.js

**Error:** `Error: listen EADDRINUSE`
- **Solution:** Port 5000 is already in use, change PORT in config.js

### Frontend Won't Connect

**Symptom:** "Disconnected" status in header
- **Solution:** Ensure backend is running on port 5000
- **Check:** Browser console for connection errors
- **Verify:** CORS_ORIGIN matches frontend URL

### No Packets Appearing

**Scenario 1:** Suricata not running
```bash
sudo systemctl start suricata
```

**Scenario 2:** No network traffic
- Generate traffic by browsing websites
- Suricata needs active network activity

**Scenario 3:** Permission denied
```bash
sudo chmod +r /var/log/suricata/eve.json
```

## Performance Considerations

- **Memory**: System keeps max 100 packets in memory
- **Batching**: Packets sent in batches of 10 or every 1 second
- **Real-time**: Individual packets emitted immediately for responsiveness
- **Filtering**: Frontend-side filtering for instant results

## Security Notes

1. Backend accepts connections only from configured CORS_ORIGIN
2. No authentication implemented (add for production use)
3. Log file read-only access required
4. WebSocket connections are unencrypted (use WSS for production)

## Development Tips

### Hot Reload

**Backend with nodemon:**
```bash
cd backend
npm run dev
```

**Frontend with Vite:**
```bash
cd frontend
npm run dev
```

### Debug Mode

Add console logs in:
- `backend/logParser.js` - Log parsing logic
- `frontend/src/hooks/usePackets.ts` - Packet reception

### Testing New Features

1. Stop both servers
2. Make code changes
3. Restart servers
4. Clear browser cache if needed

## Production Deployment

### Backend

```bash
cd backend
npm install --production
NODE_ENV=production npm start
```

### Frontend

```bash
cd frontend
npm run build
# Serve dist/ folder with nginx or similar
```

### Process Manager (PM2)

```bash
npm install -g pm2
pm2 start backend/index.js --name nids-backend
pm2 startup
pm2 save
```

## Next Steps

1. ✅ Backend server created and running
2. ✅ Log parser processing Suricata EVE logs
3. ✅ Socket.IO streaming to frontend
4. ✅ Frontend displaying packets with all fields
5. 🔄 Connect to live Suricata instance
6. 🔄 Monitor real network traffic

## Support

For issues or questions:
- Check logs in backend terminal
- Check browser console for frontend errors
- Verify Suricata is generating logs
- Ensure both servers are running

---

**System Status:** ✅ Backend Running | ⏸️ Frontend Ready | 🔄 Waiting for Connection
