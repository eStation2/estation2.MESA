#!/bin/bash
# this script should be run to add a package from a PPA to the repository

# > add-package-ppa.sh  apache2 ondrej/php5

# the packages and all his dependency will be added to the
# repository $ALL_PACKAGE_REPO an update directory will be created
# an update directory  will be created in UPDATE_PACKAGE_REPO
# together with a zipfile containing the updates
 
. ./config

PACKAGE=$1
PPA=$2
PACKAGES_STR=$(echo ${PACKAGE[@]} | sed 's/\ /-/g')
UPDATE_NAME="$(date +%Y-%m-%d-%H:%M)_${PACKAGES_STR}"

##echo $UPDATE_NAME

UPDATE_DIR="$UPDATE_PACKAGE_REPO/$UPDATE_NAME<<<$PPA"
SIG_FILE=$UPDATE_PACKAGE_LISTS/${UPDATE_NAME}.sig

mkdir -p $UPDATE_DIR

# Add PPA to apt
sudo add-apt-repository "ppa:${PPA}"
sudo apt-get update

sudo apt-offline set $SIG_FILE --install-packages $PACKAGE

if [ ! -s $SIG_FILE ]; then
	rm $SIG_FILE
	echo "No packages added. Please check that the package name is corret and if it is not already installed on this system. Exit"
	exit
fi

#download to UPDATE_DIR, sync to ALL_PACKAGE_REPO and update the repo index
sudo apt-offline get $UPDATE_PACKAGE_LISTS/${UPDATE_NAME}.sig -s /var/cache/apt/archives -d $UPDATE_DIR && rsync -av $UPDATE_DIR/ $ALL_PACKAGE_REPO/amd64/ && ./update-repository.sh

#create a zipfile with the updates -> TO BE MOVED for add-list-packages.sh ????? MC-09-01-2014
#sudo apt-offline get $UPDATE_PACKAGE_LISTS/${UPDATE_NAME}.sig -s /var/cache/apt/archives --bundle ${UPDATE_DIR}.zip

