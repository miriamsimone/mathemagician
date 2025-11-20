#!/bin/bash

# Simple HTTP server for the test UI

echo "🌐 Starting Test UI Server"
echo "=========================="
echo ""
echo "Open in browser: http://localhost:3000/test_ui.html"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 -m http.server 3000
