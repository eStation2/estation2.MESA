from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
from lib.python import es_logging as log
import json
logger = log.my_logger(__name__)
import re
# connect to the API
api = SentinelAPI('estationjrc', 'estation19', 'https://scihub.copernicus.eu/dhus')
geojson_roi = '/srv/www/eStation2/apps/tools/ex_geojson.geojson'


def sentinelsat_getlists(base_url, template, datetime_start, datetime_end):
    try:
        if datetime_start is None:
            datetime_start = date
            datetime_start = '20151219'

        if datetime_end is None:
            datetime_end = date
            datetime_end = date(2015, 12, 29)

        str_temp = ''
        if template is not None:
            sentinelsat_obj = json.loads(template)
            platformname = sentinelsat_obj.get('platformname')#'Sentinel-1'
            producttype = sentinelsat_obj.get('producttype')
            polarisationmode = sentinelsat_obj.get('polarisationmode')
            sensoroperationalmode = sentinelsat_obj.get('sensoroperationalmode')

        #Search by polygon, time, and Hub query keywords
        footprint = geojson_to_wkt(read_geojson(geojson_roi))

        if platformname != None and producttype != None and polarisationmode != None and sensoroperationalmode != None:

            products = api.query(footprint, date=(datetime_start.date(), datetime_end.date()), platformname = platformname, producttype =producttype, polarisationmode=polarisationmode,sensoroperationalmode =sensoroperationalmode )

        else:
            products = api.query(footprint,
                                 date=(datetime_start.date(), datetime_end.date()),
                                 producttype = producttype,
                                 #cloudcoverpercentage = None,
                                 platformname=platformname)

        list_links = []
        for value in products.values():
            link = value.get("uuid")
            list_links.append(link)

        list_links

    except:
        logger.error("Error in upsert_database")

    return list_links

def download_sentinelsat_getlists(uuid, target_dir):

    try:
        api.download(uuid, target_dir)
        return 0
    except:
        return 1
