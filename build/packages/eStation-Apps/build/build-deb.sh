#!/bin/bash

echo "Script not yet finished! Exiting.."
exit

# Package description
Project=eStation-
Name=Apps
Version=2.0.0
Release=1

# Tests before 'local-build'
status=($(git status | grep modified))
if [ ! -z ${status[0]} ]; then
    echo "ERROR - Local modifications exist: commit/pull/push first"
    git status
    exit
fi

# Source config file and debian build functions
. ~/home/esuser/eStation2/build/scripts/config
. ~/home/esuser/eStation2/build/packages/debianbuild

set -e

localdir=$(pwd)
installdir=/
vinstalldir=/
BUILDdir=${builddir}/${Name}-${Version}
BUILDROOTDIR=${BUILDdir}/${installdir}

# Clean build directories
clean

#############################
# Make the build directories
#############################
#exportSVN http://e-station.glab.fr.cr
mkdir -p ${BUILDROOTDIR}
#cp -r ${BUILDdir}_SVN/src/* ${BUILDROOTDIR}
#cp -r ${BUILDdir}_SVN/build/DEBIAN ${BUILDdir}
# DEBUG
cp -r ${localbuild}/trunk/InstallCD/Add-on/amesd-systems/src/* ${BUILDROOTDIR}
cp -r ${localbuild}/trunk/InstallCD/Add-on/amesd-systems/build/DEBIAN ${BUILDdir}
find ${BUILDdir} -name ".svn" | while read rep; do
        rm -rf $rep
done

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
make_deb
change_debname
# Cleaning
#clean

