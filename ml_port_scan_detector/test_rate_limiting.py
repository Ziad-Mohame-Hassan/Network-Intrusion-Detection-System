#!/usr/bin/env python3
"""
Test script to demonstrate email rate limiting
Simulates multiple port scans from same and different IPs
"""

import time
from datetime import datetime
from integrated_detector import send_alert, EMAIL_COOLDOWN, last_email_sent

def test_rate_limiting():
    """Test email rate limiting behavior"""
    
    print("="*70)
    print("🧪 EMAIL RATE LIMITING TEST")
    print("="*70)
    print(f"⏱️  Email cooldown: {EMAIL_COOLDOWN / 3600:.0f} hours ({EMAIL_COOLDOWN} seconds)")
    print("="*70 + "\n")
    
    # Test 1: First scan from IP1
    print("📌 TEST 1: First port scan from 192.168.1.100")
    print("-" * 70)
    send_alert("192.168.1.100", "192.168.138.130", [80, 443, 22, 21, 8080], 0.95)
    print("\n✅ Expected: Email SENT (first time)\n")
    time.sleep(2)
    
    # Test 2: Second scan from same IP (within cooldown)
    print("📌 TEST 2: Second port scan from 192.168.1.100 (immediately after)")
    print("-" * 70)
    send_alert("192.168.1.100", "192.168.138.130", [3306, 5432, 27017], 0.92)
    print("\n✅ Expected: Email BLOCKED (cooldown active)\n")
    time.sleep(2)
    
    # Test 3: Scan from different IP
    print("📌 TEST 3: Port scan from DIFFERENT IP (192.168.1.200)")
    print("-" * 70)
    send_alert("192.168.1.200", "192.168.138.130", [135, 139, 445, 3389], 0.98)
    print("\n✅ Expected: Email SENT (different IP, no cooldown)\n")
    time.sleep(2)
    
    # Test 4: Another scan from IP2 (within cooldown)
    print("📌 TEST 4: Another scan from 192.168.1.200 (immediately after)")
    print("-" * 70)
    send_alert("192.168.1.200", "192.168.138.130", [53, 123, 161], 0.89)
    print("\n✅ Expected: Email BLOCKED (cooldown active)\n")
    time.sleep(2)
    
    # Test 5: Scan from third IP
    print("📌 TEST 5: Port scan from THIRD IP (10.0.0.50)")
    print("-" * 70)
    send_alert("10.0.0.50", "192.168.138.130", [8000, 8080, 8443, 9000], 0.94)
    print("\n✅ Expected: Email SENT (third unique IP)\n")
    time.sleep(2)
    
    # Test 6: Rapid scans from IP1
    print("📌 TEST 6: Multiple rapid scans from 192.168.1.100")
    print("-" * 70)
    for i in range(3):
        print(f"   Scan {i+1}/3...")
        send_alert("192.168.1.100", "192.168.138.130", [8000+i, 9000+i], 0.90)
        time.sleep(0.5)
    print("\n✅ Expected: All emails BLOCKED (cooldown still active)\n")
    
    # Summary
    print("="*70)
    print("📊 RATE LIMITING SUMMARY")
    print("="*70)
    print("\nEmails sent per IP:")
    for ip, last_time in last_email_sent.items():
        time_sent = datetime.fromtimestamp(last_time).strftime('%H:%M:%S')
        print(f"  • {ip}: 1 email at {time_sent}")
    
    print(f"\n📧 Total emails sent: {len(last_email_sent)}")
    print(f"🚫 Total alerts blocked: {6 - len(last_email_sent)} (rate limited)")
    
    print("\n⏳ Cooldown Status:")
    current_time = time.time()
    for ip, last_time in last_email_sent.items():
        time_remaining = EMAIL_COOLDOWN - (current_time - last_time)
        hours_remaining = time_remaining / 3600
        print(f"  • {ip}: {hours_remaining:.2f} hours remaining")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETED")
    print("="*70)
    print("\n💡 NOTE: In production, cooldown is 6 hours.")
    print("   Only the FIRST scan from each IP sends an email.")
    print("   Subsequent scans are rate-limited until cooldown expires.\n")

if __name__ == "__main__":
    # Temporarily reduce cooldown for testing (optional)
    # EMAIL_COOLDOWN = 60  # 1 minute for testing
    
    test_rate_limiting()
