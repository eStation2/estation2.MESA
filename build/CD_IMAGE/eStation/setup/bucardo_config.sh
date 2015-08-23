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
ip_pc2=10.191.231.89
ip_pc3=10.191.231.90

echo "$(date +'%Y-%m-%d %H:%M:%S') Install bucardo from /media/cdrom"

file_tgz='Bucardo-5.3.1.tar.gz'
bucardo_tgz="/media/cdrom/eStation2/Tarball/${file_tgz}"
target_dir="/usr/lib/bucardo/"
log_dir="/var/log/bucardo"
run_dir="/var/run/bucardo"

if [ -f ${bucardo_tgz} ]; then
	mkdir -p ${target_dir}
	echo "$(date +'%Y-%m-%d %H:%M:%S') Target directory ${target_dir} created"
	cp ${bucardo_tgz} ${target_dir}
	cd ${target_dir}
	gunzip ${file_tgz}
	tar -xvf "${file_tgz%.*}"	
	echo "$(date +'%Y-%m-%d %H:%M:%S') Bucardo files extracted"
	# Build the package
	perl Makefile.PL
	make 
	make install
	echo "$(date +'%Y-%m-%d %H:%M:%S') Bucardo package ready to install"
	# Install the package
	mkdir -p /var/log/bucardo
	bucardo install
	echo "$(date +'%Y-%m-%d %H:%M:%S') Bucardo package installed"
	# Create log and run dir
    mkdir -p ${log_dir}
    chown adminuser:estation ${log_dir}
    chmod 777 ${log_dir}
    mkdir -p ${run_dir}
    chown adminuser:estation ${run_dir}
    chmod 777 ${run_dir}
else
	echo "$(date +'%Y-%m-%d %H:%M:%S') Error: bucardo .tgz ${bucardo_tgz} not found. Exit"
	exit 1
fi

echo "$(date +'%Y-%m-%d %H:%M:%S') Create bucardo objects"

# Create 'dbs'-> mesa-pc2 and mesa-pc2	
bucardo add db mesa-pc2 dbname=estationdb host=${ip_pc2} port=5432 user=bucardo
bucardo add db mesa-pc3 dbname=estationdb host=${ip_pc3} port=5432 user=bucardo

# Create 'dbgroups'-> group-pc2 (pc2 source) 
# 		   -> group-pc3 (pc3 source) 
bucardo add dbgroup group-pc2 mesa-pc2:source mesa-pc3:target
bucardo add dbgroup group-pc3 mesa-pc3:source mesa-pc2:target

# Create 'relgroups' -> rel-analysis: all tables of 'analysis' schema
#	 		rel-products-config: products tables for configuration by User (no static defs)

bucardo add relgroup rel-analysis analysis.i18n
bucardo add relgroup rel-analysis analysis.languages
bucardo add relgroup rel-analysis analysis.layers
bucardo add relgroup rel-analysis analysis.legend
bucardo add relgroup rel-analysis analysis.legend_step
bucardo add relgroup rel-analysis analysis.product_legend
bucardo add relgroup rel-analysis analysis.timeseries_drawproperties

bucardo add relgroup rel-products-config products.datasource_description
bucardo add relgroup rel-products-config products.eumetcast_source
bucardo add relgroup rel-products-config products.ingestion
bucardo add relgroup rel-products-config products.internet_source
bucardo add relgroup rel-products-config products.process_product
bucardo add relgroup rel-products-config products.processing
bucardo add relgroup rel-products-config products.product
bucardo add relgroup rel-products-config products.product_acquisition_data_source
bucardo add relgroup rel-products-config products.product_category
bucardo add relgroup rel-products-config products.sub_datasource_description

# Create 'syncs' -> see header

bucardo add sync sync-pc2-analysis relgroup=rel-analysis dbs=group-pc2
bucardo add sync sync-pc3-analysis relgroup=rel-analysis dbs=group-pc3
bucardo add sync sync-pc2-products relgroup=rel-products-config dbs=group-pc2
bucardo add sync sync-pc3-products relgroup=rel-products-config dbs=group-pc3

# Activate and start
# bucardo start
# echo "Activate bucardo syncs"

