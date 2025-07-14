#!/bin/bash

echo "🚀 Starting GAIA daemon container..."

# Step 1: Stop and remove existing container (if running)
docker-compose stop gaia_daemon >/dev/null 2>&1
docker-compose rm -f gaia_daemon >/dev/null 2>&1

# Step 2: Start the daemon container in detached mode
docker-compose up -d gaia_daemon

# Step 3: Wait for container to stabilize (optional sleep or healthcheck wait)
echo "⏳ Waiting for container to fully boot..."
sleep 5

# Step 4: Launch the external chat interface (from host into running container)
echo "💬 Launching external chat interface..."
python app/cognition/external_voice.py
