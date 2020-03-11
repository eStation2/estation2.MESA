#!/bin/bash
#
#	Script to initialize bucardo DB, configure it and create syncs
#	This configuration depends on pc2/pc3 and creates 2 'syncs' for each computer, i.e. the syncs for which the PC is 'source'
#	Usage: bucardo_config.sh <role>  (role is pc2 or pc3)
#	NOTE: The script has to be run after:
#			a. bucardo installation 
#			b. configuration of the network (and namely creation of hosts mesa-pc2 and mesa-pc3)
#			c. assignment of the PC role (as pc2 or pc3)
#
#

if [[ $# -ne 1 ]]; then
	echo 'Exactly 1 parameter is required: pc2/pc3'
	exit 1
fi

role=$1
echo "Role is: $role"

#echo "NOTE: the following definitions have to be changed for MESA Installation"
#echo "NOTE: they now refer to a TEST machine"
#echo "NOTE: consider using network hostname rather then IP addresses"

# Make sure bucardo directories exists
mkdir -p /var/run/bucardo
mkdir -p /var/log/bucardo

if [[ $role == 'pc2' ]]; then 
	ip_thispc=mesa-pc2
	ip_otherpc=mesa-pc3
	schema_to_sync=products
elif [[ $role == 'pc3' ]]; then 
	ip_thispc=mesa-pc3
	ip_otherpc=mesa-pc2
	schema_to_sync=analysis

else
	echo 'Wrong role given! Valid values: pc2/pc3'
	exit 1
fi

echo "$(date +'%Y-%m-%d %H:%M:%S') Configuration of bucardo"
echo "$(date +'%Y-%m-%d %H:%M:%S') Create bucardo objects"

# Install bucardo DB (already done in eStation-Apps postinst)
# bucardo install --batch --dbname estationdb --dbhost localhost --dbport 5432 --piddir /var/run/bucardo

# Create 'dbs'-> mesa_pc2 and mesa_pc3	
bucardo add db mesa_thispc dbname=estationdb host=${ip_thispc} port=5432
bucardo add all tables
bucardo add db mesa_otherpc dbname=estationdb host=${ip_otherpc} port=5432

# Create 'dbgroups'-> group_pc2 (pc2 
bucardo add dbgroup group_thispc mesa_thispc:source mesa_otherpc:target

bucardo add sync sync_thispc dbs=group_thispc tables=${schema_to_sync}.*

# Start
bucardo start

