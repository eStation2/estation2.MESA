#!/bin/bash
# this script is 
# - updating the cd repository with
# the files in the packages repository

. ./config

#update cd image dirs
rsync -av $GITDIR/build/CD_IMAGE/ $CD_BUILD_DIR/

#update Python Packages dir
rsync -av $PYTHON_PACKAGE_REPO $CD_BUILD_DIR/eStation

