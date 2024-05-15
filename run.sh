#!/bin/bash
#This is a docker installer for Ubuntu 
#Scripted by OWORI NICHOLOUS
print_pink() {
    echo -e "\e[1;95m$1\e[0m"
}
sudo apt update
sudo apt upgrade

#INSTALL PACKAGES
sudo apt-get install curl apt-transport-https ca-certificates software-properties-common
#docker repositories add
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

#update again
sudo apt update
#check if docker-ce is installed already
apt-cache policy docker-ce

#install docker now
sudo apt install docker-ce
sleep 3
clear
print_pink 'DOCKER HAS BEEN INSTALLED SUCCESSFULLY'

wget -O pydm.py https://raw.githubusercontent.com/Lordsniffer22/fed/main/pydm.py
wget -O requirements.txt https://raw.githubusercontent.com/Lordsniffer22/fed/main/requirements.txt

echo "# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set the environment variables (if any)
ENV TOKEN=7167940962:AAGhsvvZ0RmAitj0uxaODW-shBbiaynTYp4

# Command to run the application
CMD ["python3", "pydm.py"]
" > dockerfile
fetch_files
#make docker image
docker build -t pydm_image .

#Run the docker container from image
docker run -d --name TubyDoo --restart unless-stopped pydm_image


rm -rf dockerfile pydm.py requirements.txt
