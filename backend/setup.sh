#!/bin/bash

# GalaxyRend Backend Setup Script

set -e

echo "🚀 Setting up GalaxyRend Backend..."

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR"

cd "$BACKEND_DIR"

# Check if Python 3.8+ is available
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Copy environment template if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "🔑 Please edit .env file with your configuration"
fi

# Create logs directory
mkdir -p logs

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your configuration:"
echo "   - Database connection string"
echo "   - StarkNet RPC URL and contract address"
echo "   - Redis URL (if using)"
echo ""
echo "2. Start the backend:"
echo "   cd $BACKEND_DIR"
echo "   source venv/bin/activate"
echo "   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "3. API Documentation will be available at:"
echo "   http://localhost:8000/docs"
echo ""

# Check if PostgreSQL is running
if command -v pg_isready &> /dev/null; then
    if pg_isready -q; then
        echo "✅ PostgreSQL is running"
    else
        echo "⚠️  PostgreSQL is not running. Please start it before running the backend."
    fi
else
    echo "⚠️  PostgreSQL client tools not found. Please ensure PostgreSQL is installed and running."
fi

# Check if Redis is running (optional)
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis is running"
    else
        echo "⚠️  Redis is not running (optional for caching)"
    fi
fi

echo ""
echo "🎉 GalaxyRend Backend is ready!"
