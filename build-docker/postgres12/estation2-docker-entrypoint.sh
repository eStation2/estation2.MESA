#!/usr/bin/env bash

#  /bin/bash

# This script will run as the postgres user due to the Dockerfile USER directive
# set -e
echo "Starting container postgres"
sleep 3
source /root/setup_estationdb.sh
# sleep 3
# /etc/init.d/postgresql restart

# set -e
# internal start of server in order to allow set-up using psql-client
# does not listen on external TCP/IP and waits until start finishes
# pg_ctl -D "/var/lib/postgres/data" -o "-c listen_addresses=''" -w start
# source /setup_estationdb.sh