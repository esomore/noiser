#!/bin/bash

# Create a new user
sudo useradd -m -s /bin/bash noiser

# Update system packages
sudo apt-get update

# Install Python and pip
sudo apt-get install -y python3 python3-pip

# Install virtualenv
pip3 install virtualenv

# Create a virtual environment and activate it
cd /home/noiser/noiser
sudo -u noiser virtualenv venv

# Install the required Python packages
sudo -u noiser venv/bin/pip install flask pyaudio wave audioop

# Create a systemd service file for the Flask application
echo "[Unit]
Description=Noiser Service
After=network.target

[Service]
User=noiser
WorkingDirectory=/home/noiser/noiser
Environment='FLASK_APP=noiser.py'
Environment='FLASK_RUN_HOST=0.0.0.0'
Environment='FLASK_RUN_PORT=8080'
ExecStart=/home/noiser/noiser/venv/bin/flask run
Restart=always

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/noiser.service

# Set permissions for the noiser directory
sudo chown -R noiser:noiser /home/noiser/noiser

# Enable and start the service
sudo systemctl enable noiser
sudo systemctl start noiser