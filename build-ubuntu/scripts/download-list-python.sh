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

this_dir=$(pwd)

# Make sure target dir exists
mkdir -p $PYTHON_PACKAGE_REPO 
# Move to target dir
cd $PYTHON_PACKAGE_REPO

# Loop over list and call pip
for package in ${LIST_PCKGS[@]}
do
echo "Package: " ${package}
	# Check if is commented
	if [[ ! ${package} =~ '#' ]];
	then 
        # Download to target dir
        pip install --download="./" ${package}
        # Create symbolic link version independent
        pack_fullname=$(ls ${package}*gz)
        pack_no_release=$(echo ${pack_fullname} | sed 's/[-\.][0-9]//g')
	cp "${pack_fullname}" "${pack_no_release}"
	fi
    # Remove locally create build dir
    rm -fr "./build"
done

cd ${this_dir}
