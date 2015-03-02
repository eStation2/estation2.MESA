from unittest import TestCase

__author__ = 'clerima'

import os
from lib.python.functions import *
sep=os.path.sep

class TestFunctionsPath(TestCase):

    # Common definitions
    str_date = '201401011200'
    str_version = 'my-version'
    str_prod = str('my-prod-code')
    str_sprod = str('my-subprod-code')
    str_mapset= 'my-mapset'
    str_extension = '.tif'
    product_type = 'Ingest'
    str_type_subdir = dict_subprod_type_2_dir[product_type]

    # Rule for sub_dir is: <prod_code>/<mapset>/<type>/<sprod_code>

    sub_dir   = str_prod+sep+\
                str_version+sep+\
                str_mapset+sep+\
                str_type_subdir+sep+\
                str_sprod+sep

    dir_name=sep+'base'+sep+'dir'+sep+'some'+sep+'where' + sep + sub_dir


    # Rule for filename is: <datetime>_<prod_code>_<sprod_code>_<mapset>.<ext>
    filename=str_date+'_'+str_prod+'_'+str_sprod+'_'+str_mapset+'_'+str_version+str_extension

    fullpath = dir_name+filename

    #   -----------------------------------------------------------------------------------
    #   Extract info from dir/filename/fullpath

    def test_get_from_path_dir(self):


        [my_product_code,my_sub_product_code, my_version, my_mapset] = get_from_path_dir(self.dir_name)

        self.assertEqual(my_product_code,self.str_prod)
        self.assertEqual(my_sub_product_code,self.str_sprod)
        self.assertEqual(my_mapset,self.str_mapset)
        self.assertEqual(my_version,self.str_version)


    def test_get_date_from_path_filename(self):


        my_date = get_date_from_path_filename(self.filename)

        self.assertEqual(my_date,self.str_date)
        #self.assertEqual(my_mapset,self.str_mapset)

    def test_get_date_from_path_full(self):


        my_date = get_date_from_path_full(self.fullpath)

        self.assertEqual(my_date,self.str_date)

    def test_get_all_from_path_full(self):

        full_path = self.dir_name+self.filename

        my_product_code, my_sub_product_code, my_version, my_date, my_mapset = get_all_from_path_full(full_path)

        self.assertEqual(my_product_code,self.str_prod)
        self.assertEqual(my_sub_product_code,self.str_sprod)
        self.assertEqual(my_date,self.str_date)
        self.assertEqual(my_mapset,self.str_mapset)
        self.assertEqual(my_version,self.str_version)

    def test_get_subdir_from_path_full(self):

        full_path = self.dir_name+self.filename

        my_subdir = get_subdir_from_path_full(full_path)

        self.assertEqual(my_subdir,self.sub_dir)



    #   -----------------------------------------------------------------------------------
    #   Compose dir/filename/fullpath from attributes

    def test_set_path_filename(self):

        my_filename = set_path_filename(self.str_date, self.str_prod, self.str_sprod,
                                        self.str_mapset, self.str_version, self.str_extension)

        logger.info('Filename is: %s' % my_filename)
        self.assertEqual(self.filename,my_filename)

    def test_set_path_sub_directory(self):

        my_sub_directory = set_path_sub_directory(self.str_prod, self.str_sprod, self.product_type,
                                        self.str_version, self.str_mapset)
        logger.info('Subdirectory is: %s' % my_sub_directory)

        self.assertEqual(self.sub_dir,my_sub_directory)

