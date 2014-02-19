#!/bin/bash
# This script should be run to install a package from a PPA

# > inst-package-ppa.sh  apache2 ondrej/php5

. ./config

PACKAGE=$1
PPA=$2
# Add PPA to apt
sudo add-apt-repository "ppa:${PPA}"
sudo apt-get update

sudo apt-get install $PACKAGE

