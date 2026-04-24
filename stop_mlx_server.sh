#!/bin/bash

# Stop script for vLLM-MLX server and OpenCode
# Automatically finds and stops running processes without requiring PID

echo "Searching for running vLLM-MLX and OpenCode processes..."

# Find vllm-mlx server process
SERVER_PID=$(pgrep -f "vllm-mlx serve" 2>/dev/null | head -n 1)

# Find OpenCode process
OPENCODE_PID=$(pgrep -f "opencode serve" 2>/dev/null | head -n 1)

# Handle the cases
if [ -z "$SERVER_PID" ] && [ -z "$OPENCODE_PID" ]; then
  echo "No running vLLM-MLX server or OpenCode found!"
  exit 0
elif [ -z "$SERVER_PID" ]; then
  echo "No vLLM-MLX server found, but found OpenCode server PID: $"
  OPENCODE_PID=$OPENCODE_PID
elif [ -z "$OPENCODE_PID" ]; then
  echo "vLLM-MLX server found with PID: $SERVER_PID, but no OpenCode process"
  OPENCODE_PID=""
else
  echo "Found vLLM-MLX server (PID: $SERVER_PID) and OpenCode (PID: $OPENCODE_PID)"
  SERVER_PID=$SERVER_PID
  OPENCODE_PID=$OPENCODE_PID
fi

# Kill processes if found
if [ -n "$SERVER_PID" ]; then
  echo "Killing vLLM-MLX server (PID $SERVER_PID)..."
  kill -9 $SERVER_PID 2>/dev/null
  echo "Server killed (PID $SERVER_PID)"
fi

if [ -n "$OPENCODE_PID" ]; then
  echo "Killing OpenCode process (PID $OPENCODE_PID)..."
  kill -9 $OPENCODE_PID 2>/dev/null
  echo "OpenCode killed (PID $OPENCODE_PID)"
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
  echo "Warning: Some OpenCode process(es) still running, killing..."
  pgrep -f "claude.*--model.*mlx" 2>/dev/null | xargs -r kill -9 2>/dev/null
fi

# Cleanup log files from the last 5 minutes
find /tmp -name "vllm_mlx_*.log" -mmin -5 -delete 2>/dev/null

echo ""
echo "Done!"