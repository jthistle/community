#!/usr/bin/env bash

#sudo cp -a . /usr/lib/cgi-bin
sudo rsync -av --progress . /var/www/html/com --exclude install.sh --exclude __pycache__/
sudo rsync -av --progress ../ /var/www/html/com --exclude web/ --exclude saves/ --exclude __pycache__/ --exclude .git/
