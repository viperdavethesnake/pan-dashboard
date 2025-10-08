#!/bin/bash

# Pan-Kom Environment Setup Script
# Prepares the Python environment for importing Panzura Symphony data into ClickHouse

set -e  # Exit on any error

echo "=========================================="
echo "Pan-Kom Environment Setup"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found. Please run this script from the project root directory."
    exit 1
fi

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $PYTHON_VERSION"

# Check if Python 3.9+ is installed
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]; }; then
    echo "Error: Python 3.9 or higher is required. Found Python $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python version is compatible"
echo ""

# Check if venv exists
if [ -d "venv" ]; then
    echo "Virtual environment already exists."
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf venv
    else
        echo "Using existing virtual environment."
        SKIP_VENV_CREATE=true
    fi
fi

# Create virtual environment
if [ "$SKIP_VENV_CREATE" != "true" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt --quiet

echo "✓ Dependencies installed"
echo ""

# Check if Docker is running
echo "Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "⚠ Warning: Docker is not running or not installed."
    echo "   Please start Docker Desktop before running the import script."
else
    echo "✓ Docker is running"
fi
echo ""

# Check if ClickHouse container is running
echo "Checking ClickHouse container..."
if docker ps --format '{{.Names}}' | grep -q "pan-clickhouse"; then
    echo "✓ ClickHouse container is running"
    
    # Test connection
    if docker exec pan-clickhouse clickhouse-client --password clickhouse -q "SELECT 1" > /dev/null 2>&1; then
        echo "✓ ClickHouse is accessible"
    else
        echo "⚠ Warning: ClickHouse container is running but not responding"
        echo "   Try: cd docker && docker compose restart clickhouse"
    fi
else
    echo "⚠ Warning: ClickHouse container is not running"
    echo "   Start it with: cd docker && docker compose up -d"
fi
echo ""

# Check if data file exists
echo "Checking for data file..."
if [ -f "data/symphony_scan.csv" ]; then
    FILE_SIZE=$(du -h data/symphony_scan.csv | awk '{print $1}')
    LINE_COUNT=$(wc -l < data/symphony_scan.csv)
    echo "✓ Found data/symphony_scan.csv"
    echo "  Size: $FILE_SIZE"
    echo "  Lines: $(printf "%'d" $LINE_COUNT)"
else
    echo "⚠ Warning: data/symphony_scan.csv not found"
    echo "   Place your Panzura Symphony CSV file in the data/ directory"
    echo "   and rename it to 'symphony_scan.csv'"
fi
echo ""

# Check if schema is created
echo "Checking database schema..."
if docker exec pan-clickhouse clickhouse-client --password clickhouse -q "SELECT 1 FROM file_share.file_scan LIMIT 1" > /dev/null 2>&1; then
    ROW_COUNT=$(docker exec pan-clickhouse clickhouse-client --password clickhouse -q "SELECT COUNT(*) FROM file_share.file_scan" 2>/dev/null || echo "0")
    echo "✓ Database schema exists"
    echo "  Current row count: $(printf "%'d" $ROW_COUNT)"
else
    echo "⚠ Warning: Database schema not created"
    echo "   Create it with: cat scripts/create_schema.sql | docker exec -i pan-clickhouse clickhouse-client --password clickhouse"
fi
echo ""

echo "=========================================="
echo "Setup Summary"
echo "=========================================="
echo "✓ Virtual environment: venv/"
echo "✓ Dependencies installed"
echo ""
echo "To activate the environment manually:"
echo "  source venv/bin/activate"
echo ""
echo "To import data:"
echo "  cd scripts"
echo "  source ../venv/bin/activate"
echo "  python import_data.py"
echo ""
echo "To deactivate when done:"
echo "  deactivate"
echo ""
echo "=========================================="

