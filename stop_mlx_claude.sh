#!/bin/bash

# Stop script for vLLM-MLX server and Claude
# Usage: ./stop_mlx_claude.sh [PID]

# If no PID provided, try to find running processes
PID=$1

if [ -z "$PID" ]; then
  echo "No PID provided. Searching for running processes..."

  # Find vllm-mlx server process
  SERVER_PID=$(pgrep -f "vllm-mlx serve" 2>/dev/null | head -n 1)

  # Find Claude process
  CLAUDE_PID=$(pgrep -f "claude" 2>/dev/null | head -n 1)

  if [ -z "$SERVER_PID" ] && [ -z "$CLAUDE_PID" ]; then
    echo "No running vLLM-MLX server or Claude found!"
    exit 0
  elif [ -z "$SERVER_PID" ]; then
    echo "No vLLM-MLX server found, but found Claude PID: $CLAUDE_PID"
  elif [ -z "$CLAUDE_PID" ]; then
    echo "vLLM-MLX server found with PID: $SERVER_PID, but no Claude process"
  fi

  if [ -n "$SERVER_PID" ] || [ -n "$CLAUDE_PID" ]; then
    echo ""
    echo "Processes found:"
    echo "  vLLM-MLX server: $SERVER_PID"
    echo "  Claude: $CLAUDE_PID"
    echo ""
    echo "Press Ctrl+C to cancel or run with PID to stop immediately:"
    echo "  ./stop_mlx_claude.sh [PID]"
    read -p "> " -n 1 _
  fi
  exit 0
fi

echo "Stopping vLLM-MLX server and Claude..."
echo "Server PID: $PID"

# Kill the server (this will also kill any child processes like Claude)
kill -9 $PID 2>/dev/null

if [ $? -eq 0 ]; then
  echo "Server killed (PID $PID)"

  # Wait a moment for processes to terminate
  sleep 1

  # Check if any processes are still running
  remaining=$(pgrep -f "vllm-mlx serve" 2>/dev/null | wc -l)
  if [ "$remaining" -gt 0 ]; then
    echo "Warning: $remaining vLLM-MLX process(es) still running"
    # Kill remaining processes
    pgrep -f "vllm-mlx serve" 2>/dev/null | xargs -r kill -9 2>/dev/null
  fi

  # Check for Claude process (might have been started by the script)
  CLAUDE_PID=$(pgrep -f "claude.*--model.*mlx" 2>/dev/null | head -n 1)
  if [ -n "$CLAUDE_PID" ]; then
    echo "Killing Claude process (PID $CLAUDE_PID)..."
    kill -9 $CLAUDE_PID 2>/dev/null
  fi

  echo "Cleanup complete!"
else
  echo "Failed to kill process $PID"
  exit 1
fi

# Cleanup log file
LOG_FILE="/tmp/vllm_mlx_$(date +%s).log"
# Try to match and remove log files in the last 5 minutes
find /tmp -name "vllm_mlx_*.log" -mmin -5 -delete 2>/dev/null

echo "Log files cleaned up."
echo ""
echo "Done!"