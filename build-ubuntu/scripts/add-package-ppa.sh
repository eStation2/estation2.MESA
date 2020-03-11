#!/bin/bash
# This script should be run to install a package from a PPA

# > add-package-ppa.sh  apache2 ondrej/php5

. ./config

PACKAGE=$1
PPA=$2
# Add PPA to apt
sudo add-apt-repository -y "ppa:${PPA}"
sudo apt-get update
NOW=$(date +%Y-%m-%d-%H-%M)

# check if package status file is empty, it should be empty during install process
if [ -s /var/lib/dpkg/status ]; then
	#it is not empty
	sudo cp /var/lib/dpkg/status /var/backups/dpkg.status.$NOW
	sudo echo -n "" > /var/lib/dpkg/status
fi
sudo apt-get install --reinstall -y -d $PACKAGE
# do the reverse operation
if [ ! -s /var/lib/dpkg/status ] && [ -s  /var/backups/dpkg.status.$NOW ]; then
	#it is  empty
	sudo cp  /var/backups/dpkg.status.$NOW /var/lib/dpkg/status
fi