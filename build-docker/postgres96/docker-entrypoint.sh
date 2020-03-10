#!/bin/bash

# set -e

# internal start of server in order to allow set-up using psql-client
# does not listen on external TCP/IP and waits until start finishes
# pg_ctl -D "/var/lib/postgres/data" -o "-c listen_addresses=''" -w start

source /setup_estationdb.sh