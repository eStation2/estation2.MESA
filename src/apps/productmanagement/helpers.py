# -*- coding: utf-8 -*-
#
#	purpose: Dataset functions
#	author:  Marco Beri marcoberi@gmail.com
#	date:	 09.07.2014
#

from __future__ import absolute_import

import os
import re
import datetime
import operator
import collections

from .exceptions import WrongSequence, WrongDateParameter, BadDate

MISSING_FILE_EXTENSION = ".missing"

def str_to_date(value):
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
        date = date.replace(year=date.year + int((targetmonth - 1)/12), month=((targetmonth - 1)%12 + 1))
    except ValueError:
        # There is an exception if the day of the month we're in does not exist in the target month
        # Go to the FIRST of the month AFTER, then go back one day.
        targetmonth += 1
        date = date.replace(year=date.year + int((targetmonth - 1)/12), month=((targetmonth - 1)%12 + 1), day=1)
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
SPECIAL_ADD = re.compile("(%{)([+-])(\d)([dh])(.+)(})")

def manage_date(date, template):
    #%{dkm}
    while True:
        pos = template.find(SPECIAL_DKM)
        if pos == -1:
            break
        template = template[:pos] + ("3" if date.day > 20
                else "2" if date.day > 10 else "1") + template[pos+len(SPECIAL_DKM):]
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


class INTERVAL_TYPE:
    PRESENT = 'present'
    MISSING = 'missing'
    PERMANENT_MISSING = 'permanent-missing'


def find_gaps(unsorted_filenames, frequency, only_intervals=False, from_date=None, to_date=None):
    # Find most common filename extension
    exts = collections.defaultdict(int)
    for filename in unsorted_filenames:
        exts[get_ext(filename)] += 1
    original_ext, most_common_ext_count = "", 0
    for ext, count in exts.items():
        if count > most_common_ext_count and ext != MISSING_FILE_EXTENSION:
            original_ext = ext
            most_common_ext_count = count
    # Keep only filenames with that extenions
    filenames = sorted(no_ext(f) for f in unsorted_filenames
            if not f is None and get_ext(f) in (original_ext, MISSING_FILE_EXTENSION))
    original_filenames = dict((no_ext(f), f) for f in unsorted_filenames if not f is None and get_ext(f) in (original_ext, MISSING_FILE_EXTENSION))
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
    while date <= to_date:
        current_filename = frequency.format_filename(date, mapset)
        if not filenames or current_filename < filenames[0]:
            gaps.append(current_filename + original_ext)
            if not current_interval or current_interval[2] != INTERVAL_TYPE.MISSING:
                current_interval = [date, date, INTERVAL_TYPE.MISSING, 1, 0.0]
                intervals.append(current_interval)
            else:
                current_interval[1] = date
                current_interval[3] += 1
        else:
            filename = filenames.pop(0)
            original = original_filenames[filename]
            if filename < current_filename:
                raise WrongSequence(original, current_filename + original_ext)
            else:
                interval_type = INTERVAL_TYPE.PERMANENT_MISSING if original.lower().endswith(MISSING_FILE_EXTENSION) else INTERVAL_TYPE.PRESENT
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
