#!/bin/bash

# Development setup script for Mathemagician

echo "🎨 Mathemagician Development Setup"
echo "===================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if Redis is running
echo "🔍 Checking Redis..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis is not running!"
    echo "   Start Redis with: brew services start redis"
    echo "   Or install with: brew install redis"
else
    echo "✅ Redis is running"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "To start development:"
echo "  1. source venv/bin/activate"
echo "  2. python app/main.py"
echo "  or: uvicorn app.main:app --reload"
echo ""
echo "API will be available at: http://localhost:8000"
echo "Docs at: http://localhost:8000/docs"
