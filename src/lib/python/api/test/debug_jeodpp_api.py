from lib.python.api import jeodpp_api
import datetime

def debug_jeodpp_catalog():

    template =  {"platformname": "Sentinel-3", "producttype": "SL2WST", "max_clouds":"50", "minlon":"-33.23047637939453","minlat":"-42.923343658447266","maxlon":"65.0774154663086","maxlat":"41.53836441040039","product_type":"SL_2_WST___" }
    #   Purpose: Query JEODPP CATALOG --- https://jeodpp.jrc.ec.europa.eu/services/catalogue/dataset?       -42.923343658447266,-33.23047637939453 ,41.53836441040039,65.0774154663086
    # POLYGON ((-33.23047637939453 41.53836441040039, 65.0774154663086 41.53836441040039, 65.0774154663086 -42.923343658447266, -33.23047637939453 -42.923343658447266, -33.23047637939453 41.53836441040039, -33.23047637939453 41.53836441040039))
    #     upper_left_coord = minlon+' '+maxlat
    #     upper_right_coord = maxlon+' '+maxlat
    #     lower_right_coord = maxlon+' '+minlat
    #     lower_left_coord = minlon+' '+minlat
    #     wkt = 'POLYGON(('+upper_left_coord+','+upper_right_coord+','+lower_right_coord+','+lower_left_coord+','+upper_left_coord+'))'

    #   productType=SL_2_WST___&acquisitionStartTime=%3E=2020-03-01&acquisitionStopTime=%3C=2020-03-01&footprint=POLYGON((21.80910642591091%2040.9831398608581,22.49575193372341%2040.9831398608581,22.49575193372341%2040.494091967663174,21.80910642591091%2040.494091967663174,21.80910642591091%2040.9831398608581))
    #   POLYGON((-33.23047637939453 41.53836441040039,65.0774154663086 41.53836441040039,65.0774154663086 -42.923343658447266,-33.23047637939453 -42.923343658447266,-33.23047637939453 41.53836441040039))
    #   POLYGON ((-33.23047637939453 41.53836441040039, 65.0774154663086 41.53836441040039, 65.0774154663086 -42.923343658447266, -33.23047637939453 -42.923343658447266, -33.23047637939453 41.53836441040039, -33.23047637939453 41.53836441040039))
    base_url = 'https://jeodpp.jrc.ec.europa.eu/services/catalogue/'
    datetime_start = datetime.datetime.today() - datetime.timedelta(days=1)
    datetime_end = datetime.datetime.today() - datetime.timedelta(days=1)
    list = jeodpp_api.get_filedir_Jeodpp_catalog(datetime_start, datetime_end, template, base_url, None)

debug_jeodpp_catalog()