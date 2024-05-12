#!/bin/bash
wget -O pydm.py https://raw.githubusercontent.com/Lordsniffer22/fed/main/pydm.py
wget -O .env https://raw.githubusercontent.com/Lordsniffer22/fed/main/.env
wget -O requirements.txt https://raw.githubusercontent.com/Lordsniffer22/fed/main/requirements.txt
echo "TOKEN= 7167940962:AAGhsvvZ0RmAitj0uxaODW-shBbiaynTYp4" > .env
pip install -r requirements.txt
nohup python3 pydm.py
