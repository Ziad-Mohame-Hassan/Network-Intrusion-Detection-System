module.exports = {
  // Server configuration
  PORT: process.env.PORT || 5000,
  
  // Suricata EVE log file path
  // Change this to your actual Suricata EVE log path
  EVE_LOG_PATH: process.env.EVE_LOG_PATH || '/var/log/suricata/eve.json',
  
  // Fallback to sample log if main log doesn't exist
  SAMPLE_LOG_PATH: '../sample eve.log',
  
  // CORS settings
  CORS_ORIGIN: process.env.CORS_ORIGIN || 'http://localhost:5173',
  
  // Packet processing settings
  MAX_PACKETS_IN_MEMORY: 100,
  BATCH_SIZE: 10,
  BATCH_INTERVAL_MS: 1000
};
