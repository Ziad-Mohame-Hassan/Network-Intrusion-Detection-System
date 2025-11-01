# NIDS Backend Server

Backend server for the Network Intrusion Detection System that processes Suricata EVE logs and streams them to the frontend via Socket.IO.

## Features

- **Real-time Log Parsing**: Watches Suricata EVE JSON log files
- **Protocol Detection**: Maps network protocols to application protocols
- **Risk Assessment**: Calculates risk levels based on traffic patterns
- **Activity Classification**: Identifies network activities (VoIP, File Transfer, etc.)
- **WebSocket Streaming**: Sends processed packets to frontend in real-time
- **Batch Processing**: Efficient packet batching for optimal performance

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Suricata installed and running (optional - can use sample logs)

## Installation

```bash
cd backend
npm install
```

## Configuration

Edit `config.js` to customize:

- **PORT**: Server port (default: 5000)
- **EVE_LOG_PATH**: Path to Suricata EVE JSON log file (default: `/var/log/suricata/eve.json`)
- **CORS_ORIGIN**: Frontend URL (default: `http://localhost:5173`)

### Environment Variables

You can also use environment variables:

```bash
export PORT=5000
export EVE_LOG_PATH=/path/to/your/eve.json
export CORS_ORIGIN=http://localhost:5173
```

## Usage

### Development Mode (with auto-reload)

```bash
npm run dev
```

### Production Mode

```bash
npm start
```

## API Endpoints

### Health Check
```
GET /api/health
```
Returns server health status and connected clients count.

### Statistics
```
GET /api/stats
```
Returns server statistics including buffer size and log path.

## Socket.IO Events

### Client → Server

- **connection**: Client connects to server
- **disconnect**: Client disconnects
- **request_history**: Request recent packets

### Server → Client

- **new_packet**: Emits individual packet data
- **packet_batch**: Emits batch of packets

## Log Format

The backend expects Suricata EVE JSON format logs. Each log entry should be a JSON object with fields like:

```json
{
  "timestamp": "2024-11-01T15:30:00.123456+0000",
  "event_type": "flow",
  "src_ip": "192.168.1.100",
  "src_port": 54321,
  "dest_ip": "8.8.8.8",
  "dest_port": 53,
  "proto": "UDP",
  "app_proto": "dns",
  "flow": {...}
}
```

## Supported Event Types

- **flow**: Network flow events
- **alert**: Suricata alerts
- **http**: HTTP traffic
- **dns**: DNS queries/responses
- **tls**: TLS/SSL connections

## Troubleshooting

### No packets appearing

1. Check if Suricata is running: `sudo systemctl status suricata`
2. Verify log file exists: `ls -l /var/log/suricata/eve.json`
3. Check file permissions
4. Monitor backend logs for errors

### Connection issues

1. Ensure backend is running on port 5000
2. Check CORS configuration
3. Verify frontend is connecting to correct URL

### Using Sample Logs

If you don't have Suricata installed, the backend will automatically use the sample logs from `../sample eve.log`.

To test with real traffic:
```bash
# Tail the sample log to simulate real-time updates
tail -f ../sample\ eve.log
```

## Architecture

```
┌─────────────────┐
│  Suricata EVE   │
│   (eve.json)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Log Watcher   │
│   (tail lib)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Log Parser    │
│  (logParser.js) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Socket.IO      │
│  Server         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Frontend      │
│   (React)       │
└─────────────────┘
```

## License

MIT
