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
ip_pc2=mesa-pc2
ip_pc3=mesa-pc3

echo "$(date +'%Y-%m-%d %H:%M:%S') Configuration of bucardo"

echo "$(date +'%Y-%m-%d %H:%M:%S') Create bucardo objects"

# Create 'dbs'-> mesa_pc2 and mesa_pc3	
bucardo add db mesa_pc2 dbname=estationdb host=${ip_pc2} port=5432 user=bucardo
bucardo add db mesa_pc3 dbname=estationdb host=${ip_pc3} port=5432 user=bucardo

# Create 'dbgroups'-> group_pc2 (pc2 source) 
# 		   -> group_pc3 (pc3 source) 
bucardo add dbgroup group_pc2 mesa_pc2:source mesa_pc3:target
#bucardo add dbgroup group_pc3 mesa_pc3:source mesa_pc2:target

# Create 'relgroups' -> rel_analysis: all tables of 'analysis' schema
#	 		rel_products_config: products tables for configuration by User (no static defs)

bucardo add relgroup rel_analysis analysis.i18n
bucardo add relgroup rel_analysis analysis.languages
bucardo add relgroup rel_analysis analysis.layers
bucardo add relgroup rel_analysis analysis.legend
bucardo add relgroup rel_analysis analysis.legend_step
bucardo add relgroup rel_analysis analysis.product_legend
bucardo add relgroup rel_analysis analysis.timeseries_drawproperties

bucardo add relgroup rel_products products.datasource_description
bucardo add relgroup rel_products products.eumetcast_source
bucardo add relgroup rel_products products.ingestion
bucardo add relgroup rel_products products.internet_source
bucardo add relgroup rel_products products.process_product
bucardo add relgroup rel_products products.processing
bucardo add relgroup rel_products products.product
bucardo add relgroup rel_products products.product_acquisition_data_source
bucardo add relgroup rel_products products.product_category
bucardo add relgroup rel_products products.sub_datasource_description
bucardo add relgroup rel_products products.thema_product

bucardo add relgroup rel_products products.data_type
bucardo add relgroup rel_products products.date_format
bucardo add relgroup rel_products products.frequency
bucardo add relgroup rel_products products.mapset
bucardo add relgroup rel_products products.thema




# Create 'delta' syncs

bucardo add sync sync_pc2_analysis relgroup=rel_analysis dbs=group_pc2
#bucardo add sync sync_pc3_analysis relgroup=rel_analysis dbs=group_pc3
bucardo add sync sync_pc2_products relgroup=rel_products_config dbs=group_pc2
#bucardo add sync sync_pc3_products relgroup=rel_products_config dbs=group_pc3

# Create 'fullcopy' syncs

bucardo add sync sync_pc2_analysis_full relgroup=rel_analysis dbs=group_pc2 onetimecopy=1
#bucardo add sync sync_pc3_analysis_full relgroup=rel_analysis dbs=group_pc3 onetimecopy=1
######bucardo add sync sync_pc2_products_full relgroup=rel_products_config dbs=group_pc2 onetimecopy=1
#bucardo add sync sync_pc3_products_full relgroup=rel_products_config dbs=group_pc3 onetimecopy=1

# Activate and start
bucardo start
echo "Activate bucardo syncs"

