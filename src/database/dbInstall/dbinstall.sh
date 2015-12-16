#!/bin/sh

# Define a logfile
logfile=/var/log/eStation2/dbinstall.log
uname=$(uname -n)
echo "Machine Name = ${uname}" >> ${logfile}

# Operate only on PC2 - do nothing on PC3
# localhost reachable
if [ "$(nc -v -z localhost 5432 > /dev/null 2>&1;echo $?)" = 0 ]; then
    echo "Postgresql is running" > ${logfile}
    # estationdb exists ?
    if [ ! "$(su postgres -c "psql -c 'select datname from pg_database'"|grep estationdb)" ];then
        echo "Create User and Database" >> ${logfile}
        su postgres -c psql << EOF
            CREATE USER estation;
            ALTER ROLE estation WITH CREATEDB;            
	    CREATE DATABASE estationdb WITH OWNER estation TEMPLATE template0 ENCODING 'UTF8';
            ALTER USER estation WITH ENCRYPTED PASSWORD 'mesadmin';
EOF
    fi

    if [ ! "$(su postgres -c "psql -d estationdb -c 'select * from products.mapset'" 2> /dev/null)" ];then
        #First install from scratch data
        echo "Create database structure" >> ${logfile}
        # End automatically added section
        psql -h localhost -U estation -d estationdb -f /var/www/eStation2/database/dbInstall/products_dump_structure_only.sql >> ${logfile} 2>&1 << EOF
        mesadmin
EOF

    fi

    # Update Tables (both for upgrade and installation from scratch)
    echo "Tables contents" >> ${logfile}
    psql -h localhost -U estation -d estationdb -f /var/www/eStation2/database/dbInstall/products_dump_data_only.sql >> ${logfile} 2>&1 << EOF
    mesadmin
EOF


    # End automatically added section
fi # localhost reachable

