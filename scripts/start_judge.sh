#!/bin/sh
# Start Docker daemon (Docker-in-Docker), then Celery worker.
# Used on Fly.io where host Docker socket is not available.
set -e

# Start dockerd in background (vfs driver works without privileged mode)
dockerd --storage-driver vfs &
DOCKERD_PID=$!

# Wait for Docker daemon to be ready
echo "Waiting for Docker daemon..."
for i in 1 2 3 4 5 6 7 8 9 10; do
  if docker info >/dev/null 2>&1; then
    echo "Docker daemon ready."
    break
  fi
  if [ "$i" = "10" ]; then
    echo "Docker daemon failed to start."
    exit 1
  fi
  sleep 2
done

# Run Celery worker (foreground)
exec celery -A app.celery_app:celery_app worker -l info
