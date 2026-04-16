#!/bin/bash

# Model name - define once, used by both vllm-mlx and claude
MODEL="mlx-community/Qwen3.5-9B-MLX-4bit"
# MODEL="mlx-community/gemma-4-e4b-it-4bit"

# Log file location in /tmp (cleared on system reboot)
LOG_FILE="/tmp/vllm_mlx_$(date +%s).log"

# Function to check if the server is ready
check_server_ready() {
  local response
  response=$(curl -s -X POST "http://localhost:8000/v1/messages" \
    -H "Content-Type: application/json" \
    -d "{\"model\": \"$MODEL\", \"max_tokens\": 256, \"messages\": [{\"role\": \"user\", \"content\": \"Hello!\"}]}" 2>/dev/null)

  # Check if response contains expected fields
  if echo "$response" | grep -q '"type":"message"' && echo "$response" | grep -q '"role":"assistant"'; then
    return 0
  else
    return 1
  fi
}

# Start vLLM-MLX serve in the background
# This starts the MLX model server that Claude will connect to
echo "Starting vLLM-MLX server with model: $MODEL..."
echo "Logs will be written to: $LOG_FILE"
vllm-mlx serve $MODEL \
  --port 8000 \
  --continuous-batching \
  --enable-auto-tool-choice \
  --tool-call-parser hermes > "$LOG_FILE" 2>&1 &

SERVER_PID=$!
echo "Server PID: $SERVER_PID"

echo "Waiting for vLLM-MLX to be ready (max 60 seconds)..."

# Poll with exponential backoff: check every 2 seconds, max 30 attempts (60 seconds total)
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
  sleep 2
  ATTEMPT=$((ATTEMPT + 1))

  if check_server_ready; then
    echo "Server is ready!"
    break
  fi

  if [ $((ATTEMPT * 2)) -gt 60 ]; then
    echo "ERROR: Server did not become ready within 60 seconds. Aborting."
    kill $SERVER_PID 2>/dev/null
    rm -f "$LOG_FILE"
    exit 1
  fi

  echo "  Waiting... attempt $ATTEMPT/${MAX_ATTEMPTS}"
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
  echo "ERROR: Server failed to start. Check logs at $LOG_FILE"
  kill $SERVER_PID 2>/dev/null
  rm -f "$LOG_FILE"
  exit 1
fi

# Configure environment variables for Claude to connect to local vLLM
echo "Configuring Claude to use local vLLM-MLX..."
export ANTHROPIC_BASE_URL=http://localhost:8000
export ANTHROPIC_API_KEY=not-needed

# Start Claude with the MLX model
echo "Starting Claude with model: $MODEL..."
claude --model "$MODEL"

# Cleanup: kill server and remove log file when done
echo "Cleaning up server..."
kill $SERVER_PID 2>/dev/null
rm -f "$LOG_FILE"

echo "Done. Server cleaned up."