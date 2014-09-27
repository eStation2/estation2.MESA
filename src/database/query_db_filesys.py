####################################################################################################################
#	purpose: Define functions to access and query the postgresql db
#	author:  Jurriaan van 't Klooster
#	date:	 20.03.2014
#   descr:	 Functions to access and query the DB using SQLSoup and SQLAlchemy as Database Abstraction Layer and ORM.
####################################################################################################################

import locals
import sys
import traceback
import json
import sqlsoup
import datetime
import time
import re

from sqlalchemy import engine
from sqlalchemy.sql import func, select, or_, and_, desc, asc, expression
from sqlalchemy.orm import aliased

from lib.python import es_logging as log
from config import es_constants
from database import querydb

from apps.acquisition import get_eumetcast
from apps.productmanagement import datasets


logger = log.my_logger(__name__)

######################################################################################
#   get_ingestions(echo=False)
#   Purpose: Query the database to get the product ingestion list of all products.
#            Mainly used in the GUI Acquisition tab.
#   Author: Jurriaan van 't Klooster
#   Date: 2014/07/31
#   Input: echo             - If True echo the query result in the console for debugging purposes. Default=False
#
#   Output: Return the product ingestion list of all products ordered by productcode.
#
#    SELECT productcode, subproductcode, version, mapsetcode, defined_by,  activated
#    FROM products.product_acquisition_data_source;
#
def get_ingestions(echo=False):
    try:
        # session = db.session
        # i = aliased(db.ingestion)
        # ingestions = session.query(func.CONCAT(i.productcode, '_', i.subproductcode, '_', i.version, '_', i.mapsetcode).label('ingestionID'),
        #                            i.productcode,
        #                            i.subproductcode,
        #                            i.version,
        #                            i.mapsetcode,
        #                            i.defined_by,
        #                            i.activated).order_by(desc(i.productcode)).first()

        i = querydb.db.ingestion._table
        m = querydb.db.mapset._table
        s = select([func.CONCAT(i.c.productcode, '_', i.c.version).label('productID'),
                    i.c.productcode,
                    i.c.subproductcode,
                    i.c.version,
                    i.c.mapsetcode,
                    i.c.defined_by,
                    #func.CONCAT('tristate', ' chart widget').label('completeness'),
                    i.c.activated,
                    m.c.descriptive_name.label('mapsetname')]).select_from(i.outerjoin(m, i.c.mapsetcode == m.c.mapsetcode))

        s = s.alias('ingest')
        i = querydb.db.map(s, primary_key=[s.c.productID, i.c.subproductcode, i.c.mapsetcode])
        ingestions = i.order_by(desc(i.productcode)).all()

        completeness = {
            'completeness': {
                'firstdate': '2010-01-01',
                'lastdate': '2014-12-21',
                'totfiles': 312,
                'missingfiles': 4,
                'intervals': [{
                    'fromdate': '2010-01-01',
                    'todate': '2013-05-21',
                    'intervaltype': 'present',
                    'intervalpercentage': 20
                }, {
                    'fromdate': '2013-06-01',
                    'todate': '2013-06-21',
                    'intervaltype': 'missing',
                    'intervalpercentage': 1
                }, {
                    'fromdate': '2014-07-01',
                    'todate': '2014-07-21',
                    'intervaltype': 'present',
                    'intervalpercentage': 35
                }, {
                    'fromdate': '2014-08-01',
                    'todate': '2014-08-21',
                    'intervaltype': 'permanent-missing',
                    'intervalpercentage': 2
                }, {
                    'fromdate': '2014-09-01',
                    'todate': '2014-12-21',
                    'intervaltype': 'present',
                    'intervalpercentage': 32
                }, {
                    'fromdate': '2014-09-01',
                    'todate': '2014-12-21',
                    'intervaltype': 'missing',
                    'intervalpercentage': 1
                }, {
                    'fromdate': '2014-09-01',
                    'todate': '2014-12-21',
                    'intervaltype': 'present',
                    'intervalpercentage': 9
                }]
            }
        }

        if ingestions.__len__() > 0:
            ingest_dict_all = []
            for row in ingestions:
                kwargs = {'product_code': row.productcode, 'sub_product_code': row.subproductcode, 'version': row.version, 'mapset': row.mapsetcode}
                print kwargs
                #kwargs.update({'to_date': datetime.date(2013, 12, 31)})
                dataset = dataset.Dataset(**kwargs)
                intervals = dataset.get_dataset_normalized_info()
                print intervals

                ingest_dict = querydb.row2dict(row)
                ingest_dict.update(completeness)
                ingest_dict_all.append(ingest_dict)

            #ingestions_json = toJson(ingestions)
            ingestions_json = json.dumps(ingest_dict_all, ensure_ascii=False, sort_keys=True, indent=4, separators=(', ', ': '))

            # ingestions_json = json.dumps(ingestions,  ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
            ingestions_json = '{"success":true, "total":'+str(ingestions.__len__())+',"ingestions":'+ingestions_json+'}'
            # ingestions_json = '{"success":true, "total":1,"ingestions":'+ingestions_json+'}'

        else:
            ingestions_json = '{"success":false, "error":"No data acquisitions defined!"}'

        if echo:
            for row in ingestions:
                print row

        return ingestions_json

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and log the error telling what happened.
        logger.error("get_ingestions: Database query error!\n -> {}".format(exceptionvalue))


######################################################################################
#   get_dataacquisitions(echo=False)
#   Purpose: Query the database to get the product data acquisition list of all products.
#            Mainly used in the GUI Acquisition tab.
#   Author: Jurriaan van 't Klooster
#   Date: 2014/07/15
#   Input: echo             - If True echo the query result in the console for debugging purposes. Default=False
#
#   Output: Return the product data acquisition list of all products ordered by productcode.
#
#    SELECT productcode, subproductcode, version, data_source_id, defined_by, type, activated, store_original_data
#    FROM products.product_acquisition_data_source;
#
def get_data_acquisitions(echo=False, toJSON=True):
    try:

        pa = querydb.db.product_acquisition_data_source._table
        s = select([ func.CONCAT(pa.c.productcode, '_', pa.c.version).label('productID'),
                     pa.c.productcode,
                     pa.c.subproductcode,
                     pa.c.version,
                     pa.c.data_source_id,
                     pa.c.defined_by,
                     pa.c.type,
                     pa.c.activated,
                     pa.c.store_original_data,
                     expression.literal("05/06/2014").label('latest')], from_obj=[pa])

        s = s.alias('mypa')
        pa = querydb.db.map(s, primary_key=[s.c.productID])
        dataacquisitions = pa.order_by(desc(pa.productcode)).all()

        # session = db.session
        # pa = aliased(db.product_acquisition_data_source)
        #
        # dataacquisitions = session.query(func.CONCAT(pa.productcode, '_', pa.subproductcode, '_', pa.version).label('productID'),
        #                                  pa.productcode,
        #                                  pa.subproductcode,
        #                                  pa.version,
        #                                  pa.data_source_id,
        #                                  pa.defined_by,
        #                                  pa.type,
        #                                  pa.activated,
        #                                  pa.store_original_data,
        #                                  expression.literal("05/06/2014").label('latest')).order_by(desc(pa.productcode)).first()

        if dataacquisitions.__len__() > 0:
            #dataacquisitions_json = toJson(dataacquisitions)

            acq_dict_all = []
            for row in dataacquisitions:
                acq_dict = querydb.row2dict(row)
                # Retrieve datetime of latest acquired file and lastest datetime
                # the acquisition was active of a specific eumetcast id
                acq_dates = get_eumetcast.get_eumetcast_info(row.data_source_id)
                if acq_dates:
                    for key in acq_dates.keys():
                        #acq_info += '"%s": "%s", ' % (key, acq_dates[key])
                        if isinstance(acq_dates[key], datetime.date):
                            datetostring = acq_dates[key].strftime("%y-%m-%d %H:%M")
                            acq_dict[key] = datetostring
                        else:
                            acq_dict[key] = acq_dates[key]
                else:
                    acq_dict['time_latest_copy'] = datetime.datetime.now().strftime("%y-%m-%d %H:%M")
                    acq_dict['time_latest_exec'] = datetime.datetime.now().strftime("%y-%m-%d %H:%M")
                    acq_dict['lenght_proc_list'] = datetime.datetime.now().strftime("%y-%m-%d %H:%M")

                acq_dict_all.append(acq_dict)

            acq_json = json.dumps(acq_dict_all, ensure_ascii=False, sort_keys=True, indent=4, separators=(', ', ': '))

            logger.error("Just to log something in this log file to see if the rotatingfilehandler works!\n")

            # dataacquisitions_json = json.dumps(dataacquisitions, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
            dataacquisitions_json = '{"success":true, "total":'+str(dataacquisitions.__len__())+',"dataacquisitions":'+acq_json+'}'
            # dataacquisitions_json = '{"success":true, "total":1,"dataacquisitions":['+dataacquisitions_json+']}'

        else:
            dataacquisitions_json = '{"success":false, "error":"No data acquisitions defined!"}'

        if echo:
            for row in dataacquisitions:
                print row

        if toJSON:
            return dataacquisitions_json
        else:
            return dataacquisitions

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and log the error telling what happened.
        logger.error("get_dataacquisitions: Database query error!\n -> {}".format(exceptionvalue))

