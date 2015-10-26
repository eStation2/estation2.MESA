# -*- coding: utf-8 -*-
#
#	purpose: Dataset functions
#	author:  Marco Beri marcoberi@gmail.com
#	date:	 09.07.2014
#

from __future__ import absolute_import


class WrongIntervalType(Exception):
    def __init__(self, type_):
        super(WrongIntervalType, self).__init__(u"Wrong interval type: %s" % type_)


class WrongFrequencyValue(Exception):
    def __init__(self, value):
        super(WrongFrequencyValue, self).__init__(u"Wrong frequency value: %s" % value)


class WrongFrequencyUnit(Exception):
    def __init__(self, unit):
        super(WrongFrequencyUnit, self).__init__(u"Wrong frequency unit: %s" % unit)


class WrongFrequencyType(Exception):
    def __init__(self, type_):
        super(WrongFrequencyType, self).__init__(u"Wrong frequency type: %s" % type_)


class WrongFrequencyDateFormat(Exception):
    def __init__(self, dateformat):
        super(WrongFrequencyDateFormat, self).__init__(u"Wrong frequency dateformat: %s" % dateformat)


class WrongSequence(Exception):
    def __init__(self, filename, filename_expected):
        super(WrongSequence, self).__init__(u"Wrong sequence: found=%s expected=%s"
                % (filename, filename_expected))


class BadDate(Exception):
    def __init__(self, date):
        super(BadDate, self).__init__(u"Bad date: %s" % unicode(date))


class WrongDateType(Exception):
    def __init__(self, date, date_type_expected):
        super(WrongDateType, self).__init__(u"Wrong date type for %s: found=%s expected=%s"
                % (unicode(date), unicode(type(date)), unicode(date_type_expected)))


class WrongDateParameter(Exception):
    def __init__(self, date, date_type_expected):
        super(WrongDateParameter, self).__init__(u"Wrong date parameter: found=%s expected=%s"
                % (unicode(date), date_type_expected))


class NoProductFound(Exception):
    def __init__(self, kwargs):
        super(NoProductFound, self).__init__(u"No Product Found: %s"
                % (",".join("%s='%s'" % (key, value) for key, value in sorted(kwargs.items()))))


class NoFrequencyFound(Exception):
    def __init__(self, product):
        super(NoFrequencyFound, self).__init__(u"No Frequency Found for Product %s: %s"
                % (unicode(product), unicode(product.frequency_id)))


class MissingMapset(Exception):
    def __init__(self, subproduct):
        super(MissingMapset, self).__init__(u"Missing mapset for subproduct %s"
                % (unicode(subproduct)))


class NoMapsetFound(Exception):
    def __init__(self, mapset_code):
        super(NoMapsetFound, self).__init__(u"No Mapset Found for mapset code %s"
                % (unicode(mapset_code)))
