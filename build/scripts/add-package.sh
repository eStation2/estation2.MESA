#!/bin/bash
# this script should be run to add a package to the repository
# For example to add the postgis and php5-pgsql package to the repository type

# > add-package.sh  postgis php5-pgsql

# the packages and all his dependency will be added to the
# repository $ALL_PACKAGE_REPO an update directory will be created
# an update directory  will be created in UPDATE_PACKAGE_REPO
# together with a zipfile containing the updates


. ./config

read -p "Clean package cache in /var/cache/apt/archives/ (Y/n)? " ANS
if [ "$ANS" != "n" ]; then
  echo "INFO - cleaning /var/cache/apt/archives/";
  sudo apt-get clean
  sudo apt-get update
fi

NOW=$(date +%Y-%m-%d-%H-%M)
# check if package status file is empty, it should be empty during install process
if [ -s /var/lib/dpkg/status ]; then
	#it is not empty
	cp /var/lib/dpkg/status /var/backups/dpkg.status.$NOW
	echo -n "" > /var/lib/dpkg/status
fi

sudo apt-get install --reinstall -y -d $*

# do the reverse operation
if [ ! -s /var/lib/dpkg/status ] && [ -s  /var/backups/dpkg.status.$NOW ]; then
	#it is  empty
	cp  /var/backups/dpkg.status.$NOW /var/lib/dpkg/status
fi


#cp /var/cache/apt/archives/*.deb $UPDATE_DIR
read -p "Sync /var/cache/apt/archives/ to $ALL_PACKAGE_REPO/amd64/ (Y/n)? " ANS
if [ "$ANS" != "n" ]; then
  echo "INFO - sync /var/cache/apt/archives/";
  rsync -av  --include="*.deb" --exclude="*" /var/cache/apt/archives/ $ALL_PACKAGE_REPO/amd64/ 
fi


#&& ./update-repository.sh && ./sync-cd-repository.sh 