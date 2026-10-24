#!/bin/bash
set -euo pipefail
cat > /etc/systemd/system/cloud-notes.service <<'UNIT'
[Unit]
Description=Cloud Notes CI/CD practice application
After=network.target

[Service]
User=cloudnotes
Group=cloudnotes
WorkingDirectory=/opt/cloud-notes
Environment=APP_VERSION=deployed
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/cloud-notes/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:8000 app:app
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable cloud-notes.service
systemctl restart cloud-notes.service
