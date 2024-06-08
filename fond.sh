#!/bin/bash

# Create directory and navigate into it
mkdir -p /root/psiphon
cd /root/psiphon

# Download psiphond
rm -rf psiphond
wget https://github.com/mukswilly/psicore-binaries/raw/master/psiphond/psiphond
chmod +x psiphond

# Generate configuration
./psiphond -ip $(curl -4 ifconfig.co -sS) -protocol FRONTED=MEEK-OSSH:443 generate

# Create systemd service file
cat <<EOF > /etc/systemd/system/psiphond.service
[Unit]
Description=Psiphond Service
After=network.target

[Service]
ExecStart=/root/psiphon/psiphond run -config /root/psiphon/psiphond.config
Type=simple
WorkingDirectory=/root/psiphon/
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
systemctl enable psiphond.service
systemctl start psiphond.service

# Check the status of the service
systemctl status psiphond.service

# Clear the screen and display the server entry data
clear
cat /root/psiphon/server-entry.dat
