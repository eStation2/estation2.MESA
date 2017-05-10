#!/bin/sh

#
#	Drop and restore db tables
#
#	Input arguments: date of the files to restore: e.g. 2015-10-20
#

# Echo machine name
uname=$(uname -n)
echo "Machine Name = ${uname}" 

# Check the dump file exists
date_dump=$1
dump_structure='/var/www/eStation2/database/dbInstall/products_dump_structure_only.sql'
update_structure='/var/www/eStation2/database/dbInstall/update_db_structure.sql'
dump_analysis=$(ls /eStation2/db_dump/estationdb_analysis_"${date_dump}"*.sql)
dump_products=$(ls /eStation2/db_dump/estationdb_products_"${date_dump}"*.sql)

if [[ ! -f ${dump_analysis} ]]; then 
    echo "ERROR - no any, or more than 1, file found ${dump_analysis}"
    echo "${dump_analysis}"
    exit
fi
if [[ ! -f ${dump_products} ]]; then 
    echo "ERROR - no any, or more than 1, file found ${dump_products}"
    echo "${dump_products}"
    exit
fi

# localhost reachable
if [ "$(nc -v -z localhost 5432 > /dev/null 2>&1; echo $?)" = 0 ]; then
    echo "Postgresql is running" 
    # estationdb exists ?
    if [ "$(su postgres -c "psql -l |grep estation")" ];then

        echo "Drop Schema products" 
        psql  -U estation -h localhost -d estationdb -c "DROP SCHEMA products CASCADE;"

        echo "Drop Schema analysis" 
        psql  -U estation -h localhost -d estationdb -c "DROP SCHEMA analysis CASCADE;"
	
        echo "Re-build the schemas\' structure " 
	psql -d estationdb -h localhost -p 5432 -U estation -f ${dump_structure}

        echo "Update the schemas\' structure "
	psql -d estationdb -h localhost -p 5432 -U estation -f ${update_structure}

        echo "Restore Schema products"
	psql -d estationdb -h localhost -p 5432 -U estation -f ${dump_products}
	
        echo "Restore Schema analysis" 
	psql -d estationdb -h localhost -p 5432 -U estation -f ${dump_analysis}

    fi
fi # localhost reachable

