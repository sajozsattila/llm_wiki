#!/bin/bash

# Stop script for vLLM-MLX server and Claude
# Automatically finds and stops running processes without requiring PID

echo "Searching for running vLLM-MLX and Claude processes..."

# Find vllm-mlx server process
SERVER_PID=$(pgrep -f "vllm-mlx serve" 2>/dev/null | head -n 1)

# Find Claude process
CLAUDE_PID=$(pgrep -f "claude" 2>/dev/null | head -n 1)

# Handle the cases
if [ -z "$SERVER_PID" ] && [ -z "$CLAUDE_PID" ]; then
  echo "No running vLLM-MLX server or Claude found!"
  exit 0
elif [ -z "$SERVER_PID" ]; then
  echo "No vLLM-MLX server found, but found Claude PID: $CLAUDE_PID"
  CLAUDE_PID=$CLAUDE_PID
elif [ -z "$CLAUDE_PID" ]; then
  echo "vLLM-MLX server found with PID: $SERVER_PID, but no Claude process"
  CLAUDE_PID=""
else
  echo "Found vLLM-MLX server (PID: $SERVER_PID) and Claude (PID: $CLAUDE_PID)"
  SERVER_PID=$SERVER_PID
  CLAUDE_PID=$CLAUDE_PID
fi

# Kill processes if found
if [ -n "$SERVER_PID" ]; then
  echo "Killing vLLM-MLX server (PID $SERVER_PID)..."
  kill -9 $SERVER_PID 2>/dev/null
  echo "Server killed (PID $SERVER_PID)"
fi

if [ -n "$CLAUDE_PID" ]; then
  echo "Killing Claude process (PID $CLAUDE_PID)..."
  kill -9 $CLAUDE_PID 2>/dev/null
  echo "Claude killed (PID $CLAUDE_PID)"
fi

# Wait a moment for processes to terminate
sleep 1

# Check if any processes are still running
remaining_server=$(pgrep -f "vllm-mlx serve" 2>/dev/null | wc -l)
remaining_claude=$(pgrep -f "claude.*--model.*mlx" 2>/dev/null | wc -l)

if [ "$remaining_server" -gt 0 ]; then
  echo "Warning: $remaining_server vLLM-MLX process(es) still running, killing..."
  pgrep -f "vllm-mlx serve" 2>/dev/null | xargs -r kill -9 2>/dev/null
fi

if [ "$remaining_claude" -gt 0 ]; then
  echo "Warning: Some Claude process(es) still running, killing..."
  pgrep -f "claude.*--model.*mlx" 2>/dev/null | xargs -r kill -9 2>/dev/null
fi

# Cleanup log files from the last 5 minutes
find /tmp -name "vllm_mlx_*.log" -mmin -5 -delete 2>/dev/null

echo ""
echo "Done!"