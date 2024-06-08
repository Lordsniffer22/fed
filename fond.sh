#!/bin/bash
mkdir psiphon
cd psiphon
wget https://github.com/mukswilly/psicore-binaries/raw/master/psiphond/psiphond
chmod +x psiphond
./psiphond -ip curl -4 ifconfig.co -sS -protocol FRONTED=MEEK-OSSH:443 generate

./psiphond run

cat <<EOF > /etc/systemd/system/psiphond.service
[Unit]
After=network.target
[Service]
ExecStart=/root/psiphon/psiphond
run
Type=simple
WorkingDirectory=/root/psiphon/
[install]
WantedBy=default.target
EOF

systemctl enable psiphond.service
systemctl start psiphond.service
systemctl status psiphond.service
clear
cat server-entry.dat
