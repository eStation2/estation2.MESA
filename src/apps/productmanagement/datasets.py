# -*- coding: utf-8 -*-
#
#    purpose: Dataset functions
#    author:  Marco Beri marcoberi@gmail.com
#    date:    09.07.2014
#

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function

from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
from past.utils import old_div
from builtins import object
import datetime
import calendar
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
from .helpers import (add_years, add_months, add_dekads, add_pentads, add_days, manage_date,
                      find_gaps, cast_to_int, INTERVAL_TYPE, FILE_EXTENSIONS, add_cgl_dekads)


def _check_constant(class_, constant_name, value):
    for k, v in list(getattr(getattr(class_, constant_name, None),
                        '__dict__', {}).items()):
        if k.isupper() and v == value:
            return True
    return False


#
#   Class to define a dataset frequency, i.e. the repeat-time of a dataset
#   It includes:    type ('every' or 'per')
#                   unit (minute, hour, day, ...)
#                   value (integer)
#                   and dateformat (date/datetime)
#
class Frequency(object):
    class UNIT(object):
        YEAR = 'year'
        MONTH = 'month'
        DEKAD = 'dekad'
        CGL_DEKAD = 'cgl_dekad'
        DAYS8 = '8days'
        DAYS16 = '16days'
        PENTAD = 'pentad'
        DAY = 'day'
        HOUR = 'hour'
        MINUTE = 'minute'
        NONE = 'none'
        DAYS7 = '7days'

    class TYPE(object):
        PER = 'p'
        EVERY = 'e'
        NONE = 'n'

    class DATEFORMAT(object):
        DATETIME = 'YYYYMMDDHHMM'
        DATE = 'YYYYMMDD'
        MONTHDAY = 'MMDD'
        YYYY = 'YYYY'

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
            if len(date) > 8:
                # String like: '1998-02-01' -> returns 02-01
                return date[5:]
            else:
                # String like: '19980201'   -> returns 0201
                return date[4:]
        return date

    def format_date(self, date):
        if self.dateformat == self.DATEFORMAT.DATE:
            return date.strftime("%Y%m%d")
        elif self.dateformat == self.DATEFORMAT.MONTHDAY:
            return date.strftime("%m%d")
        elif self.dateformat == self.DATEFORMAT.DATETIME:
            return date.strftime("%Y%m%d%H%M")
        elif self.dateformat == self.DATEFORMAT.YYYY:
            return date.strftime("%Y")
        else:
            raise Exception("Dateformat not managed: %s" % self.dateformat)

    def get_next_date(self, date, unit, value):
        if unit == self.UNIT.YEAR:
            return add_years(date, value)
        elif unit == self.UNIT.MONTH:
            return add_months(date, value)
        elif unit == self.UNIT.DAYS8:
            # Dates for (modis) 8days stats (MMDD) in leap years follow the non leap year convention
            # See processing_modis_pp.py where the MMDD 8days dates are hardcoded NON leap year dates.
            if self.unit == '8days' and self.dateformat == 'MMDD' \
                    and calendar.isleap(date.year) and add_days(date, value, 9) == datetime.date(date.year, 3, 6):
                return add_days(date, value, 9)
            else:
                return add_days(date, value, 8)
        elif unit == self.UNIT.DAYS16:
            return add_days(date, value, 16)
        elif unit == self.UNIT.DAYS7:
            return add_days(date, value, 7)
        elif unit == self.UNIT.DEKAD:
            return add_dekads(date, value)
        elif unit == self.UNIT.CGL_DEKAD:
            return add_cgl_dekads(date, value)
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
            # raise Exception("Unit not managed: %s" % unit)

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

    # In case of date_format='mmdd', it adds the current year
    def extract_date(self, filename):
        try:
            date = None
            if self.dateformat == self.DATEFORMAT.MONTHDAY:
                date_parts = (datetime.date.today().year, int(filename[:2]), int(filename[2:4]))
                date = datetime.date(*date_parts)
            elif self.dateformat == self.DATEFORMAT.YYYY:
                date_parts = (int(filename[:4]), 1, 1)
                date = datetime.date(*date_parts)
            else:
                date_parts = (int(filename[:4]), int(filename[4:6]), int(filename[6:8]))
                if self.dateformat == self.DATEFORMAT.DATE:
                    date = datetime.date(*date_parts)
                else:
                    date_parts += (int(filename[8:10]), int(filename[10:12]))
                    date = datetime.datetime(*date_parts)
        except:
            logger.warning('Error in managing file: %s' % filename)

        return date

    # It is done for the case of date_format='mmdd': it returns list of existing 'mmdd'
    def extract_mmdd(self, filename):
        if self.dateformat == self.DATEFORMAT.MONTHDAY:
            mmdd = (str(filename[:4]))
        else:
            logger.error('Extract_mmdd() to be used only for MMDD format')
            mmdd = None
        return mmdd

    def next_date(self, date):
        if self.frequency_type == self.TYPE.EVERY or self.value == 1:
            # print (date.strftime("%Y%m%d%H%M"))
            date = self.get_next_date(date, self.unit, self.value)
        elif self.frequency_type == self.TYPE.PER:
            new_date = self.get_next_date(date, self.unit, 1)
            date = date + old_div((new_date - date), self.value)
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

    # ES2-281 Check if the start date corresponds to the frequency type and skip the dates
    def cast_to_frequency(self, fromdate):
        if self.unit == self.UNIT.DEKAD:
            if fromdate.day != 1:
                fromdate = fromdate.replace(day=1)

        elif self.unit == self.UNIT.CGL_DEKAD:
            if fromdate.day != 10 or fromdate.day == 20 or fromdate.day == functions.get_number_days_month(str(fromdate.year) + fromdate.strftime('%m') + fromdate.strftime('%d')):
                fromdate = fromdate.replace(day=10)

        return fromdate

    def get_dates(self, fromdate, todate):
        # ES2-281 To make the dates robust:
        fromdate = self.cast_to_frequency(fromdate)

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
        # %{dkm}
        # %{+/-<Nt><strftime>} = +/- N delta days/hours/
        return [manage_date(date, template) for date in dates]

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


# Class to define a temporal interval and logically refers to a fraction of a dataset
#   It includes:    from_date -> to_date
#                   Length
#                   percentage      (wrt to dataset extension)
#                   interval_type   (present/missing/permanently missing)
#
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


# Class to define a dataset, i.e. a collection of EO images, identified by the 4 key:
#                              product/version/subproduct/mapset
#   It also includes:    from_date -> to_date
#

class Dataset(object):
    def _check_date(self, date):
        if not isinstance(date, datetime.date):
            raise WrongDateType(date, datetime.date)

    def __init__(self, product_code, sub_product_code, mapset, version=None, from_date=None, to_date=None):
        kwargs = {'productcode': product_code,
                  'subproductcode': sub_product_code.lower() if sub_product_code else None}
        if version is not None:
            kwargs['version'] = version
        if from_date is not None:
            self._check_date(from_date)
        if to_date is not None:
            self._check_date(to_date)

        self.mapset = mapset

        self._db_product = querydb.get_product_out_info(**kwargs)
        if self._db_product is None or self._db_product == []:
            # Todo: raising and error crashes the system. Log the error and create an empty Dataset instance
            # Todo: set all values of self._db_product to 'undefined'?
            # raise NoProductFound(kwargs)
            self._path = None
            self.fullpath = None
            self.frequency_id = 'undefined'
            self.date_format = None
            self._frequency = None
            self.from_date = None
            self.to_date = None
        else:
            if isinstance(self._db_product, list):
                self._db_product = self._db_product[0]

            self._path = functions.set_path_sub_directory(product_code,
                                                          sub_product_code,
                                                          self._db_product.product_type,
                                                          version,
                                                          mapset)
            self.fullpath = os.path.join(es_constants.es2globals['processing_dir'], self._path)

            # self._db_frequency = querydb.db.frequency.get(self._db_product.frequency_id)
            # self._db_frequency = querydb.get_frequency(self._db_product.frequency_id)
            # if self._db_frequency is None:
            #    raise NoFrequencyFound(self._db_product)
            # self._frequency = Frequency(value=self._db_frequency.frequency,
            #                            unit=self._db_frequency.time_unit,
            #                            frequency_type=self._db_frequency.frequency_type,
            #                            dateformat=self._db_product.date_format)

            self.frequency_id = self._db_product.frequency_id
            self.date_format = self._db_product.date_format

        self._frequency = self.get_frequency(self.frequency_id, self.date_format)

        if not from_date and self.no_year():
            from_date = datetime.date(datetime.date.today().year, 1, 1)
        if not to_date and self.no_year():
            to_date = datetime.date(datetime.date.today().year, 12, 31)
        self.from_date = from_date or None
        self.to_date = to_date or self._frequency.today()

    @staticmethod
    def get_frequency(frequency_id, dateformat):
        _db_frequency = querydb.get_frequency(frequency_id)
        if _db_frequency is None:
            raise NoFrequencyFound(frequency_id)
        return Frequency(value=_db_frequency.frequency,
                         unit=_db_frequency.time_unit,
                         frequency_type=_db_frequency.frequency_type,
                         dateformat=dateformat)

    def next_date(self, date):
        return self._frequency.next_date(date)

    def get_filenames(self, regex='*'):
        # self._regex = regex
        # self._filenames = glob.glob(os.path.join(self.fullpath, regex))
        filenames = []
        if self.fullpath:
            filenames = glob.glob(os.path.join(self.fullpath, regex))
        return filenames

    def get_filenames_range(self):
        all_files = []
        if self.fullpath:
            all_files = glob.glob(os.path.join(self.fullpath, "*"))
        filenames = []
        for file in all_files:
            str_date = functions.get_date_from_path_full(file)
            my_date = datetime.date(int(str_date[0:4]), int(str_date[4:6]), int(str_date[6:8]))
            if my_date >= self.from_date and my_date <= self.to_date:
                filenames.append((file))
        return filenames

    def get_number_files(self):
        return len(self.get_filenames())

    def get_basenames(self, regex='*'):
        # return list(os.path.basename(filename) for filename in self.get_filenames())
        return list(os.path.basename(filename) for filename in self.get_filenames(regex=regex)
                    if len(os.path.basename(filename).split('_')) == 5 and filename.endswith((FILE_EXTENSIONS.TIF_FILE_EXTENSION, FILE_EXTENSIONS.MISSING_FILE_EXTENSION)))

    def no_year(self):
        return self._frequency.no_year()

    def strip_year(self, date):
        return self._frequency.strip_year(date)

    def format_filename(self, date):
        return os.path.join(self.fullpath, self._frequency.format_filename(date, self.mapset))

    def get_first_date(self):
        return self.intervals[0].from_date

    def get_last_date(self):
        endate = datetime.date.today()
        if self.intervals.__len__() > 0:
            endate = self.intervals[-1].to_date
        return endate

    def get_regex_from_range(self, from_date, to_date):
        regex = ''
        str_from = from_date.strftime("%Y%m%d%H%M")
        str_to = to_date.strftime("%Y%m%d%H%M")
        len_date = len(str_from)
        for i in range(len_date):
            if str_from[i] == str_to[i]:
                regex += str_from[i]
            else:
                regex += '[' + str_from[i] + '-' + str_to[
                    i] + ']' + '*'  # + '[\.tif|\.missing]'  ['+FILE_EXTENSIONS.TIF_FILE_EXTENSION + '-' + FILE_EXTENSIONS.MISSING_FILE_EXTENSION + ']'
                return regex

    def find_intervals(self, from_date=None, to_date=None, only_intervals=True):
        regex = '*'     #  +'[\.tif|\.missing]'
        if from_date is not None and to_date is not None and not self.no_year():
            regex = self.get_regex_from_range(from_date, to_date)

        return find_gaps(self.get_basenames(regex=regex), self._frequency, only_intervals,
                         from_date=from_date or self.from_date, to_date=to_date or self.to_date)

    def find_gaps(self, from_date=None, to_date=None):
        regex = '*'     # + '[\.tif|\.missing]'
        if from_date is not None and to_date is not None and not self.no_year():
            regex = self.get_regex_from_range(from_date, to_date)

        return find_gaps(self.get_basenames(regex=regex), self._frequency, only_intervals=False,
                         from_date=from_date or self.from_date, to_date=to_date or self.to_date)

    def get_interval_dates(self, from_date, to_date, last_included=True, first_included=True):
        dates = []
        first_cycle = True
        # print (from_date.strftime("%Y%m%d%H%M"))
        # print (to_date.strftime("%Y%m%d%H%M"))
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

    def get_mmdd(self):
        return sorted(self._frequency.extract_mmdd(filename) for filename in self.get_basenames())

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
        if self._frequency.frequency_type == 'n':
            missingfiles = 0
            totfilespresent = len(self.get_basenames(regex='*'))
            if totfilespresent == 0:
                missingfiles = 1

            return {
                'firstdate': '',
                'lastdate': '',
                'totfiles': 1,
                'missingfiles': missingfiles,
                'intervals': ''
            }

        dateformat = "%Y-%m-%d"
        if self._frequency.dateformat == self._frequency.DATEFORMAT.DATETIME:
            dateformat = "%Y-%m-%d %H:%M"

        if from_date and (not self.from_date or from_date < self.from_date):
            self.from_date = from_date
            refresh = True
        if to_date and (not self.to_date or to_date < self.to_date):
            self.to_date = to_date
            refresh = True
        if refresh:
            self._clean_cache()
        interval_list = list({'totfiles': interval.length,
                              'fromdate': self.strip_year(interval.from_date.strftime(dateformat)),
                              'todate': self.strip_year(interval.to_date.strftime(dateformat)),
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
            _intervals = [Interval(**self._extract_kwargs(interval)) for interval in
                          self.find_intervals(from_date=self.from_date, to_date=self.to_date)]
            setattr(self, "_intervals", _intervals)
        return _intervals
