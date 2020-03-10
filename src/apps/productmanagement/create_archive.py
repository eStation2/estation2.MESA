# -*- coding: utf-8 -*-
#
# purpose: Create 'archives' of eStation2 products to be disseminated through eumetcast
# date:  27.07.2015

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
import shutil
import os
from lib.python import es_logging as log
from lib.python import functions
from database import querydb
from config import es_constants
from apps.productmanagement.datasets import Dataset

logger = log.my_logger(__name__)

def create_archive_eumetcast(product, version, subproducts, mapset, start_date=None, end_date=None, target_dir=None, overwrite=False, tgz=False):

    # Rename and copy to target dir (/data/archives by default) the eStation2 files

    # Check target_dir
    if target_dir is None:
        target_dir = es_constants.es2globals['archive_dir']

    # Loop over subproducts
    if not isinstance(subproducts,list):
        subproducts_list=[]
        subproducts_list.append(subproducts)
    else:
        subproducts_list=subproducts

    for subproduct in subproducts_list:

        # Identify all existing files
        # Check if dates have to be disregarded (i.e. get all files)
        if start_date==-1 or end_date==-1:
            my_dataset=Dataset(product, subproduct, mapset, version=version)
            filenames = my_dataset.get_filenames()
        else:
            my_dataset=Dataset(product, subproduct, mapset, version=version, from_date=start_date, to_date=end_date)
            filenames = my_dataset.get_filenames_range()
        filenames.sort()
        for filename in filenames:
            # Derive MESA_JRC_ filename
            archive_name=functions.convert_name_to_eumetcast(filename, tgz=tgz)
            # Check if the target_file already exist
            if not os.path.isfile(target_dir+os.path.sep+archive_name) or overwrite:

                target_file=target_dir+os.path.sep+archive_name
                if not tgz:
                    # Copy only to target_dir
                    status=shutil.copyfile(filename,target_file)
                else:
                    command='tar -cvzf '+target_file+' -C '+os.path.dirname(filename)+' '+os.path.basename(filename)
                    status=os.system(command)

        logger.info("Files copied for product [%s]/version [%s]/subproducts [%s]/mapset [%s]" %(product, version, subproduct, mapset))
