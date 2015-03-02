# -*- coding: utf-8 -*-
#
#    purpose: Dataset functions
#    author:  Marco Beri marcoberi@gmail.com
#    date:    09.07.2014
#

from __future__ import absolute_import

import datetime
import os
import glob

from config import es_constants
from lib.python import es_logging as log
from lib.python import functions
from database import querydb


logger = log.my_logger(__name__)


from .exceptions import (WrongFrequencyValue, WrongFrequencyUnit,
                         WrongFrequencyType, WrongFrequencyDateFormat,
                         NoProductFound, NoFrequencyFound,
                         WrongDateType)
from .helpers import add_years, add_months, add_dekads, add_pentads, add_days, find_gaps, cast_to_int, INTERVAL_TYPE


def _check_constant(class_, constant_name, value):
    for k, v in getattr(getattr(class_, constant_name, None),
            '__dict__', {}).items():
        if k.isupper() and v == value:
            return True
    return False

class Frequency(object):
    class UNIT:
        YEAR = 'year'
        MONTH = 'month'
        DEKAD = 'dekad'
        DAYS8 = '8days'
        DAYS16 = '16days'
        PENTAD = 'pentad'
        DAY = 'day'
        HOUR = 'hour'
        MINUTE = 'minute'

    class TYPE:
        PER = 'p'
        EVERY = 'e'

    class DATEFORMAT:
        DATETIME = 'YYYYMMDDHHMM'
        DATE = 'YYYYMMDD'
        MONTHDAY = 'MMDD'

    @classmethod
    def dateformat_default(class_, unit):
        if unit in (class_.UNIT.HOUR, class_.UNIT.MINUTE,):
            return class_.DATEFORMAT.DATETIME
        return class_.DATEFORMAT.DATE

    def today(self):
        if self.dateformat == self.DATEFORMAT.DATETIME:
            return datetime.datetime.today()
        return datetime.date.today()

    def filename_mask_ok(self, filename):
        if len(filename) > len(self.dateformat) + 1:
            if filename[:len(self.dateformat)].isdigit():
                return filename[len(self.dateformat)] == "_"
        return False

    def no_year(self):
        return self.dateformat == self.DATEFORMAT.MONTHDAY

    def strip_year(self, date):
        if self.no_year():
            return date[5:]
        return date

    def format_date(self, date):
        if self.dateformat == self.DATEFORMAT.DATE:
            return date.strftime("%Y%m%d")
        elif self.dateformat == self.DATEFORMAT.MONTHDAY:
            return date.strftime("%m%d")
        elif self.dateformat == self.DATEFORMAT.DATETIME:
            return date.strftime("%Y%m%d%H%M")
        else:
            raise Exception("Dateformat not managed: %s" % self.dateformat)

    def get_next_date(self, date, unit, value):
        if unit == self.UNIT.YEAR:
            return add_years(date, value)
        elif unit == self.UNIT.MONTH:
            return add_months(date, value)
        elif unit == self.UNIT.DAYS8:
            return add_days(date, value, 8)
        elif unit == self.UNIT.DAYS16:
            return add_days(date, value, 16)
        elif unit == self.UNIT.DEKAD:
            return add_dekads(date, value)
        elif unit == self.UNIT.PENTAD:
            return add_pentads(date, value)
        elif unit == self.UNIT.DAY:
            return date + datetime.timedelta(days=value)
        elif unit == self.UNIT.HOUR:
            return date + datetime.timedelta(hours=value)
        elif unit == self.UNIT.MINUTE:
            return date + datetime.timedelta(minutes=value)
        else:
            logger.error("Unit not managed: %s" % unit)
            #raise Exception("Unit not managed: %s" % unit)

    def get_mapset(self, filename):
        return filename[len(self.dateformat):]

    def format_filename(self, date, mapset):
        return self.format_date(date) + mapset

    def check_date(self, date_datetime):
        if type(date_datetime) is datetime.datetime and (
                self.dateformat in (self.DATEFORMAT.DATE, self.DATEFORMAT.MONTHDAY)):
            return False
        if type(date_datetime) is datetime.date and self.dateformat == self.DATEFORMAT.DATETIME:
            return False
        return True

    def extract_date(self, filename):
        if self.dateformat == self.DATEFORMAT.MONTHDAY:
            date_parts = (datetime.date.today().year, int(filename[:2]), int(filename[2:4]))
            date = datetime.date(*date_parts)
        else:
            date_parts = (int(filename[:4]), int(filename[4:6]), int(filename[6:8]))
            if self.dateformat == self.DATEFORMAT.DATE:
                date = datetime.date(*date_parts)
            else:
                date_parts += (int(filename[8:10]), int(filename[10:12]))
                date = datetime.datetime(*date_parts)
        return date

    def next_date(self, date):
        if self.frequency_type == self.TYPE.EVERY or self.value == 1:
            date = self.get_next_date(date, self.unit, self.value)
        elif self.frequency_type == self.TYPE.PER:
            new_date = self.get_next_date(date, self.unit, 1)
            date = date + (new_date - date)/self.value
        else:
            raise Exception("Dateformat not managed: %s" % self.dateformat)
        return date

    def count_dates(self, fromdate, todate):
        date = self.next_date(fromdate)
        count = 1
        while date <= todate:
            date_next = self.next_date(date)
            if date_next == date:
                raise Exception("Endless loop: %s" % date)
            date = date_next
            count += 1
        return count

    def get_dates(self, fromdate, todate):
        if fromdate > todate:
            raise Exception("'To date' must be antecedent respect 'From date': %s %s" % (
                fromdate, todate))
        dates = [fromdate]
        while dates[-1] <= todate:
            dates.append(self.next_date(dates[-1]))
            if dates[-1] == dates[-2]:
                raise Exception("Endless loop: %s" % dates[-1])
        return dates[:-1]

    def get_internet_dates(self, dates, template):
        return [date.strftime(template) for date in dates]

    def next_filename(self, filename):
        date = self.next_date(self.extract_date(filename))
        return self.format_filename(date, self.get_mapset(filename))

    def __init__(self, value, unit, frequency_type, dateformat=None):
        value = cast_to_int(value)
        unit = unit.lower()
        frequency_type = frequency_type.lower()
        if dateformat:
            dateformat = dateformat.upper()
        if not isinstance(value, int):
            raise WrongFrequencyValue(value)
        if not _check_constant(self, 'UNIT', unit):
            raise WrongFrequencyUnit(unit)
        if not _check_constant(self, 'TYPE', frequency_type):
            raise WrongFrequencyType(frequency_type)
        if dateformat and not _check_constant(self, 'DATEFORMAT', dateformat):
            raise WrongFrequencyDateFormat(dateformat)
        self.value = value
        self.unit = unit
        self.frequency_type = frequency_type
        self.dateformat = dateformat or self.dateformat_default(unit)


class Interval(object):
    def __init__(self, interval_type, from_date, to_date, length, percentage):
        self.interval_type = interval_type
        self.from_date = from_date
        self.to_date = to_date
        self.length = length
        self.percentage = percentage

    @property
    def missing(self):
        return self.interval_type == INTERVAL_TYPE.MISSING


class Dataset(object):
    def _check_date(self, date):
        if not isinstance(date, datetime.date):
            raise WrongDateType(date, datetime.date)

    def __init__(self, product_code, sub_product_code, mapset, version=None, from_date=None, to_date=None):
        kwargs = {'productcode': product_code,
                  'subproductcode': sub_product_code.lower() if sub_product_code else None}
        if not version is None:
            kwargs['version'] = version
        if from_date:
            self._check_date(from_date)
        if to_date:
            self._check_date(to_date)
        self._db_product = querydb.get_product_out_info(**kwargs)
        if self._db_product is None or self._db_product == []:
            raise NoProductFound(kwargs)
        if isinstance(self._db_product, list):
            self._db_product = self._db_product[0]
        self.mapset = mapset
        self._path = functions.set_path_sub_directory(product_code,
                                                      sub_product_code,
                                                      self._db_product.product_type,
                                                      version,
                                                      mapset)
        self.fullpath = os.path.join(es_constants.es2globals['processing_dir'], self._path)
        #self._db_frequency = querydb.db.frequency.get(self._db_product.frequency_id)
        #self._db_frequency = querydb.get_frequency(self._db_product.frequency_id)
        #if self._db_frequency is None:
        #    raise NoFrequencyFound(self._db_product)
        #self._frequency = Frequency(value=self._db_frequency.frequency,
        #                            unit=self._db_frequency.time_unit,
        #                            frequency_type=self._db_frequency.frequency_type,
        #                            dateformat=self._db_product.date_format)
        self._frequency = Dataset.get_frequency(self._db_product.frequency_id, self._db_product.date_format)
        if not from_date and self.no_year():
            from_date = datetime.date(datetime.date.today().year, 1, 1)
        if not to_date and self.no_year():
            to_date = datetime.date(datetime.date.today().year, 12, 1)
        self.from_date = from_date or None
        self.to_date = to_date or self._frequency.today()

    @staticmethod
    def get_frequency(frequency_id, dateformat):
        _db_frequency = querydb.get_frequency(frequency_id)
        if _db_frequency is None:
            raise NoFrequencyFound(frequency_id)
        return  Frequency(value=_db_frequency.frequency,
                                    unit=_db_frequency.time_unit,
                                    frequency_type=_db_frequency.frequency_type,
                                    dateformat=dateformat)


    def next_date(self, date):
        return self._frequency.next_date(date)

    def get_filenames(self):
        return glob.glob(os.path.join(self.fullpath, "*"))

    def get_number_files(self):
        return len(self.get_filenames())

    def get_basenames(self):
        return list(os.path.basename(filename) for filename in self.get_filenames())

    def no_year(self):
        return self._frequency.no_year()

    def strip_year(self, date):
        return self._frequency.strip_year(date)

    def format_filename(self, date):
        return os.path.join(self.fullpath, self._frequency.format_filename(date, self.mapset))

    def get_first_date(self):
        return self.intervals[0].from_date

    def get_last_date(self):
        return self.intervals[-1].to_date

    def find_intervals(self, from_date=None, to_date=None, only_intervals=True):
        return find_gaps(self.get_basenames(), self._frequency, only_intervals,
                         from_date=from_date or self.from_date, to_date=to_date or self.to_date)

    def find_gaps(self, from_date=None, to_date=None):
        return find_gaps(self.get_basenames(), self._frequency, only_intervals=False,
                         from_date=from_date or self.from_date, to_date=to_date or self.to_date)

    def get_interval_dates(self, from_date, to_date, last_included=True, first_included=True):
        dates = []
        first_cycle = True
        while True:
            if not last_included and from_date == to_date:
                break
            if first_included or not first_cycle:
                dates.append(from_date)
            first_cycle = False
            from_date = self.next_date(from_date)
            if from_date > to_date:
                break
        return dates

    def get_dates(self):
        return sorted(self._frequency.extract_date(filename) for filename in self.get_basenames())

    def _extract_kwargs(self, interval):
        return {
            "from_date": interval[0],
            "to_date": interval[1],
            "interval_type": interval[2],
            "length": interval[3],
            "percentage": interval[4],
        }

    def get_dataset_normalized_info(self, from_date=None, to_date=None):
        refresh = False
        if from_date and (not self.from_date or from_date < self.from_date):
            self.from_date = from_date
            refresh = True
        if to_date and (not self.to_date or to_date < self.to_date):
            self.to_date = to_date
            refresh = True
        if refresh:
            self._clean_cache()
        interval_list = list({'totfiles': interval.length,
                     'fromdate': self.strip_year(interval.from_date.strftime("%Y-%m-%d")),
                     'todate': self.strip_year(interval.to_date.strftime("%Y-%m-%d")),
                     'intervaltype': interval.interval_type,
                     'missing': interval.missing,
                     'intervalpercentage': interval.percentage} for interval in self.intervals)
        return {
                'firstdate': interval_list[0]['fromdate'] if interval_list else '',
                'lastdate': interval_list[-1]['todate'] if interval_list else '',
                'totfiles': sum(i['totfiles'] for i in interval_list),
                'missingfiles': sum(i['totfiles'] for i in interval_list if i['missing']),
                'intervals': interval_list
        }

    def _clean_cache(self):
        setattr(self, "_intervals", None)

    @property
    def intervals(self):
        _intervals = getattr(self, "_intervals", None)
        if _intervals is None:
            _intervals = [Interval(**self._extract_kwargs(interval)) for interval in self.find_intervals()]
            setattr(self, "_intervals", _intervals)
        return _intervals
