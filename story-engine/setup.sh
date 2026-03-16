#!/bin/bash
# setup.sh — rebuild venv and install dependencies
# Usage: ./setup.sh

set -e

PYTHON="/opt/homebrew/bin/python3.11"
VENV=".venv"

echo "🔧 Story Engine — environment setup"
echo "Python: $PYTHON"
echo ""

# check python exists
if [ ! -f "$PYTHON" ]; then
  echo "❌ Python 3.11 not found at $PYTHON"
  echo "   Try: brew install python@3.11"
  exit 1
fi

# deactivate if in a venv
if [ -n "$VIRTUAL_ENV" ]; then
  echo "⚠️  Deactivating current venv..."
  deactivate 2>/dev/null || true
fi

# remove old venv
if [ -d "$VENV" ]; then
  echo "🗑  Removing old venv..."
  rm -rf "$VENV"
fi

# create fresh venv
echo "🐍 Creating venv with Python 3.11..."
$PYTHON -m venv $VENV

# activate
source $VENV/bin/activate

# upgrade pip silently
echo "📦 Upgrading pip..."
pip install --upgrade pip --quiet

# install requirements
echo "📦 Installing requirements..."
pip install -r backend/requirements.txt

echo ""
echo "✅ Done! Activate with:"
echo "   source .venv/bin/activate"
echo ""
echo "Then run:"
echo "   uvicorn backend.main:app --reload --port 8080"
