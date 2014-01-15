#
#	To be executed on BUILD machine (before retrieving the list of debian packages)
#	sudo set_env.sh
#

# This is for having add-apt-repository
apt-get install python-software-properties

# Add the source (and key) for postgresql 9.3
if [ ! -e "/etc/apt/sources.list.d/pgdg.list" ]; then
	echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" > /etc/apt/sources.list.d/pgdg.list
fi
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc |   sudo apt-key add -

# Update apt-get
apt-get update

