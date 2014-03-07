#!/bin/bash
# This script should be run to install a package from a PPA

# > add-package-ppa.sh  apache2 ondrej/php5

. ./config

PACKAGE=$1
PPA=$2
# Add PPA to apt
sudo add-apt-repository -y "ppa:${PPA}"
sudo apt-get update

sudo apt-get install --reinstall -y -d $PACKAGE
