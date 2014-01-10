#!/bin/bash
# this script should be run to add a package to the repository
# For example to add the postgis and php5-pgsql package to the repository type

# > add-package.sh  postgis php5-pgsql

# the packages and all his dependency will be added to the
# repository $ALL_PACKAGE_REPO an update directory will be created
# an update directory  will be created in UPDATE_PACKAGE_REPO
# together with a zipfile containing the updates
 
. ./config

PACKAGES=$*
PACKAGES_STR=$(echo ${PACKAGES[@]} | sed 's/\ /-/g')
UPDATE_NAME="$(date +%Y-%m-%d-%H:%M)_${PACKAGES_STR}"

##echo $UPDATE_NAME

UPDATE_DIR=$UPDATE_PACKAGE_REPO/$UPDATE_NAME
SIG_FILE=$UPDATE_PACKAGE_LISTS/${UPDATE_NAME}.sig

mkdir -p $UPDATE_DIR

sudo apt-offline set $SIG_FILE --install-packages $PACKAGES

if [ ! -s $SIG_FILE ]; then
	rm $SIG_FILE
	echo "No packages added. Please check that the package name is corret and if it is not already installed on this system. Exit"
	exit
fi

#download to UPDATE_DIR, sync to ALL_PACKAGE_REPO and update the repo index
sudo apt-offline get $UPDATE_PACKAGE_LISTS/${UPDATE_NAME}.sig -s /var/cache/apt/archives -d $UPDATE_DIR && rsync -av $UPDATE_DIR/ $ALL_PACKAGE_REPO/amd64/ && ./update-repository.sh

#create a zipfile with the updates -> TO BE MOVED for add-list-packages.sh ????? MC-09-01-2014
#sudo apt-offline get $UPDATE_PACKAGE_LISTS/${UPDATE_NAME}.sig -s /var/cache/apt/archives --bundle ${UPDATE_DIR}.zip

