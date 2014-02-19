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


sudo apt-get install --reinstall -y -d $*

#cp /var/cache/apt/archives/*.deb $UPDATE_DIR
read -p "Sync /var/cache/apt/archives/ to $ALL_PACKAGE_REPO/amd64/ (Y/n)? " ANS
if [ "$ANS" != "n" ]; then
  echo "INFO - sync /var/cache/apt/archives/";
  rsync -av  --include="*.deb" --exclude="*" /var/cache/apt/archives/ $ALL_PACKAGE_REPO/amd64/ 
fi


#&& ./update-repository.sh && ./sync-cd-repository.sh 