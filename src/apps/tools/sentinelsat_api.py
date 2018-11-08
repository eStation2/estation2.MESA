from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
from lib.python import es_logging as log
import json
logger = log.my_logger(__name__)
import re
# connect to the API
api = SentinelAPI('vijaycharan.v', 'creationvv1!', 'https://scihub.copernicus.eu/dhus')
geojson_roi = '/srv/www/eStation2/apps/tools/ex_geojson.geojson'
datetime_start = '20180119'
datetime_end = date(2018, 01, 20)
platformname = 'Sentinel-1'
# download single scene by known product id
#api.download(<product_id>)

# download all results from the search
#api.download_all(products)

# GeoJSON FeatureCollection containing footprints and metadata of the scenes
#api.to_geojson(products)

# GeoPandas GeoDataFrame with the metadata of the scenes and the footprints as geometries
# api.to_geodataframe(products)
#
# # Get basic information about the product: its title, file size, MD5 sum, date, footprint and
# # its download url
# api.get_product_odata(<product_id>)
#
# # Get the product's full metadata available on the server
# api.get_product_odata(<product_id>, full=True)
def sentinelsat_getlists(base_url, template, datetime_start, datetime_end):
    try:
        if datetime_start is None:
            datetime_start = date
            datetime_start = '20151219'

        if datetime_end is None:
            datetime_end = date
            datetime_end = date(2015, 12, 29)


        if template is not None:
            sentinelsat_obj = json.loads(template)
            platformname = sentinelsat_obj.get('platformname')#'Sentinel-1'
            producttype = sentinelsat_obj.get('producttype')

        #Search by polygon, time, and Hub query keywords
        footprint = geojson_to_wkt(read_geojson(geojson_roi))
        products = api.query(footprint,
                             date=(datetime_start.date(), datetime_end.date()),
                             producttype = producttype,
                             #cloudcoverpercentage = None,
                             platformname=platformname)

        list_links = []
        for value in products.itervalues():
            # get the link from each dictionary
            #link = value.get("link")
            link = value.get("uuid")
            #
            #line = re.sub('\\', '', link)
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


#sentinelsat_getlists(datetime_start, datetime_end, platformname)


#############################
#GET INTERNET
#############################

######################################################################################
#   build_list_matching_files_sentinel_sat
#   Purpose: return the list of file names matching a 'template' with 'date' placeholders
#            It is the entry point for the 'http_templ' source type
#   Author: Vijay Charan Venkatachalam, JRC, European Commission
#   Date: 2015/02/18
#   Inputs: template: regex including subdirs (e.g. 'Collection51/TIFF/Win1[01]/201[1-3]/MCD45monthly.A20.*burndate.tif.gz'
#           from_date: start date for the dataset (datetime.datetime object)
#           to_date: end date for the dataset (datetime.datetime object)
#           frequency: dataset 'frequency' (see DB 'frequency' table)
#
# def build_list_matching_files_sentinel_sat(base_url, template, from_date, to_date, frequency_id):
#
#     # Add a check on frequency
#     try:
#         frequency = datasets.Dataset.get_frequency(frequency_id, datasets.Frequency.DATEFORMAT.DATETIME)
#     except Exception as inst:
#         logger.debug("Error in datasets.Dataset.get_frequency: %s" %inst.args[0])
#         raise
#
#     # Manage the start_date (mandatory).
#     try:
#         # If it is a date, convert to datetime
#         if functions.is_date_yyyymmdd(str(from_date), silent=True):
#             datetime_start=datetime.datetime.strptime(str(from_date),'%Y%m%d')
#         else:
#             # If it is a negative number, subtract from current date
#             if isinstance(from_date,int) or isinstance(from_date,long):
#                 if from_date < 0:
#                     datetime_start=datetime.datetime.today() - datetime.timedelta(days=-from_date)
#             else:
#                 logger.debug("Error in Start Date: must be YYYYMMDD or -Ndays")
#                 raise Exception("Start Date not valid")
#     except:
#         raise Exception("Start Date not valid")
#
#     # Manage the end_date (mandatory).
#     try:
#         if functions.is_date_yyyymmdd(str(to_date), silent=True):
#             datetime_end=datetime.datetime.strptime(str(to_date),'%Y%m%d')
#         # If it is a negative number, subtract from current date
#         elif isinstance(to_date,int) or isinstance(to_date,long):
#             if to_date < 0:
#                 datetime_end=datetime.datetime.today() - datetime.timedelta(days=-to_date)
#         else:
#             datetime_end=datetime.datetime.today()
#     except:
#         pass
#
#     try:
#         list_filenames = frequency.get_dates(datetime_start, datetime_end)
#     except Exception as inst:
#         logger.debug("Error in sentinelsat.get_lists: %s" %inst.args[0])
#         raise
#
#
#     # try:
#     #     dates = frequency.get_dates(datetime_start, datetime_end)
#     # except Exception as inst:
#     #     logger.debug("Error in frequency.get_dates: %s" %inst.args[0])
#     #     raise
#     #
#     # try:
#     #     list_filenames = frequency.get_internet_dates(dates, template)
#     # except Exception as inst:
#     #     logger.debug("Error in frequency.get_internet_dates: %s" %inst.args[0])
#     #     raise
#
#     return list_filenames
#
#
# def sentinelsat_getlists(datetime_start, datetime_end):
#     from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
#     from datetime import date
#     # connect to the API
#     api = SentinelAPI('vijaycharan.v', 'creationvv1!', 'https://scihub.copernicus.eu/dhus')
#
#     # download single scene by known product id
#     # api.download(<product_id>)
#
#     # search by polygon, time, and Hub query keywords
#     footprint = geojson_to_wkt(read_geojson('/home/adminuser/WS-GMES-Oct-18/ex_geojson.geojson'))
#     products = api.query(footprint,
#                          date=('20151219', date(2015, 12, 29)),
#                          platformname='Sentinel-1',
#                          producttype = 'sdasd',
#                          cloudcoverpercentage = (0, 30))

