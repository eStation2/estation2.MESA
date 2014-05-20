#!/bin/bash
# This script should be run to download the python packages (.tgz) to be installed through pip.
# It has to be used for the python-modules for which the .deb package does not exist (e.g. pygrib)

# Usage: download-list-packages.sh

# The packages will be created under PYTHON_PACKAGE_REPO
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

# Load file into a variable
LIST_PCKGS=($(cat $LIST_FILE))

# Loop over list and call pip
for package in ${LIST_PCKGS[@]}
do
echo "Package: " ${package}
	# Check if is commented
	if [[ ! ${package} =~ '#' ]];
	then 
        # Make sure target dir exists
        mkdir -p $PYTHON_PACKAGE_REPO 
        # Download to target dir
        pip install --download="$PYTHON_PACKAGE_REPO" ${package}
        # Create symbolic link version independent
        pack_fullname=$(ls ${package}*)
        pack_no_release=$(echo ${package_fullname} | sed 's/[-\.][0-9]//g')
		ln -fs "$PYTHON_PACKAGE_REPO/${package}" "$PYTHON_PACKAGE_REPO/${pack_fullname}"
	fi
done

