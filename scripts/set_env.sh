#!/bin/sh
#	To be executed on BUILD machine (before retrieving the list of debian packages)
#	sudo set_env.sh
#
. ./config

CDIMAGE=$(grep  $CD_BUILD_DIR /etc/apt/sources.list)

echo "INFO - looking for $CD_BUILD_DIR in sources.list"

if [ "$CDIMAGE" = "" ]; then

echo "INFO - adding cd image to sources.list, this should be the first entry"
echo "deb file:$CD_BUILD_DIR/ precise main restricted\n$(cat /etc/apt/sources.list)" > /etc/apt/sources.list
else
 echo ".. ok"
fi


# This is for having add-apt-repository
apt-get install python-software-properties

# Add the source (and key) for postgresql 9.3
if [ ! -e "/etc/apt/sources.list.d/pgdg.list" ]; then
	echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" > /etc/apt/sources.list.d/pgdg.list
	wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc |   sudo apt-key add -
fi



# Update apt-get
apt-get update

