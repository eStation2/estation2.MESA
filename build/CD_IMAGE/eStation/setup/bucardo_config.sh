#!/bin/bash
#
#	Script to configure bucardo and create syncs
#	This configuration is identical on pc2 and pc3 and creates 4 'syncs'	
#	
#		sync_pc2_analisys	-> to be run on pc2
#		sync_pc2_products
#
#		sync_pc3_analisys	-> to be run on pc3
#		sync_pc3_products
#

echo "NOTE: the following definitions have to be changed for MESA Installation"
echo "NOTE: they now refer to a TEST machine"
echo "NOTE: consider using network hostname rather then IP addresses"
ip_pc2=10.191.231.89
ip_pc3=10.191.231.90

echo "$(date +'%Y-%m-%d %H:%M:%S') Configuration of bucardo"

echo "$(date +'%Y-%m-%d %H:%M:%S') Create bucardo objects"

# Create 'dbs'-> mesa_pc2 and mesa_pc3	
bucardo add db mesa_pc2 dbname=estationdb host=${ip_pc2} port=5432 user=bucardo
bucardo add db mesa_pc3 dbname=estationdb host=${ip_pc3} port=5432 user=bucardo

# Create 'dbgroups'-> group_pc2 (pc2 source) 
# 		   -> group_pc3 (pc3 source) 
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
bucardo add relgroup rel_products_config products.thema_product

# Create 'syncs' -> see header

bucardo add sync sync_pc2_analysis relgroup=rel_analysis dbs=group_pc2
bucardo add sync sync_pc3_analysis relgroup=rel_analysis dbs=group_pc3
bucardo add sync sync_pc2_products relgroup=rel_products_config dbs=group_pc2
bucardo add sync sync_pc3_products relgroup=rel_products_config dbs=group_pc3

# Activate and start
bucardo start
echo "Activate bucardo syncs"

