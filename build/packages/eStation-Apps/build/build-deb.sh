#!/bin/bash

# Package description
Project=eStation-
Name=eStation-Apps
Version=2.0.0
Release=1

# this is the destination folder for app sorces, this is specific for this package
APP_SOURCE_DESTINATION=/srv/www/eStation

#package destination dir usually ${PACKAGE_BUILD_DIR_DEB} but it can be a subdirectory with timestamp
PACKAGE_DESTINATION_DIR=${PACKAGE_BUILD_DIR_DEB}
#this is the deb package name
PACKAGE_DEB_NAME=${Name}-${Version}-${Release}.deb

## Tests before 'local-build'
#status=($(git status | grep modified))
#if [ ! -z ${status[0]} ]; then
#    echo "ERROR - Local modifications exist: commit/pull/push first"
#    git status
#    exit
#fi

# Source config file and debian build functions
# using relative path by now
. ../../../scripts/config
. ../../debianbuild

set -e

localdir=$(pwd)
# where the package is assembled
BUILDdir=${PACKAGE_BUILD_DIR_TMP}/tmp/${Name}-${Version}

# Cleaning
deb_clean ${BUILDdir}

mkdir -p ${BUILDdir}/${APP_SOURCE_DESTINATION}
cp -r ./src/* ${BUILDdir}
cp -r ${ESTATION_SRC_DIR}/* ${BUILDROOTDIR}/${APP_SOURCE_DESTINATION}
cp -r ./DEBIAN ${BUILDdir}


############################
# Parsing for build
############################
ver=$(echo ${Version}|sed 's/\./_/g')
perl -p -i -e "s#<INSTALLDIR>#${installdir}#g" ${BUILDdir}/DEBIAN/*
perl -p -i -e "s#<VINSTALLDIR>#${vinstalldir}#g" ${BUILDdir}/DEBIAN/*
perl -p -i -e "s/<VERSION>/${Version}/g" ${BUILDdir}/DEBIAN/*
perl -p -i -e "s/<RELEASE>/${Release}/g" ${BUILDdir}/DEBIAN/*
perl -p -i -e "s/<NAME>/${Name}/g" ${BUILDdir}/DEBIAN/*
cd ${BUILDdir}
find . -type f|grep -v svn |grep -v DEBIAN > ${BUILDdir}/DEBIAN/conffiles
cd -
cd ${localdir}

##########################
# Making DEB file
##########################
# $1 package source dir
# $2 package dest dir
# $3 package filename
make_deb ${BUILDdir} ${PACKAGE_DESTINATION_DIR} ${PACKAGE_DEB_NAME}
#change_debname



read -p "Sync ${PACKAGE_DESTINATION_DIR} to $ALL_PACKAGE_REPO/amd64/ and update repository index (y/N)? " ANS
if [ "$ANS" == "y" ]; then
  echo "INFO - sync  ${PACKAGE_DESTINATION_DIR}";
  rsync -av  --include="*.deb" --exclude="*" ${PACKAGE_DESTINATION_DIR}/ $ALL_PACKAGE_REPO/amd64/ 
  $SCRIPTS_DIR/update-repository.sh
fi
