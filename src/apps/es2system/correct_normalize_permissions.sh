#!/bin/bash
# Correct and Normalize permission of the ingest and processing folder after the debug run.
# This scrip as to be executed as ROOT (e.g. from its crontab)
# Ticket ES2-262 Correct/normalize permissions
#
old_user='adminuser'
new_user='analyst'

# tmp dir
dir='/tmp/eStation2/'
find -L ${dir} -user ${old_user} -exec chown ${new_user}:estation {} \; -exec chmod 775 {} \;

# eStation2 dir
dir='/eStation2/'
find -L ${dir} -user ${old_user} -exec chown ${new_user}:estation {} \; -exec chmod 775 {} \;

# data dir
dir='/data/'
find -L ${dir} -user ${old_user} -exec chown ${new_user}:estation {} \; -exec chmod 775 {} \;

# Change permissions /var/www/ (for allowing analyst to change version)
# chmod 777 /var/www/

# Change permissions for writing in Desktop
#chown -R adminuser:adminuser /home/adminuser/*
#chmod -R 755 /home/adminuser/Desktop
#chown -R analyst:analyst /home/analyst/*
#chmod -R 755 /home/analyst/Desktop

# Change permissions of the Layers dir (2.0.4) -> it is done in layers-2.0.4
#echo "`date +'%Y-%m-%d %H:%M '` Change permissions of /eStation2/layers to 775"
#chmod 775 -R /eStation2/layers
