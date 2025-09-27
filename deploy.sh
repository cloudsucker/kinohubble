#!/bin/bash
set -e # exit immediately if a command exits with a non-zero status


# VARIABLES
APP_NAME="kinohubble"
PROJECT_DIR="/opt/$APP_NAME"
PYTHON_BIN="/usr/bin/python3"
SYSTEMD_FILE="/etc/systemd/system/$APP_NAME.service"


cd "$PROJECT_DIR"


# ===== UPDATE CODE =====
echo "Updating codebase from GitHub..."
git pull origin production


# ===== VIRTUAL ENV =====
echo "Checking for virtual environment..."
if [ ! -d ".venv" ] || [ ! -f ".venv/bin/activate" ]; then
  echo "Creating virtual environment..."

  # Устанавливаем python3-venv, если его нет
  if ! python3 -m venv --help >/dev/null 2>&1; then
    echo "python3-venv is missing. Installing..."
    sudo apt update
    sudo apt install -y python3-venv
  fi

  python3 -m venv .venv
fi


# ===== INSTALL REQUIREMENTS =====
echo "Installing requirements..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate


# ===== SYSTEMD UNIT =====
if [ ! -f "$SYSTEMD_FILE" ]; then
  echo "Creating systemd unit..."
  sudo tee $SYSTEMD_FILE > /dev/null <<EOL
[Unit]
Description=Litestar Kinohubble
After=network.target

[Service]
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
EOL

  sudo systemctl daemon-reload
  sudo systemctl enable $APP_NAME
  sudo systemctl start $APP_NAME
else
  echo "Restarting systemd unit..."
  sudo systemctl restart $APP_NAME
fi

echo "Kinohubble deployment completed successfully."