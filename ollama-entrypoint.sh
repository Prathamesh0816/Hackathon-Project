#!/bin/sh
set -e

# Start Ollama server in background
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama API to be ready
echo "Waiting for Ollama server..."
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
  sleep 1
done
echo "Ollama server is ready."

# Pull the default model (timeout after 5 min so stack still starts on slow networks)
MODEL="${OLLAMA_MODEL:-qwen2.5:3b}"
echo "Pulling model: $MODEL ..."
if timeout 300 ollama pull "$MODEL"; then
  echo "Model $MODEL pulled successfully."
else
  echo "WARNING: Model pull timed out. AI pipeline will use fallback templates."
  echo "Run manually: docker exec trupulse-ollama ollama pull $MODEL"
fi

# Keep container running
wait $OLLAMA_PID
