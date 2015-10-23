# -*- coding: utf-8 -*-
#
#    purpose: Mapset functions
#    author:  Marco Beri marcoberi@gmail.com
#    date:    17.12.2014
#

from __future__ import absolute_import

from lib.python import es_logging as log
from database import querydb


from .exceptions import NoMapsetFound


logger = log.my_logger(__name__)


class Mapset(object):
    def __init__(self, mapset_code):
        self.mapset_code = mapset_code
        kwargs = {'mapsetcode': self.mapset_code}
        self._mapset = querydb.get_mapset(**kwargs)
        if not self._mapset:
            raise NoMapsetFound(kwargs)

    def to_dict(self):
        return dict((fieldname, getattr(self._mapset, fieldname))
            for fieldname in ('mapsetcode', 'defined_by', 'description', 'srs_wkt',
                'upper_left_long', 'pixel_shift_long', 'rotation_factor_long',
                'upper_left_lat', 'pixel_shift_lat', 'rotation_factor_lat',
                'pixel_size_x', 'pixel_size_y'))
