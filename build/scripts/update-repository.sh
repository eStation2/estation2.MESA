#!/bin/bash
# update repository package inxed

. ./config

cd $ALL_PACKAGE_REPO

REPO_ARCH=amd64
dpkg-scanpackages $REPO_ARCH /dev/null > $REPO_ARCH/Packages
bzip2 -kf $REPO_ARCH/Packages
