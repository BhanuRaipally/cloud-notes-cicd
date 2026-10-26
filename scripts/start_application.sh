#!/bin/bash
set -euo pipefail
APP_DIR="/opt/devops-status-dashboard"

cat > /etc/systemd/system/devops-dashboard.service <<'UNIT'
[Unit]
Description=DevOps Status Dashboard Flask application
After=network.target

[Service]
User=dashboardapp
Group=dashboardapp
WorkingDirectory=/opt/devops-status-dashboard
Environment=APP_VERSION=ec2-deployment
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/devops-status-dashboard/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:8000 app:app
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable devops-dashboard.service
systemctl restart devops-dashboard.service
