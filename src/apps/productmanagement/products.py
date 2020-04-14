# -*- coding: utf-8 -*-
#
# purpose: Product functions
# author:  Marco Beri marcoberi@gmail.com
# date:  27.10.2014

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import object
import os
import glob
import tarfile
import shutil
import tempfile
import re
from osgeo import gdal, osr

from config import es_constants
from lib.python import es_logging as log
from lib.python import functions
from lib.python import metadata
from database import querydb
from lib.python.mapset import MapSet

from .exceptions import (NoProductFound, MissingMapset)
from .datasets import Dataset
from .mapsets import Mapset
from .helpers import *
# from .helpers import str_to_date

logger = log.my_logger(__name__)

#
#   Class to define all datasets belonging to the same product/version, i.e., possible more sub-product and mapsets
#   It includes:    type ('every' or 'per')
#                   unit (minute, hour, day, ...)
#                   value (integer)
#                   and dateformat (date/datetime)
#


class Product(object):
    def __init__(self, product_code, version=None):
        self.product_code = product_code
        kwargs = {'productcode': self.product_code}
        self.version = version
        if self.version:
            kwargs['version'] = version
        self._db_product = querydb.get_product_native(**kwargs)
        if self._db_product is None:
            raise NoProductFound(kwargs)
        if isinstance(self._db_product,list):
            if len(self._db_product) == 0:
                raise NoProductFound(kwargs)
        self._fullpath = os.path.join(es_constants.es2globals['processing_dir'], product_code)
        if version:
            self._fullpath = os.path.join(self._fullpath, version)

    @property
    def mapsets(self):
        _mapsets = getattr(self, "_mapsets", None)
        if _mapsets is None:
            _mapsets = []
            for mapset in self._get_full_mapsets():
                if os.path.basename(mapset) != 'archive':
                    _mapsets.append(os.path.basename(mapset))
            setattr(self, "_mapsets", _mapsets)
        return _mapsets

    def _get_full_mapsets(self):
        return glob.glob(os.path.join(self._fullpath, "*"))

    @property
    def subproducts(self):
        _subproducts = getattr(self, "_subproducts", None)
        if _subproducts is None:
            _subproducts = [subproduct for subproduct in
                    set(os.path.basename(subproduct) for subproduct in self._get_full_subproducts())]
        return _subproducts

    def _get_full_subproducts(self, mapset="*"):
        return tuple(subproduct for subproduct_type in list(functions.dict_subprod_type_2_dir.values())
                                for subproduct in glob.glob(os.path.join(self._fullpath, mapset, subproduct_type, "*")))

    def get_dataset(self, mapset, sub_product_code, from_date=None, to_date=None):
        return Dataset(self.product_code, sub_product_code=sub_product_code, mapset=mapset, version=self.version, from_date=from_date, to_date=to_date)

    def get_subproducts(self, mapset):
        return [subproduct for subproduct in
                    set(os.path.basename(subproduct) for subproduct in self._get_full_subproducts(mapset=mapset))]

    # Return the missing info for a single dataset (i.e. product-version-mapset-subproduct)
    def get_missing_dataset_subproduct(self, mapset, sub_product_code, from_date=None, to_date=None):
        mapset_obj = Mapset(mapset_code=mapset)
        missing = {
                'product': self.product_code,
                'version': self.version,
                'mapset': mapset,
                'mapset_data': mapset_obj.to_dict(),
                'subproduct': sub_product_code,
                'from_start': from_date is None,
                'to_end': to_date is None,
                }
        dataset = Dataset(self.product_code, sub_product_code=sub_product_code,
                          mapset=mapset, version=self.version, from_date=from_date, to_date=to_date)
        missing['info'] = dataset.get_dataset_normalized_info(from_date, to_date)
        return missing

    # Return the list of datasets (i.e. mapset*subproducts) associated to prod-version
    def get_missing_datasets(self, mapset=None, sub_product_code=None, from_date=None, to_date=None):
        missings = []
        if sub_product_code:
            if not mapset:
                raise MissingMapset(sub_product_code)
            missings.append(self.get_missing_dataset_subproduct(mapset, sub_product_code, from_date, to_date))
        else:
            for mapset in [mapset] if mapset else self.mapsets:
                for sub_product_code in self.get_subproducts(mapset):
                    missings.append(self.get_missing_dataset_subproduct(mapset, sub_product_code, from_date, to_date))
        return missings

    def get_missing_filenames(self, missing, existing_only=True, for_request_creation=False):

        # NOTES:    by default, it returns the existing filenames ONLY
        #           In case the requested mapset does not exist, but a larger one is available, returns the latter
        #           -> the calling routine should perform the re-projection

        # product = Product(missing['product'], version=missing['version'])
        version = missing['version']
        mapset = missing['mapset']
        subproduct = missing['subproduct']
        dataset = self.get_dataset(mapset=mapset, sub_product_code=missing['subproduct'])

        missing_filenames = []

        # Manage the mapset: if the required one does not exist, use a 'larger' one (if exists)
        existing_files = dataset.get_filenames()
        # Usage 1: creating archive from request - old style - look at larger mapset
        if len(existing_files) == 0 and not for_request_creation:

            logger.warning("No any file found for original mapset: %s. Return" % mapset)
            my_mapset = MapSet()
            my_mapset.assigndb(mapset)
            larger_mapset = my_mapset.get_larger_mapset()
            # See ES2-64: 07.11.17 -> check a larger mapset exist (or return empty)
            if not larger_mapset:
                logger.warning("No larger mapset found for original mapset: %s. Return" % mapset)
                return missing_filenames
            new_dataset = self.get_dataset(mapset=larger_mapset, sub_product_code=missing['subproduct'])
            new_existing_files = new_dataset.get_filenames()

            if len(new_existing_files) > 0:
                use_mapset = larger_mapset
                dataset = new_dataset
            else:
                logger.warning('No any file found for larger mapset: %s. Return' % larger_mapset)
                return missing_filenames
        else:
                use_mapset = mapset

        # Manage the specific case of 'singlefile', e.g. absol-min-linearx2
        if dataset._db_product.frequency_id == 'singlefile':
            # Check if the 'single' file was missing
            info = missing['info']
            if info['missingfiles']:
                missing_filenames = dataset.get_filenames()
        else:
            dates = dataset.get_dates()
            missing_dates = []
            first_date = None
            last_date = None
            info = missing['info']
            for interval in info['intervals']:
                # if for_request_creation and len(info['intervals']) == 1 and interval['fromdate'] == interval['todate'] and interval['missing']:
                #     first_date = add_years(str_to_date(interval['fromdate']), -1)
                #     last_date = str_to_date(interval['todate'])
                #     missing_dates.extend(dataset.get_interval_dates(first_date, last_date))
                # else:
                if first_date is None:
                    first_date = str_to_date(interval['fromdate'])
                last_date = str_to_date(interval['todate'])
                if interval['missing']:
                    missing_dates.extend(dataset.get_interval_dates(
                        str_to_date(interval['fromdate']), str_to_date(interval['todate'])))

            if len(info['intervals']) == 0:
                missing_dates = dates[:]
            else:
                # NOTE: never consider 'from-start': on Server timeseries are longer then the ones delivered to Users.
                # This is a quick fix for release 2.0.3
                # if missing['from_start']:
                if False:
                    if first_date > dataset.get_first_date():
                        missing_dates.extend(dataset.get_interval_dates(dataset.get_first_date(),
                                                                        first_date, last_included=False))
                if missing['to_end']:
                    if isinstance(last_date, datetime.datetime):
                        if last_date.date() < dataset.get_last_date():
                            missing_dates.extend(dataset.get_interval_dates(last_date,
                                dataset.get_last_date(), first_included=False))
                    else:
                        if last_date < dataset.get_last_date():
                            missing_dates.extend(dataset.get_interval_dates(last_date,
                                dataset.get_last_date(), first_included=False))

            # print (missing_dates)
            if existing_only:
                dates_to_add = sorted(set(dates).intersection(set(missing_dates)))
            else:
                dates_to_add = sorted(set(missing_dates))

            for date in dates_to_add:
                date_str = dataset._frequency.format_date(date)
                filename = dataset.fullpath+functions.set_path_filename(date_str, missing['product'],
                                                                        subproduct, use_mapset, version,'.tif')
                missing_filenames.append(filename)

        return missing_filenames

    def get_missing_filenames_all(self, missing, existing_only=True):

        # NOTES:    by default, it returns the existing filenames ONLY
        #           w.r.t. get_missing_filenames(), does not consider time period

        product = Product(missing['product'], version=missing['version'])
        version = missing['version']
        mapset = missing['mapset']
        subproduct = missing['subproduct']
        dataset = product.get_dataset(mapset=mapset, sub_product_code=missing['subproduct'])

        missing_filenames=[]

        # Manage the mapset: if the required one does not exist, use a 'larger' one (if exists)
        existing_files = dataset.get_filenames()
        if len(existing_files) == 0:

            logger.warning("No any file found for original mapset: %s. Return" % mapset)
            my_mapset = MapSet()
            my_mapset.assigndb(mapset)
            larger_mapset = my_mapset.get_larger_mapset()
            new_dataset = product.get_dataset(mapset=larger_mapset, sub_product_code=missing['subproduct'])
            new_existing_files = new_dataset.get_filenames()

            if len(new_existing_files) > 0:
                use_mapset = larger_mapset
                dataset = new_dataset
            else:
                logger.warning('No any file found for larger mapset: %s. Return' % larger_mapset)
                return
        else:
                use_mapset = mapset

        missing_filenames = dataset.get_filenames()

        return missing_filenames

    @staticmethod
    def create_tar(missing_info, filetar=None, tgz=True):

    # Given a 'missing_info' object, creates a tar-file containing all required (i.e. missing) files

        result = {'status':0,            # 0 -> ok, all files copied, 1-> at least 1 file missing
                  'n_file_copied':0,
                  'n_file_missing':0,
                  }

        tmp_dir = None
        final_filenames = []

        # Check that the target filename for TAR is passed (OR define a temp one)
        if filetar is None:
            file_temp = tempfile.NamedTemporaryFile()
            filetar = file_temp.name
            file_temp.close()

        filenames = []
        # Loop over missing objects
        for missing in missing_info:
            try:
                product = Product(missing['product'], version=missing['version'],)
                # Change existing_only to True 21.3.18
                filenames.extend(product.get_missing_filenames(missing,existing_only=True))
            except NoProductFound:
                pass
            orig_mapset = missing['mapset']

            # The get_missing_filenames can return a 'larger' mapset (if the orig is missing):
            #   manage here the re-projection and append in final_filenames the ones for the 'orig' mapset

            for filename in filenames:
                [product_code, sub_product_code, version, str_date, my_mapset] = functions.get_all_from_path_full(filename)

                if my_mapset == orig_mapset:
                    if os.path.isfile(filename):
                        final_filenames.append(filename)
                else:
                    if tmp_dir is None:
                        tmp_dir = tempfile.mkdtemp(prefix=__name__, suffix='',dir=es_constants.base_tmp_dir)

                    # Do reprojection to a /tmp dir (if the file exists)
                    if os.path.isfile(filename):
                        new_filename = reproject_output(filename, my_mapset, orig_mapset, output_dir=tmp_dir+os.path.sep,
                                                        version=missing['version'])
                        if os.path.isfile(new_filename):
                            final_filenames.append(new_filename)

        # Create .tar
        if len(final_filenames) > 0:
            tar = tarfile.open(filetar, "w|gz" if tgz else "w|",dereference=True)
            for filename in final_filenames:
                name = os.path.basename(filename)
                subdir = functions.get_subdir_from_path_full(filename)
                if os.path.isfile(filename):
                    tar.add(filename, arcname=subdir+name)
                    logger.info('Added file: %s', filename)
                    result['n_file_copied']+=1
                else:
                    result['n_file_missing']+=1
                    result['status']=1
            tar.close()

        # Remove tmp_dir
        if tmp_dir is not None:
            shutil.rmtree(tmp_dir)

        return [filetar, result]

    def create_tar_vars(self, productcode, version, subproductcode, mapsetcode, from_date=None, to_date=None, filetar=None, tgz=True):

    # Given a list o variables, creates a tar-file containing all required files

        result = {'status':0,            # 0 -> ok, all files copied, 1-> at least 1 file missing
                  'n_file_copied':0,
                  'n_file_missing':0,
                  }

        tmp_dir = None
        final_filenames = []

        # Create missing structure
        interval = {'fromdate':from_date,
                    'todate':to_date,
                    'missing': True}

        info ={'intervals': [interval]}
        missing = {'product': productcode,
                   'version': version,
                   'mapset':mapsetcode,
                   'subproduct': subproductcode,
                   'info': info,
                   'to_end': False}


        # Check the target file name is passed (or define a temp one)
        if filetar is None:
            file_temp = tempfile.NamedTemporaryFile()
            filetar = file_temp.name
            file_temp.close()

        filenames = []
        # Loop over missing objects
        try:
            product = Product(productcode, version)
            if from_date is None or to_date is None:
                filenames.extend(product.get_missing_filenames_all(missing,existing_only=False))
            else:
                filenames.extend(product.get_missing_filenames(missing,existing_only=False))

            # dataset = product.get_dataset(mapset=mapsetcode, sub_product_code=subproductcode, from_date=from_date, to_date=to_date)
            # filenames.extend(dataset.get_filenames_range())
            filenames.sort()
        except NoProductFound:
            pass

        orig_mapset = mapsetcode

        # The get_missing_filenames can return a 'larger' mapset.
        # Manage here the re-projection
        for filename in filenames:
            [product_code, sub_product_code, version, str_date, my_mapset] = functions.get_all_from_path_full(filename)

            if my_mapset == orig_mapset:
                final_filenames.append(filename)
            else:
                if tmp_dir is None:
                    tmp_dir = tempfile.mkdtemp(prefix=__name__, suffix='',dir=es_constants.base_tmp_dir)
                # Do reprojection to a /tmp dir (if the file exists)
                if os.path.isfile(filename):
                    new_filename = reproject_output(filename, my_mapset, orig_mapset, output_dir=tmp_dir+os.path.sep,
                                                    version=version)
                    if os.path.isfile(new_filename):
                        final_filenames.append(new_filename)

        # Create .tar
        tar = tarfile.open(filetar, "w|gz" if tgz else "w|",dereference=True)
        for filename in final_filenames:
            name = os.path.basename(filename)
            subdir = functions.get_subdir_from_path_full(filename)
            if os.path.isfile(filename):
                tar.add(filename, arcname=subdir+name)
                logger.debug('Added file: %s', filename)
                result['n_file_copied']+=1
            else:
                result['n_file_missing']+=1
                result['status']=1
        tar.close()

        # Remove tmp_dir
        if tmp_dir is not None:
            shutil.rmtree(tmp_dir)

        return [filetar, result]

    @staticmethod
    def import_tar(filetar, tgz=False):

        result = {'status':0,            # 0 -> ok, 1-> no tmpdir created
                  'n_file_copied':0,
                  'n_file_error':0,
                  }
        # Create tmp dir
        try:
            tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(filetar),
                                  dir=es_constants.base_tmp_dir)
        except IOError:
            logger.error('Cannot create temporary dir ' + es_constants.base_tmp_dir + '. Exit')
            result['status']=1

        # Extract from tar
        if os.path.isfile(filetar):
            # Untar the file to a temp dir
            tar = tarfile.open(filetar, "r|gz" if tgz else "r|")
            names=tar.getnames()
            # Extract with subdirs
            tar.extractall(path=tmpdir)
            # Move files to basedir
            for name in names:
                os.rename(tmpdir+name,tmpdir+os.path.basename(name))
        else:
            result['status']=1

        # Copy from tmpdir to target directory
        meta = metadata.SdsMetadata()
        # Get list of files in tmp dir
        extracted_files = glob.glob(tmpdir+'*.tif')

        for my_file in extracted_files:
            fullpath_dest=meta.get_target_filepath(my_file)
            try:
                shutil.copyfile(my_file, fullpath_dest)
            except:
                logger.error('Error in copying file %s' % fullpath_dest)

        # Clean and exit
        shutil.rmtree(tmpdir)

        return result

    def list_all_ingested_and_derived_subproducts_mapsets(self):

        # Initialize list of prod/version/subprods/mapset to be returned
        list_ingested_and_derived_subproducts = []

        # Get all active product ingestion records with a subproduct count.
        active_product_ingestions = querydb.get_ingestion_product(productcode=self.product_code, version=self.version)
        # Convert tuple to list (if 1 tuple is returned)
        if isinstance(active_product_ingestions,tuple):
            my_list= []
            my_list.append(active_product_ingestions)
            active_product_ingestions=my_list

        for active_product_ingest in active_product_ingestions:

            # For the current active product ingestion: get all
            product = {"productcode": self.product_code,
                       "version": self.version}

            # Get the list of acquisition sources that are defined for this ingestion 'trigger'
            # (i.e. prod/version)
            # NOTE: the following implies there is 1 and only 1 '_native' subproduct associated to a 'subproduct';
            native_product = {"productcode":  self.product_code,
                              "subproductcode":  self.product_code + "_native",
                              "version": self.version}
            sources_list = querydb.get_product_sources(**native_product)
            logger.debug("For product [%s] N. %s  source is/are found" % (self.product_code,len(sources_list)))

            ingestions = querydb.get_ingestion_subproduct(allrecs=False, **product)
            for ingest in ingestions:
                my_tuple = {"productcode":  self.product_code,
                            "subproductcode":  ingest.subproductcode,
                            "version": self.version,
                            "mapset": ingest.mapsetcode}
                logger.debug("Looking for product [%s]/version [%s]/subproducts [%s]/mapset [%s]" % (self.product_code, self.version,ingest.subproductcode,ingest.mapsetcode))
                list_ingested_and_derived_subproducts.append(my_tuple)

        # Get all active processing chains [product/version/algo/mapset].
        active_processing_chains = querydb.get_active_processing_chains()
        for chain in active_processing_chains:
            a = chain.process_id
            logger.debug("Processing Chain N.:%s" % str(chain.process_id))
            processed_products = querydb.get_processing_chain_products(chain.process_id, type='output')
            for processed_product in processed_products:
                if processed_product.productcode==self.product_code and processed_product.version==self.version:
                    my_tuple = {"productcode":  self.product_code,
                                "subproductcode":  processed_product.subproductcode,
                                "version": self.version,
                                "mapset": processed_product.mapsetcode}

                    logger.debug("Looking for product [%s]/version [%s]/subproducts [%s]/mapset [%s]" % (self.product_code, self.version,processed_product.subproductcode,processed_product.mapsetcode))
                    list_ingested_and_derived_subproducts.append(my_tuple)

        return list_ingested_and_derived_subproducts


######################################################################################
#
#   Purpose: reproject a file to a different mapset
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2015/05/15
#   Inputs: input_file (an eStation 2.0 GTIFF file)
#           target_mapset: the target mapset of reprojection
#   Output: output_file
#
def reproject_output(input_file, native_mapset_id, target_mapset_id, output_dir=None, version=None, logger=None):

    # Check logger
    if logger is None:
        logger = log.my_logger(__name__)

    # Check output dir
    if output_dir is None:
        output_dir = es_constants.es2globals['processing_dir']

    # Get the existing dates for the dataset
    logger.debug("Entering routine %s for file %s" % ('reproject_output', input_file))
    ext=es_constants.ES2_OUTFILE_EXTENSION

    # Test the file/files exists
    if not os.path.isfile(input_file):
        logger.error('Input file: %s does not exist' % input_file)
        return 1

    # Instance metadata object (for output_file)
    sds_meta_out = metadata.SdsMetadata()

    # Read metadata from input_file
    sds_meta_in = metadata.SdsMetadata()
    sds_meta_in.read_from_file(input_file)

    # Extract info from input file
    str_date = sds_meta_in.get_item('eStation2_date')
    product_code = sds_meta_in.get_item('eStation2_product')
    sub_product_code = sds_meta_in.get_item('eStation2_subProduct')
    # 22.06.2017 Add the option to force the version
    if version is None:
        version = sds_meta_in.get_item('eStation2_product_version')

    # Define output filename
    sub_dir = sds_meta_in.get_item('eStation2_subdir')
    # Fix a bug for 10davg-linearx2 metadata - and make method more robust
    if re.search('.*derived.*',sub_dir):
        product_type = 'Derived'
    elif re.search('.*tif.*',sub_dir):
        product_type = 'Ingest'
    # product_type = functions.get_product_type_from_subdir(sub_dir)

    out_prod_ident = functions.set_path_filename_no_date(product_code, sub_product_code, target_mapset_id, version, ext)
    output_subdir = functions.set_path_sub_directory(product_code, sub_product_code, product_type, version, target_mapset_id)

    output_file = output_dir+\
                  output_subdir +\
                  str_date +\
                  out_prod_ident

    # make sure output dir exists
    output_dir = os.path.split(output_file)[0]
    functions.check_output_dir(output_dir)

    # -------------------------------------------------------------------------
    # Manage the geo-referencing associated to input file
    # -------------------------------------------------------------------------
    orig_ds = gdal.Open(input_file, gdal.GA_Update)

    # Read the data type
    band = orig_ds.GetRasterBand(1)
    out_data_type_gdal = band.DataType

    if native_mapset_id != 'default':
        native_mapset = MapSet()
        native_mapset.assigndb(native_mapset_id)
        orig_cs = osr.SpatialReference(wkt=native_mapset.spatial_ref.ExportToWkt())

        # Complement orig_ds info (necessary to Re-project)
        try:
            #orig_ds.SetGeoTransform(native_mapset.geo_transform)
            orig_ds.SetProjection(orig_cs.ExportToWkt())
        except:
            logger.debug('Cannot set the geo-projection .. Continue')
    else:
        try:
            # Read geo-reference from input file
            orig_cs = osr.SpatialReference()
            orig_cs.ImportFromWkt(orig_ds.GetProjectionRef())
        except:
            logger.debug('Cannot read geo-reference from file .. Continue')

    # TODO-M.C.: add a test on the mapset-id in DB table !
    trg_mapset = MapSet()
    trg_mapset.assigndb(target_mapset_id)
    logger.debug('Target Mapset is: %s' % target_mapset_id)

    # -------------------------------------------------------------------------
    # Generate the output file
    # -------------------------------------------------------------------------
    # Prepare output driver
    out_driver = gdal.GetDriverByName(es_constants.ES2_OUTFILE_FORMAT)

    logger.debug('Doing re-projection to target mapset: %s' % trg_mapset.short_name)
    # Get target SRS from mapset
    out_cs = trg_mapset.spatial_ref
    out_size_x = trg_mapset.size_x
    out_size_y = trg_mapset.size_y

    # Create target in memory
    mem_driver = gdal.GetDriverByName('MEM')

    # Assign mapset to dataset in memory
    mem_ds = mem_driver.Create('', out_size_x, out_size_y, 1, out_data_type_gdal)

    mem_ds.SetGeoTransform(trg_mapset.geo_transform)
    mem_ds.SetProjection(out_cs.ExportToWkt())

    # Apply Reproject-Image to the memory-driver
    orig_wkt = orig_cs.ExportToWkt()
    res = gdal.ReprojectImage(orig_ds, mem_ds, orig_wkt, out_cs.ExportToWkt(),
                                  es_constants.ES2_OUTFILE_INTERP_METHOD)

    logger.debug('Re-projection to target done.')

    # Read from the dataset in memory
    out_data = mem_ds.ReadAsArray()

    # Write to output_file
    trg_ds = out_driver.CreateCopy(output_file, mem_ds, 0, [es_constants.ES2_OUTFILE_OPTIONS])
    trg_ds.GetRasterBand(1).WriteArray(out_data)

    # -------------------------------------------------------------------------
    # Assign Metadata to the ingested file
    # -------------------------------------------------------------------------
    # Close dataset
    trg_ds = None

    sds_meta_out.assign_es2_version()
    sds_meta_out.assign_mapset(target_mapset_id)
    sds_meta_out.assign_from_product(product_code, sub_product_code, version)
    sds_meta_out.assign_date(str_date)
    sds_meta_out.assign_subdir_from_fullpath(output_dir)
    sds_meta_out.assign_compute_time_now()
    # Copy the same input files as in the non-reprojected input
    file_list = sds_meta_in.get_item('eStation2_input_files')
    sds_meta_out.assign_input_files(file_list)

    # Write metadata to file
    sds_meta_out.write_to_file(output_file)

    # Return the filename
    return output_file