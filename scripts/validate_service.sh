#!/bin/bash
set -euo pipefail

for attempt in $(seq 1 12); do
  if curl --fail --silent http://127.0.0.1:8000/health; then
    echo
    echo "Health check passed."
    exit 0
  fi
  sleep 5
done

echo "Health check failed."
systemctl --no-pager --full status devops-dashboard.service || true
journalctl -u devops-dashboard.service --no-pager -n 80 || true
exit 1
