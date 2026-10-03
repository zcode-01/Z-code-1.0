#!/bin/bash
# ─────────────────────────────────────────────
# Z-Code Backend — Setup Script
# Run this once after cloning the repository.
# Usage: ./setup.sh
# ─────────────────────────────────────────────

set -e

BACKEND_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BACKEND_DIR"

echo "🔧 Setting up Z-Code backend..."

# 1. Detect Python 3.12 or 3.13
if command -v python3.13 &>/dev/null; then
  PYTHON_CMD=python3.13
elif command -v python3.12 &>/dev/null; then
  PYTHON_CMD=python3.12
elif command -v python3 &>/dev/null; then
  PYTHON_CMD=python3
else
  echo "❌ python3 not found. Please install Python 3.12 or 3.13."
  exit 1
fi

echo "📦 Creating virtual environment using $($PYTHON_CMD --version)..."
rm -rf venv
$PYTHON_CMD -m venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies
echo "⬇️  Installing dependencies from requirements.txt..."
pip install --upgrade pip -q
pip install -r requirements.txt

# 4. Copy .env.example to .env if not exists
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  echo "📄 Creating .env configuration..."
  cp .env.example .env
fi

# 5. Seed database
echo "🌱 Initializing and seeding database..."
python -m app.seed

echo ""
echo "✅ Setup complete! Start the server anytime with: ./start.sh"
