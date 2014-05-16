#!/bin/sh

#
#   This is a test script used for cleaninf eStation db installation during pre/postinst testing
#

# --------------------------------------------------------------------------------------
#	Common Definitions
# --------------------------------------------------------------------------------------
# Define base dirs (to be moved somewhere else and sourced)
base_dir_db_data="/eStation2/dbdata/"	# it is to be on Disk1 (system)
base_dir_system="/srv/www/eStation2/"	# it is to be on Disk2 (system)
base_dir_data="/data/"			# it is to be on Disk2 (data)

# Drop the estationdb 
# localhost reachable ?
if [ "$(nc -v -z localhost 5432 2> /dev/null;echo $?)" = 0 ]; then
    echo "localhost reachable"
    su postgres -c psql << EOF
DROP DATABASE estationdb ;
EOF
fi

# Delete dbdata base dir
rm -fr "${base_dir_db_data}"
rm -f "$base_dir_system/database/version_*"
rm -fr "$base_dir_data/dbbackup"
