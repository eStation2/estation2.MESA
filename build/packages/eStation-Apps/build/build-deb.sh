#!/bin/bash

#
#   Script to create the eStation2-apps debian package
#   It also replaces placeholders in pre/postinst files

# Source the eStation2 specific definitions

. ./eStation2_config

Project=eStation-
Name=eStation-Apps
Version=2.0.4
Release=20

#this is the deb package name
PACKAGE_DEB_NAME=${Name}-${Version}-${Release}.deb

# Source config file and debian build functions
# using relative path by now
. ../../../scripts/config
. ../../debianbuild

#package destination dir usually ${PACKAGE_BUILD_DIR_DEB} but it can be a subdirectory with timestamp
PACKAGE_DESTINATION_DIR=${PACKAGE_BUILD_DIR_DEB}

set -e

localdir=$(pwd)

# where the package is assembled
BUILDdir=${PACKAGE_BUILD_DIR_TMP}/${Name}-${ESTATION2_VERSION}

# Cleaning
deb_clean ${BUILDdir}

mkdir -p ${BUILDdir}/${ESTATION2_BASE_DIR_SYSTEM}

cp -r ../src/* ${BUILDdir}/
cp -r ${ESTATION_SRC_DIR}/* ${BUILDdir}/${ESTATION2_BASE_DIR_SYSTEM}
cp -r ./DEBIAN ${BUILDdir}

############################
# Parsing preinst/postinst
############################
# Replace variables in preinst and postinst
for file in ${BUILDdir}/DEBIAN/preinst ${BUILDdir}/DEBIAN/postinst ${BUILDdir}/DEBIAN/control
do
for var in 'ESTATION2_VERSION' 'ESTATION2_RELEASE' 'ESTATION2_UBUNTU' 'ESTATION2_MAIN_USER' 'ESTATION2_THEM_USER' 'ESTATION2_MAIN_GROUP' 'ESTATION2_BASE_DIR_SYSTEM' 'ESTATION2_LOCAL_DIR' 'ESTATION2_DIR_LOG' 
do
    placeholder="<${var}>"
    value=$(eval "echo \$${var}")
    perl -p -i -e "s#${placeholder}#${value}#g" $file
done
done
for file in ${BUILDdir}/DEBIAN/preinst ${BUILDdir}/DEBIAN/postinst ${BUILDdir}/DEBIAN/control
do
for var in 'ESTATION2_DIR_LISTS' 'ESTATION2_DIR_SETTINGS' 'ESTATION2_DIR_LIST_EUM' 'ESTATION2_DIR_LIST_INT' 'ESTATION2_DIR_DATABASE' 
do
    placeholder="<${var}>"
    value=$(eval "echo \$${var}")
    perl -p -i -e "s#${placeholder}#${value}#g" $file
done
done

for file in ${BUILDdir}/DEBIAN/preinst ${BUILDdir}/DEBIAN/postinst ${BUILDdir}/DEBIAN/control
do
for var in 'ESTATION2_DIR_DATABASE' 'ESTATION2_TEMP_DIR' 'ESTATION2_DIR_SERVICES' 'ESTATION2_DIR_PROCESS' 'ESTATION2_BASE_DIR_DATA' 'ESTATION2_INST_LOG_DIR' 'ESTATION2_PYTHON_DIST_DIR'
do
    placeholder="<${var}>"
    value=$(eval "echo \$${var}")
    perl -p -i -e "s#${placeholder}#${value}#g" $file
done
done

############################
# Parsing for build
############################
ver=$(echo ${Version}|sed 's/\./_/g')
#perl -p -i -e "s#<INSTALLDIR>#${installdir}#g" ${BUILDdir}/DEBIAN/*
#perl -p -i -e "s#<VINSTALLDIR>#${vinstalldir}#g" ${BUILDdir}/DEBIAN/*
#perl -p -i -e "s/<VERSION>/${Version}/g" ${BUILDdir}/DEBIAN/*
#perl -p -i -e "s/<RELEASE>/${Release}/g" ${BUILDdir}/DEBIAN/*
#perl -p -i -e "s/<NAME>/${Name}/g" ${BUILDdir}/DEBIAN/*
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
  cd $SCRIPTS_DIR
  ./update-repository.sh
fi
