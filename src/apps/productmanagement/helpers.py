# -*- coding: utf-8 -*-
#
#	purpose: Dataset functions
#	author:  Marco Beri marcoberi@gmail.com
#	date:	 09.07.2014
#

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function

from builtins import dict
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
from builtins import object
from past.utils import old_div
import os
import re
import datetime
import operator
import collections

from lib.python import functions

from .exceptions import WrongSequence, WrongDateParameter, BadDate


def str_to_date(value):
    # If the passed datestring contains the time (e.g. 2019-10-28 00:00'), add the time.
    # print(value)
    # print(type(value))
    parts1 = value.split(" ")
    # print(parts1)
    if len(parts1) == 2:
        parts = parts1[0].split("-")
        parts.extend(parts1[1].split(":"))
        # print(parts)
    else:
        parts = value.split("-")

    if len(parts) == 2:
        return datetime.date(*([datetime.date.today().year] + [int(x) for x in parts]))
    elif len(parts) == 3:
        return datetime.date(*[int(x) for x in parts])
    elif len(parts) == 5:
        return datetime.datetime(*[int(x) for x in parts])
    raise BadDate(value)


def cast_to_int(value):
    if isinstance(value, int):
        return value
    try:
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str) or isinstance(value, unicode):
            return int(value.split(".")[0])
    except ValueError:
        pass
    return value


def no_ext(filename):
    return os.path.splitext(filename)[0]


def get_ext(filename):
    try:
        return os.path.splitext(filename)[1]
    except IndexError:
        return ""


def add_xkads(date, xkads, days=10):
    delta = datetime.timedelta(days)
    for count_dekad in range(xkads):
        new_date = date + delta
        if new_date.day == 31:
            new_date += datetime.timedelta(1)
        elif new_date.month != date.month:
            new_date = date - delta
            new_date = add_months(new_date, 1)
            while new_date.month != date.month:
                new_date -= delta
            new_date += delta
        date = new_date
    return date


def add_cgl_dekads(date, dekads=1):
    # Copernicus global data products are obtained from the vito website and the dekad naming format is different from the actual dekad patern.
    # The dekadal dates are 1stDekad - 10th day, 2ndDekad - 20th day and 3rdDekad - last day of the month.
    new_date = date
    #ES2-502
    isdatetime = isinstance(date, datetime.datetime)
    # ES2-281 Robust way to handle the dates
    if date.day >= 1 and date.day < 10:
        # ES2-502
        if isdatetime:
            new_date = datetime.datetime(new_date.year, new_date.month, 10)
        else:
            new_date = datetime.date(new_date.year, new_date.month, 10)
    elif date.day >= 10 and date.day < 20:
        if isdatetime:
            new_date = datetime.datetime(new_date.year, new_date.month, 20)
        else:
            new_date = datetime.date(new_date.year, new_date.month, 20)
    # elif date.day >= 20 and date.day < 27:
    #     tot_days = functions.get_number_days_month(str(date.year)+date.strftime('%m')+date.strftime('%d'))
    #     new_date = datetime.datetime(new_date.year, new_date.month, tot_days)
    else:
        tot_days = functions.get_number_days_month(str(date.year) + date.strftime('%m') + date.strftime('%d'))  #Last day of the month
        # check if the current day is last date of the month
        if date.day != tot_days:
            if isdatetime:  #ES2-502
                new_date = datetime.datetime(new_date.year, new_date.month, tot_days)
            else:
                new_date = datetime.date(new_date.year, new_date.month, tot_days)
        else:
            new_date = add_months(date, 1)
            if new_date.month != date.month:
                if isdatetime: #ES2-502
                    new_date = datetime.datetime(new_date.year, new_date.month, 10)
                else:
                    new_date = datetime.date(new_date.year, new_date.month, 10)
    date = new_date
    return date


def add_dekads(date, dekads=1):
    return add_xkads(date, dekads, 10)


def add_pentads(date, pentads=1):
    return add_xkads(date, pentads, 5)


def add_days(date, period, days):
    delta = datetime.timedelta(days)
    for count_dekad in range(period):
        new_date = date + delta
        if new_date.year > date.year:
            new_date = datetime.date(new_date.year, 1, 1)
        date = new_date
    return date


def add_months(date, months=1):
    targetmonth = months + date.month
    try:
        date = date.replace(year=date.year + int(old_div((targetmonth - 1),12)), month=((targetmonth - 1)%12 + 1))
    except ValueError:
        # There is an exception if the day of the month we're in does not exist in the target month
        # Go to the FIRST of the month AFTER, then go back one day.
        targetmonth += 1
        date = date.replace(year=date.year + int(old_div((targetmonth - 1),12)), month=((targetmonth - 1)%12 + 1), day=1)
        date -= datetime.timedelta(days=1)
    return date


def add_years(date, years=1):
    try:
        return date.replace(year = date.year + years)
    except ValueError:
        # 29 of february return 28 of february
        return date + (datetime.date(date.year + years, 1, 1)
                - datetime.date(date.year, 1, 1)) - datetime.timedelta(days=1)


SPECIAL_DKM = "%{dkm}"
SPECIAL_DKM2 = "%{dkm2}"
SPECIAL_DKY = "%{dky}"
SPECIAL_ADD = re.compile("(%{)([+-])(\d)([dh])(.+)(})")

def manage_date(date, template):
    #%{dkm}
    while True:
        pos = template.find(SPECIAL_DKM)
        pos2 = template.find(SPECIAL_DKM2)
        pos3 = template.find(SPECIAL_DKY)

        if pos == -1 and pos2 == -1 and pos3 == -1:
            break
        if pos != -1:
            template = template[:pos] + ("3" if date.day > 20
                    else "2" if date.day > 10 else "1") + template[pos+len(SPECIAL_DKM):]
        elif pos2 != -1:
            template = template[:pos2] + ("21" if date.day > 20
                    else "11" if date.day > 10 else "01") + template[pos2+len(SPECIAL_DKM2):]
        elif pos3 != -1:
            template = template[:pos3] + (functions.conv_yyyymmdd_2_dky(date.strftime('%Y%m%d'))) + template[pos3 + len(SPECIAL_DKY):]

    #%{+/-<Nt><strftime>} = +/- N delta days/hours/
    def manage_add_factory(date):
        def manage_add(matchobj):
            groups = matchobj.groups()
            obj = "".join(groups)
            # '%{', '+', '8', 'd', 'Y-m-d', '}'
            n = int(groups[2])
            if groups[3] == 'd':
                delta = datetime.timedelta(days=n)
            elif groups[3] == 'h':
                delta = datetime.timedelta(hours=n)
            else:
                raise Exception("Wrong format in %s" % obj)
            if groups[1] == '-':
                delta = -delta
            elif groups[1] != '+':
                raise Exception("Wrong format in %s" % obj)
            date_new = date + delta
            strf = "".join(("%" + c) if c.isalpha() else c for c in groups[4])
            return date_new.strftime(strf)
        return manage_add
    template = re.sub(SPECIAL_ADD, manage_add_factory(date), template)
    return date.strftime(template)


class INTERVAL_TYPE(object):
    PRESENT = 'present'
    MISSING = 'missing'
    PERMANENT_MISSING = 'permanent-missing'


class FILE_EXTENSIONS(object):
    MISSING_FILE_EXTENSION = ".missing"
    TIF_FILE_EXTENSION = ".tif"


def find_gaps(unsorted_filenames, frequency, only_intervals=False, from_date=None, to_date=None):
    # Find most common filename extension
    # exts = collections.defaultdict(int)
    # for filename in unsorted_filenames:
    #     exts[get_ext(filename)] += 1
    # original_ext, most_common_ext_count = "", 0
    # for ext, count in exts.items():
    #     if count > most_common_ext_count and ext != MISSING_FILE_EXTENSION:
    #         original_ext = ext
    #         most_common_ext_count = count
    # Keep only filenames with that extenions
    # filenames = sorted(no_ext(f) for f in unsorted_filenames
    #                    if not f is None and get_ext(f) in (FILE_EXTENSIONS.TIF_FILE_EXTENSION, FILE_EXTENSIONS.MISSING_FILE_EXTENSION))   # in (original_ext, MISSING_FILE_EXTENSION)) #

    if len(unsorted_filenames) == 0 and not from_date:
        from_date = None
        to_date = None

    filenames = sorted(no_ext(f) for f in unsorted_filenames)

    # Jurvtk: BEGIN remove filenames from list where date not between from_date and to_date
    if from_date is not None and to_date is not None:
        if frequency.dateformat == frequency.DATEFORMAT.DATETIME:
            from_date = datetime.datetime.combine(from_date, datetime.time.min)
            to_date = datetime.datetime.combine(to_date, datetime.time.min)

        filenames = sorted(f for f in filenames
                       if f is not None and frequency.extract_date(f) is not None and frequency.extract_date(f) >= from_date and frequency.extract_date(f) <= to_date)
    # Jurvtk: END remove filenames from list where date not between from_date and to_date

    # original_filenames = dict((no_ext(f), f) for f in unsorted_filenames if not f is None and get_ext(f) in (FILE_EXTENSIONS.TIF_FILE_EXTENSION, FILE_EXTENSIONS.MISSING_FILE_EXTENSION)) # in (original_ext, MISSING_FILE_EXTENSION))     #
    original_filenames = dict((no_ext(f), f) for f in unsorted_filenames)
    if not filenames:
        if not (from_date or to_date):
            return []
        if not from_date:
            from_date = to_date
        elif not to_date:
            to_date = from_date
    else:
        if not from_date:
            from_date = frequency.extract_date(filenames[0])
        if not to_date:
            to_date = frequency.extract_date(filenames[-1])

    for date_parameter in (from_date, to_date):
        if date_parameter and not frequency.check_date(date_parameter):
            raise WrongDateParameter(date_parameter, frequency.dateformat)

    gaps = []
    intervals = []
    current_interval = None
    date = from_date
    mapset = frequency.get_mapset((filenames or [''])[0])
    # dateformatlength = len(frequency.dateformat)
    while date <= to_date:
        current_filename = frequency.format_filename(date, mapset)
        if not filenames or current_filename < filenames[0]:
            # gaps.append(current_filename + original_ext)
            gaps.append(current_filename + FILE_EXTENSIONS.TIF_FILE_EXTENSION)
            if not current_interval or current_interval[2] != INTERVAL_TYPE.MISSING:
                current_interval = [date, date, INTERVAL_TYPE.MISSING, 1, 0.0]
                intervals.append(current_interval)
            else:
                current_interval[1] = date
                current_interval[3] += 1
        else:
            filename = filenames.pop(0)
            original = original_filenames[filename]
            # print 'filename: ' + filename
            # print 'current_filename: ' + current_filename
            if filename < current_filename:
                # raise WrongSequence(original, current_filename + original_ext)
                raise WrongSequence(original, current_filename + FILE_EXTENSIONS.TIF_FILE_EXTENSION)
            else:
                interval_type = INTERVAL_TYPE.PERMANENT_MISSING if original.lower().endswith(FILE_EXTENSIONS.MISSING_FILE_EXTENSION) else INTERVAL_TYPE.PRESENT
                if not current_interval or current_interval[2] != interval_type:
                    current_interval = [date, date, interval_type, 1, 0.0]
                    intervals.append(current_interval)
                else:
                    current_interval[1] = date
                    current_interval[3] += 1
        date = frequency.next_date(date)
    if only_intervals:
        total = sum(interval[3] for interval in intervals)
        remainder = 0.0
        for interval in intervals:
            interval[4] = float(interval[3]*100.0/float(total))
            if interval[4] < 1.0:
                remainder += 1.0 - interval[4]
                interval[4] = 1.0
        index, value = max(enumerate(intervals), key=operator.itemgetter(1))
        intervals[index][4] -= remainder
        return intervals
    return gaps
