#!/bin/bash
#
#	Script to initialize bucardo DB, configure it and create syncs
#	This configuration depends on pc2/pc3 and creates 2 'syncs' for each computer, i.e. the syncs for which the PC is 'source'
#	Usage: bucardo_config.sh 
#	NOTE: The script has to be run after:
#			a. bucardo installation 
#			b. configuration of the network (and namely creation of hosts mesa-pc2 and mesa-pc3)
#			c. assignment of the PC role (as pc2 or pc3)
#
#

logfile=/var/log/eStation2/bucardo_config.log

role=$(hostname)
echo "Role is: $role" > $logfile

#echo "NOTE: the following definitions have to be changed for MESA Installation"
#echo "NOTE: they now refer to a TEST machine"
#echo "NOTE: consider using network hostname rather then IP addresses"

# Make sure bucardo directories exists
mkdir -p /var/run/bucardo >> $logfile 2>&1
mkdir -p /var/log/bucardo >> $logfile 2>&1

if [[ $role == 'MESA-PC2' ]]; then 
	ip_thispc=MESA-PC2
	ip_otherpc=MESA-PC3
	schema_to_sync=products
elif [[ $role == 'MESA-PC3' ]]; then 
	ip_thispc=MESA-PC3
	ip_otherpc=MESA-PC2
	schema_to_sync=analysis

else
	echo 'Wrong role given! Valid values: pc2/pc3' >> $logfile 2>&1
	exit 1
fi

echo "$(date +'%Y-%m-%d %H:%M:%S') Configuration of bucardo" >> $logfile 2>&1
echo "$(date +'%Y-%m-%d %H:%M:%S') Create bucardo objects" >> $logfile 2>&1

# Install bucardo DB
bucardo install --batch --dbname estationdb --dbhost localhost --dbport 5432 --piddir /var/run/bucardo >> $logfile 2>&1

# Create 'dbs'-> mesa_pc2 and mesa_pc3	
bucardo add db mesa_thispc dbname=estationdb host=${ip_thispc} port=5432 >> $logfile 2>&1
bucardo add all tables	>> $logfile 2>&1
bucardo add db mesa_otherpc dbname=estationdb host=${ip_otherpc} port=5432 >> $logfile 2>&1

# Create 'dbgroups'-> group_pc2 (pc2 
bucardo add dbgroup group_thispc mesa_thispc:source mesa_otherpc:target >> $logfile 2>&1

bucardo add sync sync_thispc dbs=group_thispc tables=${schema_to_sync}.* >> $logfile 2>&1

# Start
bucardo start >> $logfile 2>&1

