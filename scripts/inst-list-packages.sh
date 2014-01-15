#!/bin/bash
# This script should be run to install a complete list of packages on a machine
# It correspond to add-list-packages.sh, but does the installation, rather then apt-offline download
#
# Usage: add-list-packages.sh  list_filename.txt
#
# Script can also add a specific PPA, in which case in the list the syntax below should be used in the list file:
#
# package_std1
# package_std2
# package_ppa1<<<ppa_definition

# NOTE that: 1. a subdirectory is created/used under PACKAGE_REPO
# 	     2. eventhough add-package.sh can be called with several args, a loop is preferred
#	
	
. ./config

LIST_FILE=$1

# Check arguments
if [ $# -lt 1 ]; then
	echo "ERROR - At least one argument must be provided"
	exit
fi

if [ ! -s $LIST_FILE ]; then
	echo "ERROR - List file does not exist OR is empty. Exit"
	exit
fi

# Empty /var/cache/apt/archives/ - but lock file
#mkdir -p /var/cache/apt/archives_backup/
#mv /var/cache/apt/archives/*deb /var/cache/apt/archives_backup/
#echo "INFO - /var/cache/apt/archive_backup/ dir cleaned."

# Load file into a variable
LIST_PCKGS=($(cat $LIST_FILE))

# Loop over list and call add-package.sh

for package in ${LIST_PCKGS[@]}
do
	# Check if is commented
	if [[ ! ${package} =~ '#' ]];
	then 
  	  # Check if a PPA is defined
	  if [[ ${package} =~ '<<<' ]]; 
	  then 
		name=${package%%<<<*}
		ppa=${package##*<<<}
		./inst-package-ppa.sh ${name} ${ppa}
	  else
		apt-get install ${package}
	  fi
	fi
done


