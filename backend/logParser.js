const crypto = require('crypto');

/**
 * Maps Suricata protocol to application protocol
 */
function mapProtocol(proto, appProto) {
  if (appProto) {
    return appProto.toUpperCase();
  }
  
  switch (proto?.toLowerCase()) {
    case 'tcp':
      return 'TCP';
    case 'udp':
      return 'UDP';
    case 'icmp':
      return 'ICMP';
    default:
      return 'UNKNOWN';
  }
}

/**
 * Determines activity type based on protocol and port
 */
function determineActivity(protocol, destPort, srcPort) {
  const port = destPort || srcPort;
  const proto = protocol?.toUpperCase();
  
  // Protocol-based classification (most specific)
  switch (proto) {
    case 'DNS':
    case 'MDNS':
      return 'DNS Query';
    
    case 'HTTP':
      return 'Web Browsing';
    
    case 'HTTPS':
    case 'TLS':
      // Check port for more specific classification
      if (port === 443) return 'Secure Web Browsing';
      if ([465, 587, 993, 995].includes(port)) return 'Secure Email';
      return 'Encrypted Communication';
    
    case 'SSH':
      return 'Remote Shell';
    
    case 'FTP':
    case 'FTPS':
      return 'File Transfer';
    
    case 'SMTP':
    case 'POP3':
    case 'IMAP':
      return 'Email';
    
    case 'SMB':
    case 'NETBIOS':
      return 'File Sharing';
    
    case 'RDP':
      return 'Remote Desktop';
    
    case 'MYSQL':
    case 'PGSQL':
    case 'MSSQL':
    case 'MONGODB':
    case 'REDIS':
      return 'Database Activity';
    
    case 'SIP':
      return 'VoIP Signaling';
    
    case 'RTP':
      return 'VoIP Call';
    
    case 'RTSP':
      return 'Video Streaming';
    
    case 'NTP':
      return 'Time Sync';
    
    case 'DHCP':
      return 'Network Config';
    
    case 'ICMP':
      return 'Network Diagnostic';
  }
  
  // Port-based classification (fallback for TCP/UDP)
  if (port) {
    // Web traffic
    if ([80, 8080, 8000, 8888].includes(port)) return 'Web Browsing';
    if ([443, 8443].includes(port)) return 'Secure Web Browsing';
    
    // VoIP
    if ([5060, 5061].includes(port)) return 'VoIP Signaling';
    if ([10000, 20000].includes(port) || (port >= 16384 && port <= 32767)) return 'VoIP Call';
    
    // File transfer
    if ([20, 21, 69, 115, 989, 990].includes(port)) return 'File Transfer';
    
    // Email
    if ([25, 110, 143, 465, 587, 993, 995].includes(port)) return 'Email';
    
    // Database
    if ([3306, 5432, 1433, 1521, 27017, 6379].includes(port)) return 'Database Activity';
    
    // Remote Desktop
    if ([3389, 5900, 5901].includes(port)) return 'Remote Desktop';
    
    // DNS
    if (port === 53) return 'DNS Query';
    
    // File Sharing
    if ([445, 139, 137, 138].includes(port)) return 'File Sharing';
    
    // Streaming
    if ([554, 1935, 8554].includes(port)) return 'Video Streaming';
    
    // Gaming ports
    if ([27015, 27016, 25565, 7777].includes(port)) return 'Gaming';
    
    // Messaging
    if ([5222, 5223, 5228].includes(port)) return 'Messaging';
  }
  
  // Generic classification based on protocol type
  if (proto === 'TCP') return 'TCP Traffic';
  if (proto === 'UDP') return 'UDP Traffic';
  
  return 'Network Traffic';
}

/**
 * Calculates risk level based on various factors
 */
function calculateRiskLevel(event) {
  // If Suricata already marked it as an alert, it's high risk
  if (event.event_type === 'alert') {
    const severity = event.alert?.severity || 3;
    if (severity === 1) return 'HIGH';
    if (severity === 2) return 'MEDIUM';
    return 'LOW';
  }
  
  // Check for suspicious ports
  const destPort = event.dest_port;
  const suspiciousPorts = [23, 135, 139, 445, 1433, 3389, 5900];
  
  if (suspiciousPorts.includes(destPort)) {
    return 'MEDIUM';
  }
  
  // Check for unusual packet sizes
  if (event.flow?.bytes_toserver > 100000 || event.flow?.bytes_toclient > 100000) {
    return 'MEDIUM';
  }
  
  return 'LOW';
}

/**
 * Determines if a packet is suspicious
 */
function isSuspicious(event) {
  // Alert events are always suspicious
  if (event.event_type === 'alert') return true;
  
  // Check for anomalies
  if (event.anomaly) return true;
  
  // High risk packets are suspicious
  const riskLevel = calculateRiskLevel(event);
  if (riskLevel === 'HIGH') return true;
  
  return false;
}

/**
 * Extract packet size from various event types
 */
function extractPacketSize(event) {
  // Try to get from flow data first (most accurate)
  const flow = event.flow || {};
  const flowBytes = (flow.bytes_toserver || 0) + (flow.bytes_toclient || 0);
  
  if (flowBytes > 0) {
    return flowBytes;
  }
  
  // For HTTP events, check http.length
  if (event.event_type === 'http' && event.http) {
    return event.http.length || 512; // Default HTTP size if not specified
  }
  
  // For DNS events, estimate based on typical DNS packet size
  if (event.event_type === 'dns') {
    // DNS queries are typically 64-512 bytes
    // DNS responses can be larger (up to 4KB with EDNS)
    if (event.dns?.type === 'answer') {
      // Estimate based on number of answers
      const answerCount = event.dns.answers?.length || 0;
      return Math.max(128, answerCount * 64);
    }
    return 64; // Typical DNS query size
  }
  
  // For TLS events, use initial handshake estimate
  if (event.event_type === 'tls') {
    return 1500; // Typical TLS handshake packet size
  }
  
  // For alert events, estimate based on protocol
  if (event.event_type === 'alert') {
    const proto = event.proto?.toLowerCase();
    if (proto === 'tcp') return 1460; // TCP MTU
    if (proto === 'udp') return 1472; // UDP MTU
    return 512;
  }
  
  // Default estimate
  return 0;
}

/**
 * Parses a single Suricata EVE log line
 */
function parseSuricataLog(logLine) {
  try {
    const event = JSON.parse(logLine);
    
    // Only process flow and alert events
    if (!['flow', 'alert', 'http', 'dns', 'tls'].includes(event.event_type)) {
      return null;
    }
    
    const protocol = mapProtocol(event.proto, event.app_proto);
    const activity = determineActivity(protocol, event.dest_port, event.src_port);
    const riskLevel = calculateRiskLevel(event);
    
    // Extract flow statistics
    const flow = event.flow || {};
    const duration = flow.age || 0;
    const bytes = extractPacketSize(event);
    const packets = (flow.pkts_toserver || 0) + (flow.pkts_toclient || 0) || 1;
    
    return {
      id: crypto.randomUUID(),
      timestamp: new Date(event.timestamp),
      sourcePort: event.src_port || 0,
      destinationPort: event.dest_port || 0,
      sourceIP: event.src_ip || 'unknown',
      destinationIP: event.dest_ip || 'unknown',
      protocol: protocol,
      application_protocol: event.app_proto?.toUpperCase() || protocol,
      size: bytes,
      isSuspicious: isSuspicious(event),
      activity: activity,
      risk_level: riskLevel,
      features: {
        duration: duration,
        packet_rate: duration > 0 ? packets / duration : 0,
        avg_size: packets > 0 ? bytes / packets : 0,
        is_encrypted: event.app_proto === 'tls' || event.app_proto === 'ssh',
        is_compressed: false
      },
      // Additional metadata (optional)
      _raw: {
        event_type: event.event_type,
        alert: event.alert || null,
        flow_id: event.flow_id || null
      }
    };
  } catch (error) {
    console.error('Error parsing log line:', error.message);
    return null;
  }
}

module.exports = {
  parseSuricataLog
};
