#!/bin/bash
set -euo pipefail
APP_DIR="/opt/cloud-notes"
dnf install -y python3 python3-pip
python3 -m venv "${APP_DIR}/venv"
"${APP_DIR}/venv/bin/pip" install --upgrade pip
"${APP_DIR}/venv/bin/pip" install -r "${APP_DIR}/requirements.txt"
id -u cloudnotes >/dev/null 2>&1 || useradd --system --home-dir "${APP_DIR}" --shell /sbin/nologin cloudnotes
chown -R cloudnotes:cloudnotes "${APP_DIR}"
