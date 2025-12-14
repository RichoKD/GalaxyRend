#!/bin/bash

# GalaxyRend Worker Switcher
# Easily switch between old and new worker implementations

set -e

WORKER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$WORKER_DIR"

echo "🔧 GalaxyRend Worker Switcher"
echo "============================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env - please edit with your configuration"
    echo ""
fi

# Function to check dependencies
check_deps() {
    echo "🔍 Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 not found"
        exit 1
    fi
    echo "✅ Python: $(python3 --version)"
    
    # Check Blender
    if ! command -v blender &> /dev/null; then
        echo "⚠️  Blender not found in PATH"
        echo "   Make sure BLENDER_PATH is set correctly in .env"
    else
        echo "✅ Blender: $(blender --version | head -n 1)"
    fi
    
    # Check IPFS
    if ! command -v ipfs &> /dev/null; then
        echo "⚠️  IPFS not found in PATH"
        echo "   Make sure IPFS node is running"
    else
        echo "✅ IPFS installed"
    fi
    
    echo ""
}

# Function to show menu
show_menu() {
    echo "Select worker to run:"
    echo ""
    echo "  1) New API-based worker (main_api.py) ⭐ RECOMMENDED"
    echo "  2) Old blockchain-based worker (main.py)"
    echo "  3) Check dependencies"
    echo "  4) View logs"
    echo "  5) Clean temp files"
    echo "  6) Exit"
    echo ""
    read -p "Enter choice [1-6]: " choice
    echo ""
}

# Function to run new worker
run_new_worker() {
    echo "🚀 Starting API-based worker..."
    echo "Press Ctrl+C to stop"
    echo ""
    python3 src/main_api.py
}

# Function to run old worker
run_old_worker() {
    echo "🚀 Starting blockchain-based worker..."
    echo "⚠️  Note: This is the legacy version"
    echo "Press Ctrl+C to stop"
    echo ""
    python3 src/main.py
}

# Function to view logs
view_logs() {
    echo "📋 Recent worker activity:"
    echo ""
    if [ -f src/temp/completed_jobs.json ]; then
        echo "Completed jobs:"
        cat src/temp/completed_jobs.json
        echo ""
    else
        echo "No completed jobs yet"
    fi
}

# Function to clean temp files
clean_temp() {
    echo "🧹 Cleaning temporary files..."
    if [ -d src/temp ]; then
        rm -rf src/temp/*
        echo "✅ Temp directory cleaned"
    else
        echo "ℹ️  No temp directory found"
    fi
    echo ""
}

# Main loop
while true; do
    show_menu
    
    case $choice in
        1)
            run_new_worker
            ;;
        2)
            run_old_worker
            ;;
        3)
            check_deps
            ;;
        4)
            view_logs
            ;;
        5)
            clean_temp
            ;;
        6)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice"
            echo ""
            ;;
    esac
done
