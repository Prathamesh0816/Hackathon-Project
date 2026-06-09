#!/bin/sh
set -e

ollama serve &
OLLAMA_PID=$!

echo "Waiting for Ollama server..."
until ollama list >/dev/null 2>&1; do
  sleep 1
done
echo "Ollama server is ready."

MODEL="${OLLAMA_MODEL:-qwen2.5:3b}"
echo "Checking model: $MODEL"
if ollama list | grep -q "$MODEL"; then
  echo "Model $MODEL is already available."
else
  echo "Pulling model: $MODEL"
  ollama pull "$MODEL"
fi

wait "$OLLAMA_PID"
