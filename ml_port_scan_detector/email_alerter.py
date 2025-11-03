#!/usr/bin/env python3
"""
Email Alert System for Port Scan Detection
Sends detailed email notifications when port scans are detected
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Email Configuration from environment variables
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')

def send_port_scan_email(alert_data):
    """
    Send email alert for detected port scan
    
    Args:
        alert_data: Dictionary containing:
            - source_ip: Attacker IP
            - target_ip: Target IP
            - ports_scanned: List of ports
            - port_count: Number of ports
            - confidence: ML confidence score
            - timestamp: Detection time
    """
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = SENDER_EMAIL
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = f"🚨 PORT SCAN ALERT - {alert_data['source_ip']} → {alert_data['target_ip']}"
        
        # Format ports list
        ports_str = ', '.join(map(str, alert_data['ports_scanned'][:20]))  # First 20 ports
        if alert_data['port_count'] > 20:
            ports_str += f"... (+{alert_data['port_count'] - 20} more)"
        
        # Format confidence
        confidence_pct = alert_data['confidence'] * 100
        threat_level = "CRITICAL" if confidence_pct >= 90 else "HIGH" if confidence_pct >= 70 else "MEDIUM"
        
        # Create plain text version
        text_content = f"""
╔══════════════════════════════════════════════════════════════╗
║           NETWORK INTRUSION DETECTION ALERT                  ║
║                  PORT SCAN DETECTED                          ║
╚══════════════════════════════════════════════════════════════╝

THREAT LEVEL: {threat_level}
ML CONFIDENCE: {confidence_pct:.1f}%

═══════════════════════════════════════════════════════════════

ATTACK DETAILS:
───────────────────────────────────────────────────────────────
  Attacker IP:     {alert_data['source_ip']}
  Target IP:       {alert_data['target_ip']}
  Ports Scanned:   {alert_data['port_count']} ports
  Detection Time:  {alert_data['timestamp']}

SCANNED PORTS:
───────────────────────────────────────────────────────────────
  {ports_str}

═══════════════════════════════════════════════════════════════

RECOMMENDED ACTIONS:
───────────────────────────────────────────────────────────────
  1. Block source IP: {alert_data['source_ip']} at firewall
  2. Review firewall rules for target: {alert_data['target_ip']}
  3. Check system logs for any successful connections
  4. Monitor for additional scanning attempts
  5. Consider implementing rate limiting

TECHNICAL DETAILS:
───────────────────────────────────────────────────────────────
  Detection Method:  Machine Learning (Random Forest)
  Scan Type:         TCP SYN Scan
  Alert Type:        Real-time Detection
  System:            Network Intrusion Detection System (NIDS)

═══════════════════════════════════════════════════════════════

This is an automated alert from your Network Intrusion Detection System.
For questions or support, contact your security administrator.

System Location: {alert_data.get('system_location', 'Primary Network Gateway')}
Alert ID: {alert_data.get('alert_id', 'N/A')}
"""

        # Create HTML version
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 700px;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .threat-badge {{
            display: inline-block;
            padding: 8px 20px;
            background-color: rgba(255,255,255,0.2);
            border-radius: 20px;
            font-weight: bold;
            margin-top: 15px;
            font-size: 16px;
        }}
        .content {{
            padding: 30px;
        }}
        .info-box {{
            background-color: #fef2f2;
            border-left: 4px solid #dc2626;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .info-row {{
            display: flex;
            padding: 10px 0;
            border-bottom: 1px solid #fee2e2;
        }}
        .info-row:last-child {{
            border-bottom: none;
        }}
        .info-label {{
            font-weight: 600;
            color: #991b1b;
            width: 140px;
            flex-shrink: 0;
        }}
        .info-value {{
            color: #1f2937;
            flex-grow: 1;
            font-family: 'Courier New', monospace;
        }}
        .ports-box {{
            background-color: #f9fafb;
            border: 2px solid #e5e7eb;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            color: #374151;
            word-wrap: break-word;
        }}
        .actions {{
            background-color: #fffbeb;
            border: 2px solid #fbbf24;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .actions h3 {{
            color: #92400e;
            margin-top: 0;
            font-size: 16px;
        }}
        .actions ol {{
            margin: 10px 0;
            padding-left: 20px;
            color: #78350f;
        }}
        .actions li {{
            margin: 8px 0;
            line-height: 1.6;
        }}
        .footer {{
            background-color: #f9fafb;
            padding: 20px 30px;
            text-align: center;
            color: #6b7280;
            font-size: 12px;
            border-top: 1px solid #e5e7eb;
        }}
        .confidence-bar {{
            width: 100%;
            height: 8px;
            background-color: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 10px;
        }}
        .confidence-fill {{
            height: 100%;
            background: linear-gradient(90deg, #dc2626 0%, #ef4444 100%);
            width: {confidence_pct}%;
            transition: width 0.3s;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 PORT SCAN DETECTED 🚨</h1>
            <p>Network Intrusion Detection Alert</p>
            <div class="threat-badge">THREAT LEVEL: {threat_level}</div>
        </div>
        
        <div class="content">
            <div class="info-box">
                <div class="info-row">
                    <div class="info-label">ML Confidence:</div>
                    <div class="info-value">
                        <strong>{confidence_pct:.1f}%</strong>
                        <div class="confidence-bar">
                            <div class="confidence-fill"></div>
                        </div>
                    </div>
                </div>
                <div class="info-row">
                    <div class="info-label">Attacker IP:</div>
                    <div class="info-value"><strong>{alert_data['source_ip']}</strong></div>
                </div>
                <div class="info-row">
                    <div class="info-label">Target IP:</div>
                    <div class="info-value"><strong>{alert_data['target_ip']}</strong></div>
                </div>
                <div class="info-row">
                    <div class="info-label">Ports Scanned:</div>
                    <div class="info-value"><strong>{alert_data['port_count']} ports</strong></div>
                </div>
                <div class="info-row">
                    <div class="info-label">Detection Time:</div>
                    <div class="info-value">{alert_data['timestamp']}</div>
                </div>
            </div>
            
            <h3 style="color: #1f2937; margin: 25px 0 10px 0;">Scanned Ports:</h3>
            <div class="ports-box">
                {ports_str}
            </div>
            
            <div class="actions">
                <h3>⚠️ Recommended Immediate Actions:</h3>
                <ol>
                    <li><strong>Block attacker IP:</strong> Add {alert_data['source_ip']} to firewall blacklist</li>
                    <li><strong>Review logs:</strong> Check for successful connection attempts</li>
                    <li><strong>Verify target:</strong> Ensure {alert_data['target_ip']} has no vulnerabilities</li>
                    <li><strong>Monitor traffic:</strong> Watch for additional scanning activity</li>
                    <li><strong>Update rules:</strong> Consider implementing rate limiting</li>
                </ol>
            </div>
            
            <div style="margin-top: 20px; padding: 15px; background-color: #f0f9ff; border-left: 4px solid #0284c7; border-radius: 5px;">
                <p style="margin: 0; color: #075985; font-size: 13px;">
                    <strong>ℹ️ Technical Details:</strong><br>
                    Detection Method: Machine Learning (Random Forest)<br>
                    Scan Type: TCP SYN Scan<br>
                    System: Network Intrusion Detection System (NIDS)
                </p>
            </div>
        </div>
        
        <div class="footer">
            <p>This is an automated alert from your Network Intrusion Detection System.</p>
            <p>Alert generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
            <p style="margin-top: 10px; font-size: 11px;">
                If you believe this is a false positive, please contact your security administrator.
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        # Attach both versions
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        return True, "Email sent successfully"
        
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"

def test_email_connection():
    """Test email configuration by sending a test message"""
    try:
        msg = MIMEText("This is a test email from your NIDS. Email alerts are working correctly! ✅")
        msg['From'] = SENDER_EMAIL
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = "✅ NIDS Email Alert System - Test Successful"
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        return True, "Test email sent successfully"
    except Exception as e:
        return False, f"Email test failed: {str(e)}"

if __name__ == "__main__":
    # Test email configuration
    print("Testing email configuration...")
    success, message = test_email_connection()
    if success:
        print(f"✅ {message}")
        print(f"Test email sent to: {ADMIN_EMAIL}")
    else:
        print(f"❌ {message}")
