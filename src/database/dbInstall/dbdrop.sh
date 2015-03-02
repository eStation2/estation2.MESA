#!/bin/sh

#
#	Drop eStation database and delete estation user
#

# Define a logfile
logfile=/var/log/eStation2/dbdrop.log
uname=$(uname -n)
echo "Machine Name = ${uname}" >> ${logfile}

# localhost reachable
if [ "$(nc -v -z localhost 5432 2> /dev/null;echo $?)" = 0 ]; then
    echo "Postgresql is running" >> ${logfile}
    # estationdb exists ?
    if [ "$(su postgres -c "psql -l |grep estation")" ];then

        echo "Drop Database" >> ${logfile}
        su postgres -c psql << EOF
DROP DATABASE estationdb;
EOF
    else 
        echo "Database do not exist. Continue" >> ${logfile}
    fi
	
    if [ "$(su postgres -c "psql -c 'select usename from pg_user'"|grep estation)" ];then

        echo "Drop User" >> ${logfile}
        su postgres -c psql << EOF
DROP USER estation;
EOF
    else
        echo "User estation does not exist. Continue" >> ${logfile}
    fi

fi # localhost reachable

