#!/bin/bash

#fetch_files
wget -O bot_data.db https://raw.githubusercontent.com/Lordsniffer22/fed/main/dbs.db

#del_files_from_docker container
docker exec -it adskit rm bot_data.db

#copy the new file back to the docker container
docker cp bot_data.db adskit:/app

#finally remove the py script.
sleep 3
rm -rf bot_data.db
echo "REBOOTING SERVER"
sleep 5
reboot
