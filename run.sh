#!/bin/bash
wget -O pydm.py https://raw.githubusercontent.com/Lordsniffer22/fed/main/pydm.py
wget -O .env https://raw.githubusercontent.com/Lordsniffer22/fed/main/.env
wget -O requirements.txt https://raw.githubusercontent.com/Lordsniffer22/fed/main/requirements.txt
pip install -r requirements.txt
python3 pydm.py
