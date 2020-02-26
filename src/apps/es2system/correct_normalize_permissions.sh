#!/bin/sh
# Correct and Normalize permission of the ingest and processing folder after the debug run.
# Ticket ES2-262 Correct/normalize permissions
# Since 25.11.19 include ES2-478: sanity check on the ingested/derived products

#chmod 755 -R /var/www/eStation2-%{version}

chown -R analyst:estation /tmp/eStation2/
chmod 775 -R /tmp/eStation2/

chown -R analyst:estation /eStation2/
chmod 775 -R /eStation2/

# Change owner of /data/
# echo "`date +'%Y-%m-%d %H:%M '` Assign /data to analyst User"
chown -R analyst:estation /data/
chmod 775 -R /data/

# Change permissions /var/www (for allowing analyst to change version)
# chmod 777 /var/www

# Change permissions for writing in Desktop
#chown -R adminuser:adminuser /home/adminuser/*
#chmod -R 755 /home/adminuser/Desktop
#chown -R analyst:analyst /home/analyst/*
#chmod -R 755 /home/analyst/Desktop

# Change permissions of the Layers dir (2.0.4) -> it is done in layers-2.0.4
#echo "`date +'%Y-%m-%d %H:%M '` Change permissions of /eStation2/layers to 775"
#chmod 775 -R /eStation2/layers

# Call also the sanity check routine, with -remove option
chmod 775 /var/www/eStation2/apps/es2system/sanity_check.sh
/var/www/eStation2/apps/es2system/sanity_check.sh remove
