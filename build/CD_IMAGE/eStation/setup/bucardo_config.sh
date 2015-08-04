#!/bin/bash
#
#	Script to configure bucardo installation and create syncs
#	This configuration is identical on pc2 and pc3 and creates 4 'syncs'	
#	
#		sync-pc2-analisys	-> to be run on pc2
#		sync-pc2-products
#
#		sync-pc3-analisys	-> to be run on pc3
#		sync-pc3-products
#

echo "NOTE: the following definitions have to be changed for MESA Installation"
echo "NOTE: they now refer to a TEST machine"
echo "NOTE: consider using network hostname rather then IP addresses"
ip_base=10.191.231.0
ip_pc2=10.191.231.89
ip_pc3=10.191.231.90

echo "$(date +'%Y-%m-%d %H:%M:%S') Install bucardo from /media/cdrom"

file_tgz='Bucardo-5.3.1.tar.gz'
bucardo_tgz="/home/adminuser/${file_tgz}"
target_dir="/usr/lib/bucardo/"
run_dir="/var/run/bucardo/"
if [ -f ${bucardo_tgz} ]; then
	mkdir -p ${target_dir}
	echo "$(date +'%Y-%m-%d %H:%M:%S') Target directory ${target_dir} created"
	mkdir -p ${run_dir}
	echo "$(date +'%Y-%m-%d %H:%M:%S') Run directory ${run_dir} created"
	cp ${bucardo_tgz} ${target_dir}
	cd ${target_dir}
	gunzip ${file_tgz}
	tar -xvf "${file_tgz%.*}"	
	echo "$(date +'%Y-%m-%d %H:%M:%S') Bucardo files extracted"
	# Build the package
	cd Bucardo*
	perl Makefile.PL
	make 
	make install
	echo "$(date +'%Y-%m-%d %H:%M:%S') Bucardo package ready to install"
	# Install the package
	mkdir -p /var/log/bucardo
	bucardo install --dbhost localhost --batch
	echo "$(date +'%Y-%m-%d %H:%M:%S') Bucardo package installed"
	# Fix permissions in pg_hba.conf
	sed -i "s/local   all             all                                     peer/local   all             all                                     trust/" /etc/postgresql/9.3/main/pg_hba.conf
	echo  "host    all         all         ${ip_base}/24               trust" >> /etc/postgresql/9.3/main/pg_hba.conf

	sed -i "s/\#listen_addresses = 'localhost'.*/listen_addresses = '*'\# what IP address(es) to listen on;/" /etc/postgresql/9.3/main/postgresql.conf
else
	echo "$(date +'%Y-%m-%d %H:%M:%S') Error: bucardo .tgz ${bucardo_tgz} not found. Exit"
	exit 1
fi

echo "$(date +'%Y-%m-%d %H:%M:%S') Create bucardo objects"

# Create 'dbs'-> mesa-pc2 and mesa-pc2	
bucardo add db mesa_pc2 dbname=estationdb host=${ip_pc2} port=5432 user=bucardo
bucardo add db mesa_pc3 dbname=estationdb host=${ip_pc3} port=5432 user=bucardo
echo "$(date +'%Y-%m-%d %H:%M:%S') Databases mesa_pc2 and mesa_pc3 added."

# Create 'dbgroups'-> group-pc2 (pc2 source) 
# 		   -> group-pc3 (pc3 source) 
bucardo add dbgroup group_pc2 mesa_pc2:source mesa_pc3:target
bucardo add dbgroup group_pc3 mesa_pc3:source mesa_pc2:target

# Create 'relgroups' -> rel_analysis: all tables of 'analysis' schema
#	 		rel_products_config: products tables for configuration by User (no static defs)

bucardo add relgroup rel_analysis analysis.i18n
bucardo add relgroup rel_analysis analysis.languages
bucardo add relgroup rel_analysis analysis.layers
bucardo add relgroup rel_analysis analysis.legend
bucardo add relgroup rel_analysis analysis.legend_step
bucardo add relgroup rel_analysis analysis.product_legend
bucardo add relgroup rel_analysis analysis.timeseries_drawproperties

bucardo add relgroup rel_products_config products.datasource_description
bucardo add relgroup rel_products_config products.eumetcast_source
bucardo add relgroup rel_products_config products.ingestion
bucardo add relgroup rel_products_config products.internet_source
bucardo add relgroup rel_products_config products.process_product
bucardo add relgroup rel_products_config products.processing
bucardo add relgroup rel_products_config products.product
bucardo add relgroup rel_products_config products.product_acquisition_data_source
bucardo add relgroup rel_products_config products.product_category
bucardo add relgroup rel_products_config products.sub_datasource_description

echo "$(date +'%Y-%m-%d %H:%M:%S') Relgroups created."

# Create 'syncs' -> see header

bucardo add sync sync_pc2_analysis relgroup=rel_analysis dbs=group_pc2
bucardo add sync sync_pc3_analysis relgroup=rel_analysis dbs=group_pc3
bucardo add sync sync_pc2_products relgroup=rel_products_config dbs=group_pc2 type=pushdelta
bucardo add sync sync_pc3_products relgroup=rel_products_config dbs=group_pc3

echo "$(date +'%Y-%m-%d %H:%M:%S') Rsyncs created."

# Start bucardo
bucardo start
echo "$(date +'%Y-%m-%d %H:%M:%S') Bucardo started."

# De-activate every rsync
bucardo deactivate sync_pc2_analysis
bucardo deactivate sync_pc3_analysis
bucardo deactivate sync_pc2_products
bucardo deactivate sync_pc3_products

echo "$(date +'%Y-%m-%d %H:%M:%S') Rsyncs de-activated."

