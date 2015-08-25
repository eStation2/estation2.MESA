#!/bin/bash
#
#	Script to configure bucardo and create syncs
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

echo "$(date +'%Y-%m-%d %H:%M:%S') Configuration of bucardo"

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
bucardo start
echo "Activate bucardo syncs"

