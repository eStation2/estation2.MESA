#!/bin/bash

export PGPASSWORD='mesadmin'

psql -h postgres -U estation -d estationdb -w -f /var/tmp/products_dump_structure_only.sql >/var/log/eStation2/products_dump_structure_only.log 2>/var/log/eStation2/products_dump_structure_only.err

psql -h postgres -U estation -d estationdb -w -f /var/tmp/update_db_structure.sql >/var/log/eStation2/update_db_structure.log 2>/var/log/eStation2/update_db_structure.err

psql -h postgres -U estation -d estationdb -w -f /var/tmp/online_old_h05estationdru7_data.sql >/var/log/eStation2/online_old_h05estationdru7_data.log 2>/var/log/eStation2/online_old_h05estationdru7_data.err

psql -h postgres -U estation -d estationdb -w -f /var/tmp/update_insert_jrc_data.sql >/var/log/eStation2/update_insert_jrc_data.log 2>/var/log/eStation2/update_insert_jrc_data.err

