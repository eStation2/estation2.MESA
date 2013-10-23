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
UPDATE_NAME=$(date +%Y%m%d%H%M)

echo $UPDATE_NAME

UPDATE_DIR=$UPDATE_PACKAGE_REPO/$UPDATE_NAME

mkdir -p $UPDATE_DIR

sudo apt-offline set $UPDATE_PACKAGE_LISTS/${UPDATE_NAME}.sig --install-packages $PACKAGES

#download to UPDATE_DIR, sync to ALL_PACKAGE_REPO and update the repo index
sudo apt-offline get $UPDATE_PACKAGE_LISTS/${UPDATE_NAME}.sig -d $UPDATE_DIR && rsync -av $UPDATE_DIR/ $ALL_PACKAGE_REPO/amd64/ && ./update-repository.sh

#create a zipfile with the updates
sudo apt-offline get $UPDATE_PACKAGE_LISTS/${UPDATE_NAME}.sig --bundle ${UPDATE_DIR}.zip

