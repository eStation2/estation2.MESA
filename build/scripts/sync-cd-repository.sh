#!/bin/bash
# this script is updating the cd repository with
# the files in the packages repository

. ./config

#update repository package index (just to be sure)
./update-repository.sh

rsync -av $ALL_PACKAGE_REPO/ $CD_BUILD_DIR/eStation/repository/
rsync -av $PYTHON_PACKAGE_REPO/ $CD_BUILD_DIR/eStation/Python-Modules

