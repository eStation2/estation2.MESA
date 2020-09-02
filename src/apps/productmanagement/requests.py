# -*- coding: utf-8 -*-
#
# purpose: handle request for completing datasets
# author:  MC, JvK
# date:  27.08.2015

# from config import es_constants
# from lib.python import metadata
# from .exceptions import (NoProductFound, MissingMapset)
# from .datasets import Dataset
# from .mapsets import Mapset


# import glob
# import tempfile
# import pprint

from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from builtins import open
from builtins import int
from future import standard_library

standard_library.install_aliases()
from builtins import str
from builtins import map
import os
import tarfile
import shutil
import json
import datetime
from dateutil.relativedelta import relativedelta

from apps.productmanagement.products import *
# from lib.python import functions
# from database import querydb
from config import es_constants
from .mapsets import Mapset

from lib.python import es_logging as log

logger = log.my_logger(__name__)


# New function to correct the mapset object returned by the mapset class (\apps\productmanagement\mapsets.py)
# which calls the query get_mapset that now returns the new mapset info but in a dict with all strings.
# The eStationSync.jar expects float or int values for certain mapset fields, which in this function are casted to
# the correct datatype.
def correctMapset(mapset_corrected):
    mapset_corrected['upper_left_long'] = float(mapset_corrected['upper_left_long'])
    mapset_corrected['upper_left_lat'] = float(mapset_corrected['upper_left_lat'])
    mapset_corrected['pixel_shift_long'] = float(mapset_corrected['pixel_shift_long'])
    mapset_corrected['pixel_shift_lat'] = float(mapset_corrected['pixel_shift_lat'])
    mapset_corrected['pixel_size_x'] = int(mapset_corrected['pixel_size_x'])
    mapset_corrected['pixel_size_y'] = int(mapset_corrected['pixel_size_y'])
    mapset_corrected['rotation_factor_long'] = float(mapset_corrected['rotation_factor_long'])
    mapset_corrected['rotation_factor_lat'] = float(mapset_corrected['rotation_factor_lat'])
    return mapset_corrected


def get_from_date(frequency_id, dateformat):
    if frequency_id in ['e15minute', 'e30minute']:
        today = datetime.date.today()
        from_date = today - relativedelta(months=3)

    elif frequency_id in ['e1day', '2pday']:
        today = datetime.date.today()
        from_date = today - relativedelta(years=1)

    elif frequency_id in ['e1dekad', 'e1modis16day', 'e1modis8day', 'e1modis8day']:
        if dateformat == 'MMDD':
            years_back = 1
        elif dateformat == 'YYYYMMDD':
            years_back = 5
        else:
            years_back = 1

        today = datetime.date.today()
        # for decad always start on the 1st of the month (here the 1st of january of the current year)
        first_day_of_year = str(today.year) + '-01-01'
        year, month, day = list(map(int, first_day_of_year.split("-")))
        first_day_of_year = datetime.date(year, month, day)
        from_date = first_day_of_year - relativedelta(years=years_back)

    elif frequency_id in ['e1month', 'e3month', 'e6month', 'e1year']:
        if dateformat in ['MMDD', 'YYYY']:
            years_back = 1
        elif dateformat == 'YYYYMMDD':
            years_back = 5
        else:
            years_back = 1

        today = datetime.date.today()
        # for decad always start on the 1st of the month (here the 1st of january of the current year)
        first_day_of_year = str(today.year) + '-01-01'
        year, month, day = list(map(int, first_day_of_year.split("-")))
        first_day_of_year = datetime.date(year, month, day)
        from_date = first_day_of_year - relativedelta(years=years_back)
    else:
        from_date = None

    return from_date


def create_request(productcode, version, mapsetcode=None, subproductcode=None, dekad_frequency=5, daily_frequency=1,
                   high_frequency=3):
    # Define the 'request' object
    request = {'product': productcode,
               'version': version}

    product = Product(product_code=productcode, version=version)

    # Check the level of the request
    if mapsetcode is None:
        if subproductcode is not None:
            logger.error('Create Request: If mapset is not defined, subproduct cannot be defined!')
            return request
        else:
            all_prod_mapsets = product.mapsets
            all_prod_subproducts = product.subproducts
            if all_prod_mapsets.__len__() > 0 and all_prod_subproducts.__len__() > 0:
                request['productmapsets'] = []
                for mapset in all_prod_mapsets:
                    mapset_obj = Mapset(mapset_code=mapset)
                    mapset_corrected = correctMapset(mapset_obj.to_dict())
                    mapset_dict = {'mapset': mapset_corrected, 'mapsetdatasets': []}
                    # mapset_dict = {'mapset': mapset_obj.to_dict(), 'mapsetdatasets': []}

                    all_mapset_datasets = product.get_subproducts(mapset=mapset)
                    for subproductcode in all_mapset_datasets:
                        from_date = None
                        to_date = None

                        dataset_dbinfo = querydb.get_subproduct(productcode=productcode,
                                                                version=version,
                                                                subproductcode=subproductcode)
                        kwargs = {'mapset': mapset,
                                  'sub_product_code': subproductcode}
                        if dataset_dbinfo is not None:
                            if hasattr(dataset_dbinfo, 'frequency_id'):
                                if dataset_dbinfo.frequency_id == 'e15minute':
                                    today = datetime.date.today()
                                    from_date = today - datetime.timedelta(days=int(high_frequency))
                                    to_date = today + datetime.timedelta(days=1)
                                    kwargs = {'mapset': mapset,
                                              'sub_product_code': subproductcode,
                                              'from_date': from_date,
                                              'to_date': to_date}
                                elif dataset_dbinfo.frequency_id == 'e30minute':
                                    today = datetime.date.today()
                                    from_date = today - datetime.timedelta(days=int(high_frequency))
                                    to_date = today + datetime.timedelta(days=1)
                                    kwargs = {'mapset': mapset,
                                              'sub_product_code': subproductcode,
                                              'from_date': from_date,
                                              'to_date': to_date}
                                elif dataset_dbinfo.frequency_id == 'e1day':
                                    today = datetime.date.today()
                                    from_date = today - relativedelta(years=int(daily_frequency))
                                    # if sys.platform != 'win32':
                                    #     from_date = today - relativedelta(years=1)
                                    # else:
                                    #     from_date = today - datetime.timedelta(days=365)
                                    kwargs = {'mapset': mapset,
                                              'sub_product_code': subproductcode,
                                              'from_date': from_date}
                                elif dataset_dbinfo.date_format == 'YYYYMMDD':  # dataset_dbinfo.frequency_id == 'e1dekad' and
                                    today = datetime.date.today()
                                    from_date = today - relativedelta(years=int(dekad_frequency))
                                    from_date = from_date.replace(day=1)  # always start at the first of the month!

                                    kwargs = {'mapset': mapset,
                                              'sub_product_code': subproductcode,
                                              'from_date': from_date}
                                else:
                                    kwargs = {'mapset': mapset,
                                              'sub_product_code': subproductcode}

                            dataset = product.get_dataset(**kwargs)
                            # dataset = product.get_dataset(mapset=mapset, sub_product_code=subproductcode,
                            #                               from_date=None, to_date=None)

                            dataset_info = dataset.get_dataset_normalized_info()
                            tot_files = dataset_info['totfiles']
                            if tot_files == 0:
                                from_date = get_from_date(dataset.frequency_id, dataset.date_format)
                                to_date = datetime.date.today()

                            missing_info = product.get_missing_datasets(mapset=mapset, sub_product_code=subproductcode,
                                                                        from_date=from_date, to_date=to_date)
                            filenames = []
                            # Loop over missing objects
                            for missing in missing_info:
                                try:
                                    filenames.extend(product.get_missing_filenames(missing, existing_only=False,
                                                                                   for_request_creation=True))
                                except NoProductFound:
                                    pass

                            # Remove the processing dir from file path because this can be different for each
                            # installation (especially the windows version) than on the cloud service processing dir
                            filenames[:] = [os.path.join(os.path.sep, os.path.relpath(filename, es_constants.es2globals[
                                'processing_dir'])) for
                                            filename in filenames]
                            # for filename in filenames:
                            #     print filename

                            dataset_dict = {'subproductcode': subproductcode,
                                            "allfiles": False,
                                            'missingfiles': filenames}
                            mapset_dict['mapsetdatasets'].append(dataset_dict)

                    request['productmapsets'].append(mapset_dict)
    # Mapset is defined
    else:
        if subproductcode is None:
            # Get full list of subproducts (ingest/derived) for the given mapset
            request['productmapsets'] = []
            mapset_obj = Mapset(mapset_code=mapsetcode)
            mapset_corrected = correctMapset(mapset_obj.to_dict())
            mapset_dict = {'mapset': mapset_corrected, 'mapsetdatasets': []}
            # mapset_dict = {'mapset': mapset_obj.to_dict(), 'mapsetdatasets': []}

            all_mapset_datasets = product.get_subproducts(mapset=mapsetcode)
            for subproductcode in all_mapset_datasets:
                from_date = None
                to_date = None
                dataset_dbinfo = querydb.get_subproduct(productcode=productcode,
                                                        version=version,
                                                        subproductcode=subproductcode)
                kwargs = {'mapset': mapsetcode,
                          'sub_product_code': subproductcode}
                if dataset_dbinfo is not None:
                    if hasattr(dataset_dbinfo, 'frequency_id'):
                        if dataset_dbinfo.frequency_id == 'e15minute':
                            today = datetime.date.today()
                            from_date = today - datetime.timedelta(days=int(high_frequency))
                            to_date = today + datetime.timedelta(days=1)
                            kwargs = {'mapset': mapsetcode,
                                      'sub_product_code': subproductcode,
                                      'from_date': from_date,
                                      'to_date': to_date}
                        elif dataset_dbinfo.frequency_id == 'e30minute':
                            today = datetime.date.today()
                            from_date = today - datetime.timedelta(days=int(high_frequency))
                            to_date = today + datetime.timedelta(days=1)
                            kwargs = {'mapset': mapsetcode,
                                      'sub_product_code': subproductcode,
                                      'from_date': from_date,
                                      'to_date': to_date}
                        elif dataset_dbinfo.frequency_id == 'e1day':
                            today = datetime.date.today()
                            from_date = today - relativedelta(years=int(daily_frequency))
                            # if sys.platform != 'win32':
                            #     from_date = today - relativedelta(years=1)
                            # else:
                            #     from_date = today - datetime.timedelta(days=365)
                            kwargs = {'mapset': mapsetcode,
                                      'sub_product_code': subproductcode,
                                      'from_date': from_date}
                        elif dataset_dbinfo.date_format == 'YYYYMMDD':  # dataset_dbinfo.frequency_id == 'e1dekad' and
                            today = datetime.date.today()
                            from_date = today - relativedelta(years=int(dekad_frequency))
                            from_date = from_date.replace(day=1)  # always start at the first of the month!

                            kwargs = {'mapset': mapsetcode,
                                      'sub_product_code': subproductcode,
                                      'from_date': from_date}
                        else:
                            kwargs = {'mapset': mapsetcode,
                                      'sub_product_code': subproductcode}

                    dataset = product.get_dataset(**kwargs)
                    # dataset = product.get_dataset(mapset=mapsetcode, sub_product_code=subproductcode,
                    #                               from_date=None, to_date=None)

                    dataset_info = dataset.get_dataset_normalized_info()
                    tot_files = dataset_info['totfiles']
                    if tot_files == 0:
                        from_date = get_from_date(dataset.frequency_id, dataset.date_format)
                        to_date = datetime.date.today()

                    missing_info = product.get_missing_datasets(mapset=mapsetcode, sub_product_code=subproductcode,
                                                                from_date=from_date, to_date=to_date)
                    filenames = []
                    # Loop over missing objects
                    for missing in missing_info:
                        try:
                            filenames.extend(product.get_missing_filenames(missing, existing_only=False,
                                                                           for_request_creation=True))
                        except NoProductFound:
                            pass

                    # Remove the processing dir from file path because this can be different for each
                    # installation (especially the windows version) than on the cloud service processing dir
                    filenames[:] = [
                        os.path.join(os.path.sep, os.path.relpath(filename, es_constants.es2globals['processing_dir']))
                        for filename in
                        filenames]
                    # for filename in filenames:
                    #     print filename

                    dataset_dict = {'subproductcode': subproductcode,
                                    "allfiles": False,
                                    'missingfiles': filenames}
                    mapset_dict['mapsetdatasets'].append(dataset_dict)

            request['productmapsets'].append(mapset_dict)
        else:
            from_date = None
            to_date = None

            request['productmapsets'] = []
            mapset_obj = Mapset(mapset_code=mapsetcode)
            mapset_corrected = correctMapset(mapset_obj.to_dict())
            mapset_dict = {'mapset': mapset_corrected, 'mapsetdatasets': []}
            # mapset_dict = {'mapset': mapset_obj.to_dict(), 'mapsetdatasets': []}

            # All variable defined -> get missing object
            dataset_dbinfo = querydb.get_subproduct(productcode=productcode,
                                                    version=version,
                                                    subproductcode=subproductcode)
            kwargs = {'mapset': mapsetcode,
                      'sub_product_code': subproductcode}
            if dataset_dbinfo is not None:
                if hasattr(dataset_dbinfo, 'frequency_id'):
                    if dataset_dbinfo.frequency_id == 'e15minute':
                        today = datetime.date.today()
                        from_date = today - datetime.timedelta(days=int(high_frequency))
                        to_date = today + datetime.timedelta(days=1)
                        # from_date = today - relativedelta(days=int(high_frequency))
                        kwargs = {'mapset': mapsetcode,
                                  'sub_product_code': subproductcode,
                                  'from_date': from_date,
                                  'to_date': to_date}
                    elif dataset_dbinfo.frequency_id == 'e30minute':
                        today = datetime.date.today()
                        from_date = today - datetime.timedelta(days=int(high_frequency))
                        # from_date = today - relativedelta(days=int(high_frequency)*2)
                        to_date = today + datetime.timedelta(days=1)
                        kwargs = {'mapset': mapsetcode,
                                  'sub_product_code': subproductcode,
                                  'from_date': from_date,
                                  'to_date': to_date}
                    elif dataset_dbinfo.frequency_id == 'e1day':
                        today = datetime.date.today()
                        from_date = today - relativedelta(years=int(daily_frequency))
                        # if sys.platform != 'win32':
                        #     from_date = today - relativedelta(years=1)
                        # else:
                        #     from_date = today - datetime.timedelta(days=365)
                        kwargs = {'mapset': mapsetcode,
                                  'sub_product_code': subproductcode,
                                  'from_date': from_date}
                    elif dataset_dbinfo.date_format == 'YYYYMMDD':  # dataset_dbinfo.frequency_id == 'e1dekad' and
                        today = datetime.date.today()
                        from_date = today - relativedelta(years=int(dekad_frequency))
                        from_date = from_date.replace(day=1)  # always start at the first of the month!

                        kwargs = {'mapset': mapsetcode,
                                  'sub_product_code': subproductcode,
                                  'from_date': from_date}
                    else:
                        kwargs = {'mapset': mapsetcode,
                                  'sub_product_code': subproductcode}

                dataset = product.get_dataset(**kwargs)
                # dataset = product.get_dataset(mapset=mapsetcode, sub_product_code=subproductcode, from_date=None,
                #                               to_date=None)

                dataset_info = dataset.get_dataset_normalized_info()
                tot_files = dataset_info['totfiles']
                if tot_files == 0:
                    from_date = get_from_date(dataset.frequency_id, dataset.date_format)
                    to_date = datetime.date.today()

                missing_info = product.get_missing_datasets(mapset=mapsetcode, sub_product_code=subproductcode,
                                                            from_date=from_date, to_date=to_date)
                filenames = []
                # Loop over missing objects
                for missing in missing_info:
                    try:
                        filenames.extend(product.get_missing_filenames(missing, existing_only=False,
                                                                       for_request_creation=True))
                    except NoProductFound:
                        pass

                # Remove the processing dir from file path because this can be different for each
                # installation (especially the windows version) than on the cloud service processing dir
                filenames[:] = [
                    os.path.join(os.path.sep, os.path.relpath(filename, es_constants.es2globals['processing_dir'])) for
                    filename in
                    filenames]
                # for filename in filenames:
                #     print filename

                dataset_dict = {'subproductcode': subproductcode, "allfiles": False, 'missingfiles': filenames}
                mapset_dict['mapsetdatasets'].append(dataset_dict)
            request['productmapsets'].append(mapset_dict)
    return request
    # Dump the request object to JSON


def __create_request(productcode, version, mapsetcode=None, subproductcode=None):
    # Define the 'request' object
    request = {'product': productcode,
               'version': version}

    product = Product(product_code=productcode, version=version)
    # Check the level of the request
    if mapsetcode is None:
        if subproductcode is not None:
            logger.error('Create Request: If mapset is not defined, subproduct cannot be defined!')
            return request
        else:
            all_prod_mapsets = product.mapsets
            all_prod_subproducts = product.subproducts
            if all_prod_mapsets.__len__() > 0 and all_prod_subproducts.__len__() > 0:
                request['productmapsets'] = []
                mapset_dict = {}
                dataset_dict = {}
                for mapset in all_prod_mapsets:
                    mapset_dict = {'mapsetcode': mapset, 'mapsetdatasets': []}
                    # request['productmapsets'].append(mapset_dict)

                    dataset_dict = {}
                    all_mapset_datasets = product.get_subproducts(mapset=mapset)
                    for subproductcode in all_mapset_datasets:
                        missing = product.get_missing_datasets(mapset=mapset, sub_product_code=subproductcode,
                                                               from_date=None, to_date=None)
                        # dataset_dict['subproductcode'] = row_dict['subproductcode']
                        # dataset_dict['product_type'] = row_dict['product_type']
                        dataset_dict = {'subproductcode': subproductcode,
                                        'missing': missing,
                                        'product_type': ''}
                        mapset_dict['mapsetdatasets'].append(dataset_dict)
                        dataset_dict = {}

                    request['productmapsets'].append(mapset_dict)
    # Mapset is defined
    else:
        if subproductcode is None:
            # Get full list of subproducts (ingest/derived) for the given mapset
            request['productmapsets'] = []
            mapset_dict = {'mapsetcode': mapsetcode, 'mapsetdatasets': []}

            dataset_dict = {}
            all_mapset_datasets = product.get_subproducts(mapset=mapsetcode)
            for subproductcode in all_mapset_datasets:
                missing = product.get_missing_datasets(mapset=mapsetcode, sub_product_code=subproductcode,
                                                       from_date=None, to_date=None)
                # dataset_dict['subproductcode'] = row_dict['subproductcode']
                # dataset_dict['product_type'] = row_dict['product_type']
                dataset_dict = {'subproductcode': subproductcode,
                                'missing': missing,
                                'product_type': ''}
                mapset_dict['mapsetdatasets'].append(dataset_dict)
                dataset_dict = {}

            request['productmapsets'].append(mapset_dict)

        else:
            # All variable defined -> get missing object
            # product = Product(product_code=productcode, version=version)
            missing = product.get_missing_datasets(mapset=mapsetcode, sub_product_code=subproductcode, from_date=None,
                                                   to_date=None)
            request['productmapsets'] = []
            mapset_dict = {'mapsetcode': mapsetcode, 'mapsetdatasets': []}
            dataset_dict = {'subproductcode': subproductcode, 'missing': missing}
            mapset_dict['mapsetdatasets'].append(dataset_dict)
            request['productmapsets'].append(mapset_dict)
    return request
    # Dump the request object to JSON


def create_archive_from_request(request_file):
    # Creates an archive file (.tgz) from a 'json' request file
    # Create a self-extracting archive (.bsx) from a template script and the .tgz

    # Read the request
    try:
        with open(request_file) as json_req:
            my_request = json.load(json_req)
            json_req.close()
    except:
        logger.error('Error in reading the request. Exit')
        return 1

    my_product = my_request['product']
    my_version = my_request['version']
    # See ES2-64 : mapset MUST be specified
    try:
        my_mapsets = my_request['productmapsets']
    except:
        logger.error('No mapset defined in the request: cannot proceed. Exit')
        return 1

    n_mapsets = len(my_mapsets)
    incresing_number = 1

    # Loop over defined mapsets
    for my_mapset in my_mapsets:
        mapsetcode = my_mapset['mapsetcode']

        mapsetdatasets = my_mapset['mapsetdatasets']

        # Loop over all datasets in a mapset
        for mapsetdataset in mapsetdatasets:
            subproductcode = mapsetdataset['subproductcode']
            missing_info = mapsetdataset['missing']
            archive_base_name = request_file.replace('.req', '')
            archive_name = archive_base_name + '_{0:04d}'.format(incresing_number) + '.tgz'
            self_extracting_name = archive_name
            self_extracting_name = self_extracting_name.replace('.tgz', '.bsx')
            logger.debug('Archive file name: {0}'.format(archive_name))

            # Create a product object - no date indication
            product = Product(product_code=my_product, version=my_version)
            [tarfile, results] = product.create_tar(missing_info, filetar=archive_name, tgz=True)
            logger.debug('Files found for {0}: {1}'.format(subproductcode, results['n_file_copied']))
            # Test there is - at list - 1 file missing
            if results['n_file_copied'] > 0:
                logger.info('Creating file {0}'.format(self_extracting_name))
                # Get the decompression script template
                decompress_file = es_constants.decompress_script

                target = open(self_extracting_name, 'wb')
                shutil.copyfileobj(open(decompress_file, 'rb'), target)
                shutil.copyfileobj(open(archive_name, 'rb'), target)
                target.close()
                os.chmod(self_extracting_name, 775)
                # Increase the counter
                incresing_number += 1

                # Remove .tgz file
                os.remove(archive_name)

            product = None
    return 0


def get_archive_name(productcode, version, id):
    filename = es_constants.es2globals['base_tmp_dir'] + os.path.sep
    filename += 'archive_' + productcode + '_' + version + '_' + id + '.tgz'
    return filename


def get_request_filename(productcode, version, subproductcode, mapsetcode, date=None):
    if date is None:
        filename = productcode + '_' + subproductcode + '_' + mapsetcode + '_' + version

    return filename


def create_archive_vars(productcode, version, mapsetcode, subproductcode, from_date=None, to_date=None,
                        time_suffix=None, output_dir=None):
    # Creates an archive file (.tgz) for a single period (prod/version/sprod/mapset)
    incresing_number = 1

    if output_dir is None:
        output_dir = es_constants.es2globals['base_tmp_dir']

    if time_suffix is not None:
        time_token = str(time_suffix)
    else:
        if from_date is not None:
            time_token = from_date
            if to_date is not None:
                time_token += '_to_'
                time_token += to_date
        else:
            time_token = 'alltimes'

    # Define archive name
    archive_base_name = output_dir + os.path.sep + \
                        productcode + '_' + version + '_' + mapsetcode + '_' + subproductcode + '_' + time_token

    archive_name = archive_base_name + '_{0:04d}'.format(incresing_number) + '.tgz'
    self_extracting_name = archive_name
    self_extracting_name = self_extracting_name.replace('.tgz', '.bsx')

    logger.debug('Archive file name: {0}'.format(archive_name))

    # Create a product object - no date indication
    product = Product(product_code=productcode, version=version)
    [tarfile, results] = product.create_tar_vars(productcode, version, subproductcode, mapsetcode, from_date=from_date,
                                                 to_date=to_date, filetar=archive_name, tgz=True)

    logger.info('Tar archive created: {0}'.format(archive_name))
    logger.debug('Files found for {0}: {1}'.format(subproductcode, results['n_file_copied']))

    # Test there is - at list - 1 file missing
    if results['n_file_copied'] > 0:
        logger.info('Creating file {0}'.format(self_extracting_name))
        # Get the decompression script template
        decompress_file = es_constants.decompress_script

        target = open(self_extracting_name, 'wb')
        shutil.copyfileobj(open(decompress_file, 'rb'), target)
        shutil.copyfileobj(open(archive_name, 'rb'), target)
        target.close()
        os.chmod(self_extracting_name, 775)
        # Increase the counter
        incresing_number += 1

    # Remove .tgz file
    os.remove(archive_name)
    product = None

    return self_extracting_name
