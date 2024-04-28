#!/bin/bash

# Update system packages
sudo apt-get update

# Install Python and pip
sudo apt-get install -y python3 python3-pip

# Install virtualenv
pip3 install virtualenv

# Create a virtual environment and activate it
cd /home/ubuntu/noiser
virtualenv venv
source venv/bin/activate

# Install the required Python packages
pip install flask sounddevice numpy

# Create a systemd service file for the Flask application
echo "[Unit]
Description=Noiser Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/noiser
Environment='FLASK_APP=noiser.py'
Environment='FLASK_RUN_HOST=0.0.0.0'
Environment='FLASK_RUN_PORT=5000'
ExecStart=/home/ubuntu/noiser/venv/bin/flask run
Restart=always

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/noiser.service

# Enable and start the service
sudo systemctl enable noiser
sudo systemctl start noiser