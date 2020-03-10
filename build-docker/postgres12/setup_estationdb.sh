#!/bin/bash

export PGPASSWORD='mesadmin'

if [[ `su postgres -c "psql -c 'select version from products.db_version'"  2>/dev/null` < ${DB_VERSION} ]];then
  echo "`date +'%Y-%m-%d %H:%M '` Create estationdb Database"

  if [[ ! `su postgres -c "psql -d estationdb -c 'select * from products.mapset'" 2> /dev/null` ]];then
      # First install from scratch data
      echo "`date +'%Y-%m-%d %H:%M '` Create database structure"
      # Create database initial version (2.0.2)
      # psql -h postgres -U estation -d estationdb -f /var/tmp/products_dump_structure_only.sql >/dev/null 2>&1
      psql -h postgres -U estation -d estationdb -w -f /var/tmp/products_dump_structure_only.sql >/var/log/eStation3/products_dump_structure_only.log 2>/var/log/eStation3/products_dump_structure_only.err
  else
      echo "`date +'%Y-%m-%d %H:%M '` Database structure already exists. Continue"
  fi
  # Update database structure to current release
  echo "`date +'%Y-%m-%d %H:%M '` Update database structure"
  psql -h postgres -U estation -d estationdb -w -f /var/tmp/update_db_structure.sql >/var/log/eStation3/update_db_structure.log 2>/var/log/eStation3/update_db_structure.err

  # psql -h postgres -U estation -d estationdb -w -f /var/tmp/online_old_h05estationdru7_data.sql >/var/log/eStation2/online_old_h05estationdru7_data.log 2>/var/log/eStation2/online_old_h05estationdru7_data.err

  # Update Tables (both for upgrade and installation from scratch)
  echo "`date +'%Y-%m-%d %H:%M '` Populate/update tables"
  psql -h postgres -U estation -d estationdb -w -f /var/tmp/update_insert_jrc_data.sql >/var/log/eStation3/update_insert_jrc_data.log 2>/var/log/eStation3/update_insert_jrc_data.err
else
  echo "`date +'%Y-%m-%d %H:%M '` DB estationdb already uptodate. Continue"
fi
