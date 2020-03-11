#!/bin/bash
#
#	Script to reset all bucardo definitions: it is called during an upgrade, in order to have a clean starting point for the definition of new syncs, which 
#	should include the NEW added tables.		
#	Subsequenty, the bucardo_config.sh will be called by the 'System' services
#	Usage: bucardo_reset.sh <role>  (role is pc2 or pc3)
#	NOTE: The script has to be run after:
#			a. bucardo installation 
#			b. configuration of the network (and namely creation of hosts mesa-pc2 and mesa-pc3)
#			c. assignment of the PC role (as pc2 or pc3)
#
#

echo "$(date +'%Y-%m-%d %H:%M:%S') Resetting configuration of bucardo"

# Remove the bucardo schema from the estation DB
psql -h localhost -d estationdb -U postgres -c 'drop schema bucardo cascade'

# Remove all definitions 
bucardo remove tables all 
bucardo remove sync sync_thispc
bucardo remove dbgroup group_thispc
bucardo remove db mesa_otherpc --force
bucardo remove db mesa_thispc --force

relgroups=($(bucardo list relgroup | grep 'Relgroup' | awk   '{print $2}'))
for rel in  ${relgroups[@]}; do bucardo remove relgroup $rel; done

