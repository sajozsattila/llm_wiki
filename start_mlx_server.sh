#!/bin/bash

# Model name - define once, used by both vllm-mlx and claude
MODEL="mlx-community/Qwen3.5-9B-MLX-4bit"
# MODEL="mlx-community/gemma-4-e4b-it-4bit"
# MODEL="mlx-community/Qwopus3.5-9B-v3-4bit"

# Log file location in /tmp (cleared on system reboot)
LOG_VLLM_FILE="/tmp/vllm_mlx_$(date +%s).log"
LOG__OPENCODE_SERVER_FILE="/tmp/opencode_server_$(date +%s).log"

# Start vLLM-MLX serve in the background
# This starts the MLX model server that Claude will connect to
echo "Starting vLLM-MLX server with model: $MODEL..."
echo "Logs will be written to: $LOG_FILE"
vllm-mlx serve $MODEL \
  --port 8000 \
  --continuous-batching \
  --enable-auto-tool-choice \
  --tool-call-parser auto > "$LOG_VLLM_FILE" 2>&1 &

SERVER_PID=$!
echo "vllm-mlx PID: $SERVER_PID"

echo "Waiting for vLLM-MLX to be ready (20 seconds)..."
sleep 20
opencode serve  > "$LOG__OPENCODE_SERVER_FILE" 2>&1 &

SERVER_PID=$!
echo "opencode server PID: $SERVER_PID"
