#!/bin/bash

#fetch_files
wget -O owoi.py https://raw.githubusercontent.com/Lordsniffer22/fed/main/owoi.py

#del_files_from_docker container
docker exec -it adskit rm owoi.py

#copy the new file back to the docker container
docker cp owoi.py adskit:/app

#finally remove the py script.
sleep 3
rm -rf owoi.py
echo "RESTARTING THE CONTAINER"
sleep 5
docker restart adskit
