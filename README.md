# Network Intrusion Detection System (NIDS)

A real-time network intrusion detection system built with React and TypeScript that monitors network traffic and identifies potential security threats.

## Features

- **Real-time Traffic Monitoring** - Live packet capture and analysis
- **Protocol Filtering** - Filter traffic by protocol type (TCP, UDP, HTTP, etc.)
- **Threat Detection** - Identify suspicious network activity
- **Search Functionality** - Search through captured packets
- **Connection Status** - Real-time connection monitoring
- **Modern UI** - Clean, responsive interface built with React and Tailwind CSS

## Tech Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS
- **Backend**: Node.js, Express, Socket.IO
- **Icons**: Lucide React
- **Build Tool**: Vite
- **Real-time Communication**: Socket.IO Client/Server
- **Network Analysis**: Suricata IDS (configuration included)
- **Log Processing**: Real-time EVE JSON parsing

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Suricata IDS (optional - sample logs provided)

### Quick Start

**Option 1: Using startup scripts (Recommended)**

1. Clone the repository:
```bash
git clone <repository-url>
cd IDS
```

2. Install backend dependencies:
```bash
cd backend
npm install
cd ..
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

4. Start both servers:
```bash
# Terminal 1 - Backend
./start-backend.sh

# Terminal 2 - Frontend
./start-frontend.sh
```

5. Open your browser and navigate to `http://localhost:5173`

**Option 2: Manual setup**

1. Start the backend:
```bash
cd backend
npm install
npm start
# Backend runs on http://localhost:5000
```

2. In a new terminal, start the frontend:
```bash
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:5173
```

### Connecting to Real Suricata Logs

By default, the backend monitors `/var/log/suricata/eve.json`. To use your own Suricata installation:

1. Ensure Suricata is running:
```bash
sudo systemctl status suricata
```

2. Verify log file exists:
```bash
sudo ls -l /var/log/suricata/eve.json
```

3. Grant read permissions (if needed):
```bash
sudo chmod +r /var/log/suricata/eve.json
```

4. Restart the backend server

The system will automatically start processing real-time network traffic!

## Project Structure

```
IDS/
├── frontend/              # React frontend application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom React hooks (usePackets)
│   │   ├── types/         # TypeScript type definitions
│   │   └── utils/         # Utility functions
│   └── package.json
├── backend/               # Node.js backend server
│   ├── index.js           # Main server file
│   ├── logParser.js       # Suricata log parser
│   ├── config.js          # Configuration settings
│   ├── package.json
│   └── README.md
├── sample eve.log         # Sample Suricata logs for testing
├── suricata.yaml          # Suricata IDS configuration
├── start-backend.sh       # Backend startup script
├── start-frontend.sh      # Frontend startup script
└── README.md
```

## Available Scripts

### Frontend (in `frontend/` directory)
- `npm run dev` - Start development server (http://localhost:5173)
- `npm run build` - Build for production
- `npm run lint` - Run ESLint
- `npm run preview` - Preview production build

### Backend (in `backend/` directory)
- `npm start` - Start production server
- `npm run dev` - Start with auto-reload (nodemon)

## How It Works

1. **Suricata IDS** monitors network traffic and writes events to `eve.json`
2. **Backend Server** watches the log file in real-time using the `tail` library
3. **Log Parser** processes EVE JSON entries and extracts:
   - Source/Destination IP and Port
   - Protocol (TCP, UDP, TLS, HTTP, DNS, etc.)
   - Traffic statistics (bytes, packets, duration)
   - Risk assessment (LOW, MEDIUM, HIGH)
   - Activity classification (VoIP, File Transfer, Database, etc.)
4. **Socket.IO** streams processed packets to connected clients
5. **React Frontend** displays packets in a responsive table with filtering options

## Data Fields Displayed

- **Timestamp**: Precise time of packet capture
- **Source IP & Port**: Origin of network traffic
- **Destination IP & Port**: Target of network traffic
- **Protocol**: Application protocol (HTTP, HTTPS, SSH, DNS, etc.)
- **Activity**: Classified activity type
- **Size**: Packet size and rate
- **Risk Level**: Security assessment (LOW/MEDIUM/HIGH)
- **Status**: Normal or Suspicious flag

## Configuration

### Backend Configuration (`backend/config.js`)
- `PORT`: Backend server port (default: 5000)
- `EVE_LOG_PATH`: Path to Suricata log file
- `CORS_ORIGIN`: Allowed frontend origin
- `MAX_PACKETS_IN_MEMORY`: Buffer size for packets

### Suricata Configuration (`suricata.yaml`)
Contains Suricata IDS configuration for network monitoring.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.
