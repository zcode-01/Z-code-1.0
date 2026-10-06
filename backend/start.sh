#!/bin/bash
# ─────────────────────────────────────────────
# Z-Code Backend — Start Script
# Run this from the backend/ directory.
# Usage:  ./start.sh
# ─────────────────────────────────────────────

set -e

BACKEND_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BACKEND_DIR"

# 1. Activate virtual environment (auto-run setup if missing)
if [ ! -d "venv" ]; then
  echo "📦 Virtual environment not found. Running setup.sh..."
  bash setup.sh
fi

source venv/bin/activate

# 2. Seed the database (safe to run multiple times — skips existing data)
echo "🌱 Running database seed..."
python -m app.seed

# 3. Free port 8000 if already in use
PORT_PIDS=$(lsof -ti :8000 2>/dev/null || true)
if [ -n "$PORT_PIDS" ]; then
  echo "⚠️  Port 8000 is already in use. Cleaning up old processes ($PORT_PIDS)..."
  echo "$PORT_PIDS" | xargs kill -9 2>/dev/null || true
  sleep 1
fi

# 4. Start the server
echo ""
echo "🚀 Starting Z-Code backend..."
echo "   API:       http://localhost:8000/api"
echo "   Swagger:   http://localhost:8000/api/docs"
echo "   Press Ctrl+C to stop"
echo ""
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
