#!/bin/bash
#echo "Starting container $(hostname)"
sleep 2
#export PYTHONPATH=$PYTHONPATH:'var/www/estation2'
python -c 'import webpy_esapp_helpers; webpy_esapp_helpers.importJRCRefWorkspaces(version=1)'
sleep 2
python -c 'from database.dbInstall.install_update_db_in_postgres_container import install_update_db; install_update_db()'
#/setup_pythonenvironment.sh
sleep 3
apache2ctl -D FOREGROUND
