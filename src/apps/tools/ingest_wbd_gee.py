from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from future import standard_library
standard_library.install_aliases()
_author__ = "Marco Clerici"


from config import es_constants
from apps.acquisition import ingestion
from lib.python import metadata
from lib.python import functions
from database import querydb
import unittest
import os
import glob

# Overwrite Dirs
from lib.python import es_logging as log
logger = log.my_logger(__name__)

def ingest_jrc_wbd(input_dir, in_date=None, avg=None):

    if avg:
        date_fileslist = glob.glob(input_dir+'/JRC-WBD_AVG2000-'+in_date+'*')
        subproductcode = 'avg'
        mapsetcode = 'WD-GEE-ECOWAS-AVG'
        datasource_descrID='JRC:WBD:GEE:AVG'
    else:
        date_fileslist = glob.glob(input_dir+'/JRC-WBD_'+in_date+'*')
        subproductcode = 'occurr'
        mapsetcode = 'WD-GEE-ECOWAS-1'
        datasource_descrID='JRC:WBD:GEE'

    productcode = 'wd-gee'
    productversion = '1.0'

    product = {"productcode": productcode,
               "version": productversion}
    args = {"productcode": productcode,
            "subproductcode": subproductcode,
            "datasource_descr_id": datasource_descrID,
            "version": productversion}

    product_in_info = querydb.get_product_in_info(**args)

    re_process = product_in_info.re_process
    re_extract = product_in_info.re_extract

    sprod = {'subproduct': subproductcode,
                         'mapsetcode': mapsetcode,
                         're_extract': re_extract,
                         're_process': re_process}

    subproducts=[]
    subproducts.append(sprod)

    output_file = es_constants.es2globals['processing_dir']+\
                  functions.set_path_sub_directory(productcode, subproductcode, 'Ingest', productversion, mapsetcode) +\
                  functions.set_path_filename(in_date,productcode,subproductcode,mapsetcode,productversion,'.tif')

    for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='INTERNET',
                                                                          source_id=datasource_descrID):
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)


    return output_file

def reproject_jrc_wbd(input_file):

    new_mapset = 'WD-GEE-ECOWAS-AVG'
    out_filepath = input_file.replace('WD-GEE-ECOWAS-1','WD-GEE-ECOWAS-AVG')

    # Check the file is not yet there
    if not os.path.isfile(out_filepath):
        # Reproject
        command = 'gdal_translate -of GTIFF -co "compress=LZW" -projwin -17.5290058 27.3132762 24.0006488 4.2682552 ' + input_file +' '+out_filepath
        os.system(command)
        # Update metadata (mapset)
        sds_meta = metadata.SdsMetadata()

        # Check if the input file is single, or a list
        sds_meta.read_from_file(out_filepath)
        sds_meta.assign_mapset(new_mapset)
        sds_meta.write_to_file(out_filepath)

    else:
        print ('Output file already exists: %s' % os.path.basename(out_filepath))

if __name__=='__main__':

    in_date = '20160301'
    input_dir = es_constants.es2globals['ingest_dir']

    # 'occurr' product
    avg = False
    out_file = ingest_jrc_wbd(input_dir, in_date=in_date, avg=avg)

    # Perform re-projection to 'WD-GEE-ECOWAS-AVG' mapset
    reproject_jrc_wbd(out_file)

    # 'occurr' product
    # avg = True
    # result = ingest_jrc_wbd(input_dir, in_date=in_date, avg=avg)
