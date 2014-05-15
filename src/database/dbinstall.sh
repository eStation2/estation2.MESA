#!/bin/sh

# Define a logfile
logfile=/var/log/eStation2/dbinstall.log
uname=$(uname -n)
echo "Machine Name = ${uname}" >> ${logfile}

# Operate only on PC2 - do nothing on PC3
if [ $uname == 'eStation-PS' ]; then

    # localhost reachable
    if [ "$(nc -v -z localhost 5432 2> /dev/null;echo $?)" = 0 ]; then
        echo "Postgresql is running" > ${logfile}
        # estationdb exists ?
        if [ ! "$(su postgres -c "psql -c 'select usename from pg_user'"|grep estation)" ];then
            echo "Create User and Database" >> ${logfile}
            su postgres -c psql << EOF
                CREATE USER estation;
                ALTER ROLE estation WITH CREATEDB;
                CREATE DATABASE estationdb WITH OWNER estation;
                ALTER USER estation WITH ENCRYPTED PASSWORD 'mesadmin';
                EOF
        fi

        if [ ! "$(su postgres -c "psql -d estationdb -c 'select * from products.mapset'" 2> /dev/null)" ];then
            #First install from scratch data
            echo "Create database structure" >> ${logfile}
            # End automatically added section
            psql -h localhost -U estation -d estationdb -f /srv/www/eStation2/database/dump_database_structure.sql >> ${logfile} 2>&1 << EOF
            mesadmin
            EOF

        fi

        # Update Tables (both for upgrade and installation from scratch)
        echo "Tables contents" >> ${logfile}
        psql -h localhost -U estation -d estationdb -f /srv/www/eStation2/database/dump_database_data.sql >> ${logfile} 2>&1 << EOF
        mesadmin
        EOF


        # End automatically added section
    fi # localhost reachable
# Operate only on PC2 - do nothing on PC3
else
  echo "eStation-EMMA machine: Do nothing" >> ${logfile}
fi
