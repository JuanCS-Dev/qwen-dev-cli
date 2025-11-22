#!/bin/bash
# Performance Benchmarking Script

set -euo pipefail

echo "⚡ Performance Benchmarks"
echo "========================"
echo ""

# LLM response time
echo "🧠 Testing LLM response time..."
time python -c "
from qwen_dev_cli.core.llm_engine import LLMEngine
engine = LLMEngine()
response = engine.generate('What is 2+2?')
print(f'Response: {response[:50]}...')
"

# Bash command execution
echo ""
echo "⚡ Testing bash command speed..."
time python -c "
from qwen_dev_cli.mcp_tools.bash_commands import execute_bash_command
result = execute_bash_command('echo test', timeout=5)
print(f'Exit code: {result.exit_code}')
"

# File operations
echo ""
echo "📁 Testing file operations..."
time python -c "
from qwen_dev_cli.mcp_tools.file_operations import list_files
files = list_files('.', max_depth=2)
print(f'Found {len(files)} files')
"

# Constitutional AI check
echo ""
echo "⚖️  Testing Constitutional AI speed..."
time python -c "
from qwen_dev_cli.core.constitutional_ai import ConstitutionalAI
ai = ConstitutionalAI()
result = ai.evaluate_command('ls -la')
print(f'Safety: {result[\"safety_level\"]}')
"

echo ""
echo "✅ Benchmarks complete"
