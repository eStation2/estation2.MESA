# -*- coding: utf-8 -*-
#
# purpose: Product functions
# author:  Marco Beri marcoberi@gmail.com
# date:  27.10.2014

from __future__ import absolute_import

import os
import glob
import tarfile

from config import es_constants
from lib.python import es_logging as log
from lib.python import functions
from database import querydb

from .exceptions import (NoProductFound, MissingMapset)
from .datasets import Dataset
from .mapsets import Mapset
from .helpers import str_to_date

logger = log.my_logger(__name__)


class Product(object):
    def __init__(self, product_code, version=None):
        self.product_code = product_code
        kwargs = {'productcode': self.product_code}
        self.version = version
        if not version is None:
            kwargs['version'] = version
        self._db_product = querydb.get_product_native(**kwargs)
        if self._db_product is None:
            raise NoProductFound(kwargs)
        self._fullpath = os.path.join(es_constants.es2globals['processing_dir'], product_code)

    @property
    def mapsets(self):
        _mapsets = getattr(self, "_mapsets", None)
        if _mapsets is None:
            _mapsets = [os.path.basename(mapset) for mapset in self._get_full_mapsets()]
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
        return tuple(subproduct for subproduct_type in functions.dict_subprod_type_2_dir.values()
                                for subproduct in glob.glob(os.path.join(self._fullpath, mapset, subproduct_type, "*")))

    def get_dataset(self, mapset, sub_product_code):
        return Dataset(self.product_code, sub_product_code=sub_product_code, mapset=mapset, version=self.version)

    def get_subproducts(self, mapset):
        return [subproduct for subproduct in
                    set(os.path.basename(subproduct) for subproduct in self._get_full_subproducts(mapset=mapset))]

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

    def get_missing_filenames(self, missing):
        product = Product(missing['product'], version=missing['version'])
        mapset = missing['mapset']
        dataset = product.get_dataset(mapset=mapset, sub_product_code=missing['subproduct'])
        dates = dataset.get_dates()
        missing_dates = []
        first_date = None
        last_date = None
        info = missing['info']
        for interval in info['intervals']:
            if first_date is None:
                first_date = str_to_date(interval['fromdate'])
            last_date = str_to_date(interval['todate'])
            if interval['missing']:
                missing_dates.extend(dataset.get_interval_dates(
                    str_to_date(interval['fromdate']), str_to_date(interval['todate'])))
        if len(info['intervals']) == 0:
            missing_dates = dates[:]
        else:
            if missing['from_start']:
                if first_date > dataset.get_first_date():
                    missing_dates.extend(dataset.get_interval_dates(dataset.get_first_date(),
                        first_date, last_included=False))
            if missing['to_end']:
                if last_date < dataset.get_last_date():
                    missing_dates.extend(dataset.get_interval_dates(last_date,
                        dataset.get_last_date(), first_included=False))
        return [dataset.format_filename(date) for date in sorted(set(dates).intersection(set(missing_dates)))]

    @staticmethod
    def create_tar(missing_info, filetar=None, tgz=False):
        if filetar is None:
            import tempfile
            file_temp = tempfile.NamedTemporaryFile()
            filetar = file_temp.name
            file_temp.close()
        filenames = []
        for missing in missing_info:
            try:
                product = Product(missing['product'], version=missing['version'])
                filenames.extend(product.get_missing_filenames(missing))
            except NoProductFound:
                pass
        # creare il tar contenente files
        tar = tarfile.open(filetar, "w|gz" if tgz else "w|")
        for filename in filenames:
            tar.add(filename)
        tar.close()
        return filetar
