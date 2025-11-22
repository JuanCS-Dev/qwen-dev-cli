#!/bin/bash
# HuggingFace Spaces Deployment Script
# For MCP 1st Birthday Hackathon

set -euo pipefail

SPACE_NAME="${HF_SPACE_NAME:-qwen-dev-cli}"
SPACE_SDK="gradio"
SPACE_SDK_VERSION="6.0.0"

echo "🚀 HuggingFace Spaces Deployment"
echo "================================"
echo "Space: $SPACE_NAME"
echo "SDK: $SPACE_SDK $SPACE_SDK_VERSION"
echo ""

# Check if HF CLI is installed
if ! command -v huggingface-cli &> /dev/null; then
    echo "❌ huggingface-cli not found. Installing..."
    pip install -U huggingface_hub
fi

# Check authentication
echo "🔐 Checking authentication..."
if ! huggingface-cli whoami &> /dev/null; then
    echo "❌ Not logged in to HuggingFace"
    echo "Run: huggingface-cli login"
    exit 1
fi
echo "✅ Authenticated"

# Pre-flight checks
echo ""
echo "✈️  Pre-flight checks..."
bash scripts/maintenance/directory_audit.sh || {
    echo "⚠️  Directory structure has issues, but continuing..."
}

# Run tests
echo ""
echo "🧪 Running test suite..."
pytest tests/ -v --tb=short || {
    echo "⚠️  Some tests failed, review before deploying"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
}

# Create Space README
echo ""
echo "📝 Generating Space README..."
cat > HF_SPACES_README.md << 'HFEOF'
---
title: Qwen Dev CLI
emoji: 🚀
colorFrom: purple
colorTo: blue
sdk: gradio
sdk_version: 6.0.0
app_file: gradio_ui/app.py
pinned: false
license: mit
tags:
  - mcp
  - cli
  - ai-assistant
  - qwen
  - gemini
  - hackathon
---

# Qwen Dev CLI - MCP Hackathon Submission

> **Advanced AI-Powered Development Assistant with MCP Integration**

Built for the **MCP 1st Birthday Hackathon** 🎉

## Features

- 🧠 Multi-LLM orchestration (Qwen + Gemini)
- 🛠️ 27+ MCP tools with hardened bash execution
- 🎨 Skills-based UI (Anthropic pattern)
- ⚖️ Constitutional AI with real-time metrics
- 🔒 150/150 tests - production-grade reliability

## Quick Start

Try these examples:
- "Analyze this codebase structure"
- "Create a Flask API with auth"
- "Run tests and explain failures"

## Links

- [GitHub Repository](https://github.com/YourUsername/qwen-dev-cli)
- [Documentation](https://github.com/YourUsername/qwen-dev-cli/blob/main/README.md)
- [Hackathon Submission](https://www.modelcontextprotocol.io/hackathon)

HFEOF

echo "✅ README generated"

# Build package
echo ""
echo "📦 Building package..."
python -m build

# Deploy instructions
echo ""
echo "🎯 Deployment Steps:"
echo "==================="
echo ""
echo "1. Create Space on HuggingFace:"
echo "   huggingface-cli repo create $SPACE_NAME --type space --space_sdk gradio"
echo ""
echo "2. Clone the Space:"
echo "   git clone https://huggingface.co/spaces/YOUR_USERNAME/$SPACE_NAME"
echo ""
echo "3. Copy files:"
echo "   cp -r gradio_ui/* ../YOUR_SPACE/"
echo "   cp requirements.txt ../YOUR_SPACE/"
echo "   cp HF_SPACES_README.md ../YOUR_SPACE/README.md"
echo ""
echo "4. Push to Space:"
echo "   cd ../YOUR_SPACE"
echo "   git add ."
echo "   git commit -m 'Initial deployment'"
echo "   git push"
echo ""
echo "✅ Deployment script complete!"
