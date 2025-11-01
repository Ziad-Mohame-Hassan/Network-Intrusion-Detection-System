const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const fs = require('fs');
const { Tail } = require('tail');
const path = require('path');
const { parseSuricataLog } = require('./logParser');
const config = require('./config');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: config.CORS_ORIGIN,
    methods: ['GET', 'POST']
  }
});

// Middleware
app.use(cors());
app.use(express.json());

// Store connected clients
let connectedClients = 0;

// Packet buffer for batching
let packetBuffer = [];
let batchTimer = null;

/**
 * Send packet batch to all connected clients
 */
function sendPacketBatch() {
  if (packetBuffer.length > 0) {
    io.emit('packet_batch', packetBuffer);
    console.log(`Sent batch of ${packetBuffer.length} packets to clients`);
    packetBuffer = [];
  }
}

/**
 * Add packet to buffer and emit
 */
function handleNewPacket(packet) {
  if (packet) {
    // Emit individual packet immediately
    io.emit('new_packet', packet);
    
    // Also add to buffer for batch processing
    packetBuffer.push(packet);
    
    // Send batch if buffer is full
    if (packetBuffer.length >= config.BATCH_SIZE) {
      sendPacketBatch();
    }
  }
}

/**
 * Initialize log file watching
 */
function initializeLogWatcher() {
  // Determine which log file to use
  let logPath = config.EVE_LOG_PATH;
  
  if (!fs.existsSync(logPath)) {
    console.warn(`Primary log file not found: ${logPath}`);
    logPath = path.join(__dirname, config.SAMPLE_LOG_PATH);
    
    if (!fs.existsSync(logPath)) {
      console.error(`Sample log file not found: ${logPath}`);
      console.log('Starting server without log file. Waiting for logs...');
      return null;
    }
    
    console.log(`Using sample log file: ${logPath}`);
  } else {
    console.log(`Monitoring Suricata log: ${logPath}`);
  }
  
  try {
    // Create tail instance to watch log file
    const tail = new Tail(logPath, {
      fromBeginning: false,
      follow: true,
      useWatchFile: true
    });
    
    tail.on('line', (data) => {
      const packet = parseSuricataLog(data);
      handleNewPacket(packet);
    });
    
    tail.on('error', (error) => {
      console.error('Tail error:', error);
    });
    
    console.log('Log watcher initialized successfully');
    return tail;
  } catch (error) {
    console.error('Error initializing log watcher:', error);
    return null;
  }
}

// Socket.IO connection handling
io.on('connection', (socket) => {
  connectedClients++;
  console.log(`Client connected. Total clients: ${connectedClients}`);
  
  socket.on('disconnect', () => {
    connectedClients--;
    console.log(`Client disconnected. Total clients: ${connectedClients}`);
  });
  
  socket.on('request_history', () => {
    // Optionally send recent packets on request
    if (packetBuffer.length > 0) {
      socket.emit('packet_batch', packetBuffer);
    }
  });
});

// API Routes
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    clients: connectedClients,
    timestamp: new Date().toISOString()
  });
});

app.get('/api/stats', (req, res) => {
  res.json({
    connected_clients: connectedClients,
    buffer_size: packetBuffer.length,
    log_path: config.EVE_LOG_PATH
  });
});

// Initialize batch timer
batchTimer = setInterval(() => {
  sendPacketBatch();
}, config.BATCH_INTERVAL_MS);

// Start server
const PORT = config.PORT;
server.listen(PORT, () => {
  console.log(`===========================================`);
  console.log(`NIDS Backend Server running on port ${PORT}`);
  console.log(`===========================================`);
  console.log(`Health check: http://localhost:${PORT}/api/health`);
  console.log(`Stats: http://localhost:${PORT}/api/stats`);
  console.log(`===========================================`);
  
  // Initialize log watcher after server starts
  const tail = initializeLogWatcher();
  
  if (!tail) {
    console.log('\n⚠️  WARNING: No log file found!');
    console.log('To connect to a real Suricata log:');
    console.log(`1. Set EVE_LOG_PATH environment variable`);
    console.log(`2. Or edit config.js to point to your eve.json file`);
    console.log('\nServer is running but waiting for log data...\n');
  }
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down gracefully...');
  clearInterval(batchTimer);
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});
