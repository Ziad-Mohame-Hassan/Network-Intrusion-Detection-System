#!/bin/bash

# Test Email Alert System
echo "🧪 Testing Email Alert System..."
echo "================================"

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run test
python3 email_alerter.py

echo ""
echo "Check your email: mohamed230104326@sut.edu.eg"
echo "If you received the test email, the system is working! ✅"
