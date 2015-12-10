#!/bin/bash

# Actions executed when a PC (PC2/3) goes into Failover (recovery) mode

log_file=/eStation2/log/estation_failback.log

target='PC3::products'
echo "`date +'%Y-%m-%d %H:%M '`Target PC for data sync is: ${target}" >> ${log_file}

# Execute a full data sync
echo "`date +'%Y-%m-%d %H:%M '`Executing data sync" >> ${log_file}
rsync -CavK /data/processing/ ${target}
echo "`date +'%Y-%m-%d %H:%M '`Data sync finished" >> ${log_file}

# Execute a full db sync
echo "`date +'%Y-%m-%d %H:%M '`Executing db sync" >> ${log_file}
su - analyst -c "python /var/www/eStation2/apps/tools/full_db_sync.py"
echo "`date +'%Y-%m-%d %H:%M '`DB sync finished" >> ${log_file}

# Write settings to system_settings.ini
echo "`date +'%Y-%m-%d %H:%M '`Writing the settings to system_settings.ini" >> ${log_file}
system_file=/eStation2/settings/system_settings.ini
if [[ -f ${system_file} ]]; then
    sed -i "s|.*mode.=.*|mode = nominal|" ${system_file}
    sed -i "s|.*data_sync.=.*|data_sync = true|" ${system_file}
    sed -i "s|.*db_sync.=.*|db_sync = true|" ${system_file}
fi

