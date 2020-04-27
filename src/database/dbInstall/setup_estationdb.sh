#!/usr/bin/env bash


if [[ `su - postgres -c "psql postgres -d estationdb -c \"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'products' AND table_name = 'mapset') as x;\"" 2> /dev/null|grep t` == '' ]]; then
    # First install from scratch the database structure
    echo "`date +'%Y-%m-%d %H:%M '` Create database structure"
    # Create database initial version (2.0.2)
    psql -h postgres -U estation -d estationdb -w -f /var/www/eStation2/database/dbInstall/products_dump_structure_only.sql >/var/log/eStation2/products_dump_structure_only.log 2>/var/log/eStation2/products_dump_structure_only.err
else
    echo "`date +'%Y-%m-%d %H:%M '` Database structure already exists. Continue"
fi

if [[ `su - postgres -c "psql postgres -d estationdb -c \"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'products' AND table_name = 'db_version') as x;\""  2>/dev/null|grep t` == '' ]]; then
  # Table products.db_version does not exist so create it and set initial value to 2200
  echo "`date +'%Y-%m-%d %H:%M '` Create table products.db_version"
  psql -h postgres -U estation -d estationdb -w -f /var/www/eStation2/database/dbInstall/create_table_db_version.sql >/var/log/eStation2/create_table_db_version.log 2>/var/log/eStation2/create_table_db_version.err
else
    echo "`date +'%Y-%m-%d %H:%M '` Table products.db_version exists. Continue"
fi

if [[ `su - postgres -c "psql postgres -d estationdb -c \"select db_version from products.db_version;\""  2>/dev/null|grep -m1 -o '[0-9]\+'` < ${DB_VERSION} ]]; then
    # Update database structure to current release
    echo "`date +'%Y-%m-%d %H:%M '` Update database structure"
    psql -h postgres -U estation -d estationdb -w -f /var/www/eStation2/database/dbInstall/update_db_structure.sql >/var/log/eStation2/update_db_structure.log 2>/var/log/eStation2/update_db_structure.err

    # psql -h postgres -U estation -d estationdb -w -f /var/www/eStation2/database/dbInstall/online_old_h05estationdru7_data.sql >/var/log/eStation2/online_old_h05estationdru7_data.log 2>/var/log/eStation2/online_old_h05estationdru7_data.err

    # Update Tables (both for upgrade and installation from scratch)
    echo "`date +'%Y-%m-%d %H:%M '` Populate/update tables"
    psql -h postgres -U estation -d estationdb -w -f /var/www/eStation2/database/dbInstall/update_insert_jrc_data.sql >/var/log/eStation2/update_insert_jrc_data.log 2>/var/log/eStation2/update_insert_jrc_data.err

    # Activate the User THEMA in the thema table (since 2.1.0)
    thema=`grep -i thema /eStation2/settings/system_settings.ini | sed 's/thema =//'| sed 's/ //g'`
    psql -h postgres -U estation -d estationdb -w -c "update products.thema SET activated=TRUE WHERE thema_id='$thema'"
    echo "`date +'%Y-%m-%d %H:%M '` Thema activated in the products.thema table"

    # Update table products.db_version to value DB_VERSION
    psql -h postgres -U estation -d estationdb -w -c "update products.db_version SET db_version='${DB_VERSION}'"
else
  echo "`date +'%Y-%m-%d %H:%M '` DB estationdb already uptodate. Continue"
fi
