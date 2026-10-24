#!/bin/bash
set -euo pipefail
APP_DIR="/opt/devops-status-dashboard"

# This project targets Amazon Linux 2023 on EC2.
dnf install -y python3 python3-pip
python3 -m venv "${APP_DIR}/venv"
"${APP_DIR}/venv/bin/pip" install --upgrade pip
"${APP_DIR}/venv/bin/pip" install -r "${APP_DIR}/requirements.txt"

# Create a dedicated, unprivileged runtime user.
id -u dashboardapp >/dev/null 2>&1 || useradd --system --home-dir "${APP_DIR}" --shell /sbin/nologin dashboardapp
chown -R dashboardapp:dashboardapp "${APP_DIR}"
chmod 755 "${APP_DIR}/scripts"/*.sh
