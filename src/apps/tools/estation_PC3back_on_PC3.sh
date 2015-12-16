#!/bin/bash

# Actions executed when a PC (PC2/3) goes into Failover (recovery) mode

log_file=/eStation2/log/estation_failback.log

# Write settings to system_settings.ini
echo "`date +'%Y-%m-%d %H:%M '`Writing the settings to system_settings.ini" >> ${log_file}
system_file=/eStation2/settings/system_settings.ini
if [[ -f ${system_file} ]]; then

    sed -i "s|.*mode.=.*|mode = nominal|" ${system_file}
    sed -i "s|.*data_sync.=.*|data_sync = false|" ${system_file}
    sed -i "s|.*db_sync.=.*|db_sync = true|" ${system_file}
fi

