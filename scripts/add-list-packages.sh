#!/bin/bash
# This script should be run to add a complete list of packages to a repository
# The name of the list is passed as argument

# Usage: add-list-packages.sh  list_filename.txt

# Script can also add a specific PPA, in which case in the list the syntax below should be used:
# package_std1
# package_std2
# package_ppa1<<<ppa_definition

# The packages and all his dependency will be added to the repo
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
mkdir -p /var/cache/apt/archives_backup/
mv /var/cache/apt/archives/*deb /var/cache/apt/archives_backup/
echo "INFO - /var/cache/apt/archive_backup/ dir cleaned."

# Manage repo-subdir
LABEL=$(echo $LIST_FILE | sed 's/.txt//')
REPO_SUBDIR="$(date +%Y-%m-%d-%H:%M)_${LABEL}"
THIS_PACKAGE_REPO="${PACKAGE_REPO}_${REPO_SUBDIR}"

# Create a new base dir
mkdir -p ${THIS_PACKAGE_REPO}

echo "INFO - New package repo base-dir and subdirs created as ${THIS_PACKAGE_REPO}"

# Check the ${PACKAGE_REPO} is a symlink, and delete it. If it is a dir, exit.
if [ -h ${PACKAGE_REPO} ]; then
	rm ${PACKAGE_REPO}
else if [ -d ${PACKAGE_REPO} ]; then
	echo "ERROR - ${PACKAGE_REPO} is a dir. Exit"
	exit
     fi	
fi
ln -fs ${THIS_PACKAGE_REPO} ${PACKAGE_REPO}
# Make subdirs
mkdir ${UPDATE_PACKAGE_REPO}
mkdir ${UPDATE_PACKAGE_LISTS}
mkdir ${ALL_PACKAGE_REPO}

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
		./add-package-ppa.sh ${name} ${ppa}
	  else
		./add-package.sh ${package}
	  fi
	fi
done


