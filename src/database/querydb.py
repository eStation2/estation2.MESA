####################################################################################################################
#	purpose: Define functions to access and query the postgresql db
#	author:  Jurriaan van 't Klooster
#	date:	 20.03.2014
#   descr:	 Functions to access and query the DB using SQLSoup and SQLAlchemy as Database Abstraction Layer and ORM.
####################################################################################################################

#import locals
import sys
import traceback
import json
import sqlsoup
import datetime
import time
import re
#import JsonSerializer
#import anyjson

#from sqlalchemy import engine
from sqlalchemy.sql import func, select, or_, and_, desc, asc, expression
from sqlalchemy.orm import aliased

from lib.python import es_logging as log
#from config import es_constants
#from crud import CrudDB

from database import connectdb

#from apps.acquisition.get_eumetcast import *

#from apps.productmanagement.datasets import Dataset


logger = log.my_logger(__name__)


######################################################################################
#   connect_db()
#   Purpose: Create a connection to the database
#   Author: Jurriaan van 't Klooster
#   Date: 2014/05/16
#   Input: None
#   Output: Return connection handler to the database
#def connect_db_sqlsoup():
#
#    try:
#        sqlsoup_dns = connectdb.ConnectDB.get_db_url()
#
#        dbconn = sqlsoup.SQLSoup(sqlsoup_dns)
#        dbconn.schema = es_constants.dbglobals['schema_products']
#        return dbconn
#    except:
#        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
#        #print traceback.format_exc()
#        # Exit the script and print an error telling what happened.
#        logger.error("Database connection failed!\n -> {}".format(exceptionvalue))
#        #raise Exception("Database connection failed!\n ->%s" % exceptionvalue)


#def connect_db():
#
#    try:
#        schema = es_constants.dbglobals['schema_products']
#
#        db_url = "postgresql://%s:%s@%s/%s" % (es_constants.dbglobals['dbUser'],
#                                               es_constants.dbglobals['dbPass'],
#                                               es_constants.dbglobals['host'],
#                                               es_constants.dbglobals['dbName'])
#        dbconn = engine.create_engine(db_url)
#        dbconn.schema = schema
#        return dbconn
#    except:
#        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
#        #print traceback.format_exc()
#        # Exit the script and print an error telling what happened.
#        logger.error("Database connection failed!\n -> {}".format(exceptionvalue))
#        #raise Exception("Database connection failed!\n ->%s" % exceptionvalue)

db = connectdb.ConnectDB().db
#db = dbconn.db

def row2dict(row):
    d = {}
    for column in row.c._all_cols:
        d[column.name] = str(getattr(row, column.name))

    return d


def toJson(queryResult):
    tojson = ''
    for row in queryResult:
        da = row2dict(row)
        tojson = tojson + json.dumps(da, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': ')) + ', '
    tojson = tojson[:-2]
    return tojson

# Return True if the date is in the correct format
def checkDateFormat(myString):
    isDate = re.match('[0-1][0-9]\/[0-3][0-9]\/[1-2][0-9]{3}', myString)
    return isDate


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

        i = db.ingestion._table
        m = db.mapset._table
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
        i = db.map(s, primary_key=[s.c.productID, i.c.subproductcode, i.c.mapsetcode])
        ingestions = i.order_by(desc(i.productcode)).all()

        #completeness = {
        #    'completeness': {
        #        'firstdate': '2010-01-01',
        #        'lastdate': '2014-12-21',
        #        'totfiles': 312,
        #        'missingfiles': 4,
        #        'intervals': [{
        #            'fromdate': '2010-01-01',
        #            'todate': '2013-05-21',
        #            'intervaltype': 'present',
        #            'intervalpercentage': 20
        #        }, {
        #            'fromdate': '2013-06-01',
        #            'todate': '2013-06-21',
        #            'intervaltype': 'missing',
        #            'intervalpercentage': 1
        #        }, {
        #            'fromdate': '2014-07-01',
        #            'todate': '2014-07-21',
        #            'intervaltype': 'present',
        #            'intervalpercentage': 35
        #        }, {
        #            'fromdate': '2014-08-01',
        #            'todate': '2014-08-21',
        #            'intervaltype': 'permanent-missing',
        #            'intervalpercentage': 2
        #        }, {
        #            'fromdate': '2014-09-01',
        #            'todate': '2014-12-21',
        #            'intervaltype': 'present',
        #            'intervalpercentage': 32
        #        }, {
        #            'fromdate': '2014-09-01',
        #            'todate': '2014-12-21',
        #            'intervaltype': 'missing',
        #            'intervalpercentage': 1
        #        }, {
        #            'fromdate': '2014-09-01',
        #            'todate': '2014-12-21',
        #            'intervaltype': 'present',
        #            'intervalpercentage': 9
        #        }]
        #    }
        #}
        #
        #if ingestions.__len__() > 0:
        #    ingest_dict_all = []
        #    for row in ingestions:
        #        kwargs = {'product_code': row.productcode, 'sub_product_code': row.subproductcode, 'version': row.version, 'mapset': row.mapsetcode}
        #        print kwargs
        #        #kwargs.update({'to_date': datetime.date(2013, 12, 31)})
        #        dataset = Dataset(**kwargs)
        #        intervals = dataset.get_dataset_normalized_info()
        #        print intervals
        #
        #        ingest_dict = row2dict(row)
        #        ingest_dict.update(completeness)
        #        ingest_dict_all.append(ingest_dict)
        #
        #    #ingestions_json = toJson(ingestions)
        #    ingestions_json = json.dumps(ingest_dict_all, ensure_ascii=False, sort_keys=True, indent=4, separators=(', ', ': '))
        #
        #    # ingestions_json = json.dumps(ingestions,  ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
        #    ingestions_json = '{"success":true, "total":'+str(ingestions.__len__())+',"ingestions":'+ingestions_json+'}'
        #    # ingestions_json = '{"success":true, "total":1,"ingestions":'+ingestions_json+'}'
        #
        #else:
        #    ingestions_json = '{"success":false, "error":"No data acquisitions defined!"}'

        if echo:
            for row in ingestions:
                print row

        return ingestions

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
def get_dataacquisitions(echo=False, tojson=True):
    try:
        pa = db.product_acquisition_data_source._table
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
        pa = db.map(s, primary_key=[s.c.productID])
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

        #if dataacquisitions.__len__() > 0:
        #    #dataacquisitions_json = toJson(dataacquisitions)
        #
        #    acq_dict_all = []
        #    for row in dataacquisitions:
        #        acq_dict = row2dict(row)
        #        # Retrieve datetime of latest acquired file and lastest datetime
        #        # the acquisition was active of a specific eumetcast id
        #        acq_dates = get_eumetcast_info(row.data_source_id)
        #        if acq_dates:
        #            for key in acq_dates.keys():
        #                #acq_info += '"%s": "%s", ' % (key, acq_dates[key])
        #                if isinstance(acq_dates[key], datetime.date):
        #                    datetostring = acq_dates[key].strftime("%y-%m-%d %H:%M")
        #                    acq_dict[key] = datetostring
        #                else:
        #                    acq_dict[key] = acq_dates[key]
        #        else:
        #            acq_dict['time_latest_copy'] = datetime.datetime.now().strftime("%y-%m-%d %H:%M")
        #            acq_dict['time_latest_exec'] = datetime.datetime.now().strftime("%y-%m-%d %H:%M")
        #            acq_dict['lenght_proc_list'] = datetime.datetime.now().strftime("%y-%m-%d %H:%M")
        #
        #        acq_dict_all.append(acq_dict)
        #
        #        acq_json = json.dumps(acq_dict_all, ensure_ascii=False, sort_keys=True, indent=4, separators=(', ', ': '))
        #
        #        logger.error("Just to log something in this log file to see if the rotatingfilehandler works!\n")
        #
        #        # dataacquisitions_json = json.dumps(dataacquisitions, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
        #        dataacquisitions_json = '{"success":true, "total":'+str(dataacquisitions.__len__())+',"dataacquisitions":'+acq_json+'}'
        #        # dataacquisitions_json = '{"success":true, "total":1,"dataacquisitions":['+dataacquisitions_json+']}'
        #
        #else:
        #    dataacquisitions_json = '{"success":false, "error":"No data acquisitions defined!"}'

        if echo:
            for row in dataacquisitions:
                print row

        if tojson:
            return dataacquisitions
        else:
            return dataacquisitions

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and log the error telling what happened.
        logger.error("get_dataacquisitions: Database query error!\n -> {}".format(exceptionvalue))


######################################################################################
#   get_products(echo=False)
#   Purpose: Query the database to get the (Native) product list with their product category.
#            Mainly used in the GUI Acquisition tab.
#   Author: Jurriaan van 't Klooster
#   Date: 2014/07/08
#   Input: echo             - If True echo the query result in the console for debugging purposes. Default=False
#
#   Output: Return the (Native) product list with their product category
#           ordered by product category order_index and productcode.

#   SELECT p.productcode, p.version, p.activated, pc.category_id, pc.descriptive_name, pc.order_index
#   FROM products.product p inner join products.product_category pc on p.category_id = pc.category_id
#   WHERE p.product_type = 'Native'
#   ORDER BY pc.order_index, productcode
#
def get_products(echo=False, activated=True):
#def get_products(echo=False):
    try:
        session = db.session

        #pc = session.query(db.product_category.category_id,
        #                   db.product_category.descriptive_name,
        #                   db.product_category.order_index).subquery()
        #pc = aliased(db.product_category)
        #p = aliased(db.product)

        #if activated in ['True', 'true', '1', 't', 'y', 'Y', 'yes', 'Yes']:
        #    where = and_(p.product_type == 'Native', p.activated)
        #else:
        #    where = and_(p.product_type == 'Native', p.activated != 't')

        # The columns on the subquery "pc" are accessible through an attribute called "c"
        # e.g. product.c.descriptive_name
        #productslist = session.query(func.CONCAT(p.productcode, '_', p.version).label('productID'),
        #                             p.productcode,
        #                             p.subproductcode,
        #                             p.version,
        #                             p.activated,
        #                             p.descriptive_name.label('prod_descriptive_name'),
        #                             p.description,
        #                             pc.category_id,
        #                             pc.descriptive_name.label('cat_descr_name'),
        #                             pc.order_index).\
        #    outerjoin(pc, p.category_id == pc.category_id).\
        #    filter(where).\
        #    order_by(asc(pc.order_index), asc(p.productcode)).all()

        pc = db.product_category._table
        p = db.product._table

        s = select([func.CONCAT(p.c.productcode, '_', p.c.version).label('productID'),
                    p.c.productcode,
                    p.c.subproductcode,
                    p.c.version,
                    p.c.activated,
                    p.c.product_type,
                    p.c.descriptive_name.label('prod_descriptive_name'),
                    p.c.description,
                    pc.c.category_id,
                    pc.c.descriptive_name.label('cat_descr_name'),
                    pc.c.order_index]).select_from(p.outerjoin(pc, p.c.category_id == pc.c.category_id))

        s = s.alias('pl')
        pl = db.map(s, primary_key=[s.c.productID])

        #where = and_(pl.c.product_type == 'Native')

        if activated or activated in ['True', 'true', '1', 't', 'y', 'Y', 'yes', 'Yes']:
            where = and_(pl.c.product_type == 'Native', pl.c.activated)
        else:
            where = and_(pl.c.product_type == 'Native', pl.c.activated != 't')

        productslist = pl.filter(where).order_by(asc(pl.c.order_index), asc(pl.c.productcode)).all()
        #productslist.filter(where).order_by(asc(productslist.c.order_index), asc(productslist.c.productcode)).all()
        productslist_json = toJson(productslist)

        #productslist_json = json.dumps(productslist, sort_keys=True, indent=4, separators=(',', ': '))
        productslist_json = '{"success":true, "total":'+str(productslist.__len__())+',"products":['+productslist_json+']}'

        #echo '{"success":false,"error":"' . 'No records found!' . '"}';
        if echo:
            for row in productslist:
                print row

        return productslist_json

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and log the error telling what happened.
        logger.error("get_products: Database query error!\n -> {}".format(exceptionvalue))


######################################################################################
#   get_product_out_info(allrecs=False, echo=False, productcode='', subproductcode='', version='undefined')
#   Purpose: Query the database to get the records of all or a specific product from the table product
#   Author: Jurriaan van 't Klooster
#   Date: 2014/05/16
#   Input: allrecs          - If True return all products. Default=False
#          echo             - If True echo the query result in the console for debugging purposes. Default=False
#          productcode      - The productcode of the specific product info requested.
#                             If given also subproductcode and version have to be given. Default=''
#          subproductcode   - The subproductcode of the specific product info requested. Default=''
#          version          - The version of the specific product info requested. Default='undefined'
#   Output: Return the fields of all or a specific product record from the table product.
def get_product_out_info(allrecs=False, echo=False, productcode='', subproductcode='', version='undefined'):
    try:
        if allrecs:
            product_out_info = db.product.order_by(asc(db.product.productcode)).all()
            if echo:
                for row in product_out_info:
                    print row
        else:
            where = and_(db.product.productcode == productcode,
                         db.product.subproductcode == subproductcode,
                         db.product.version == version)
            product_out_info = db.product.filter(where).all()
            if echo:
                print product_out_info
        return product_out_info
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_product_out_info: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_product_out_info: Database query error!\n ->%s" % exceptionvalue)


######################################################################################
#   get_product_in_info(allrecs=False, echo=False, productcode='', subproductcode='',
#                       version='undefined', datasource_descr_id='')
#   Purpose: Query the database to get the fields scale_factor, scale_offset, no_data, mask_min,
#            mask_max and data_type_id of all or a specific product datasource from the table sub_datasource_description
#   Author: Jurriaan van 't Klooster
#   Date: 2014/05/16
#   Input: allrecs              - If True return all products. Default=False
#          echo                 - If True echo the query result in the console for debugging purposes. Default=False
#          productcode          - The productcode of the specific product datasource info requested.
#                                 If given also subproductcode, version and datasource_descr_id have to be given.
#                                 Default=''
#          subproductcode       - The subproductcode of the specific product info requested. Default=''
#          version              - The version of the specific product info requested. Default='undefined'
#          datasource_descr_id  - The version of the specific product info requested. Default='undefined'
#   Output: Return the fields of all [or a specific product record} from the sub_datasource_description table.
def get_product_in_info(allrecs=False, echo=False,
                        productcode='', subproductcode='',
                        version='undefined', datasource_descr_id=''):
    try:
        if allrecs:
            product_in_info = db.sub_datasource_description.order_by(asc(db.sub_datasource_description.productcode)).all()
            if echo:
                for row in product_in_info:
                    print row
        else:
            where = and_(db.sub_datasource_description.productcode == productcode,
                         db.sub_datasource_description.subproductcode == subproductcode,
                         db.sub_datasource_description.version == version,
                         db.sub_datasource_description.datasource_descr_id == datasource_descr_id)
            product_in_info = db.sub_datasource_description.filter(where).one()
            if echo:
                print product_in_info
        return product_in_info
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_product_out_info: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_product_in_info: Database query error!\n ->%s" % exceptionvalue)


######################################################################################
#   get_product_native(pkid='', allrecs=False, echo=False)
#   Purpose: Query the database to get the records of all products or one specific product
#            with product_type='Native' from the table product.
#   Author: Jurriaan van 't Klooster
#   Date: 2014/05/16
#   Input: productcode      - The productcode of the specific product info requested. Default=''
#          allrecs          - If True return all products. Default=False
#          echo             - If True echo the query result in the console for debugging purposes. Default=False
#   Output: Return the fields of all or a specific product record with product_type='Native' from the table product.
def get_product_native(productcode='', allrecs=False, echo=False):
    try:
        if allrecs:
            where = db.product.product_type == 'Native'
            product = db.product.filter(where).order_by(asc(db.product.productcode)).all()
            if echo:
                for row in product:
                    print row
        else:
            where = and_(db.product.productcode == productcode, db.product.product_type == 'Native')
            product = db.product.filter(where).one()
            if echo:
                print product
        return product
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_product_native: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_product_native: Database query error!\n ->%s" % exceptionvalue)


######################################################################################
#   get_eumetcast(source_id='', allrecs=False, echo=False)
#   Purpose: Query the database to get the records of all eumetcast sources or one specific eumetcast source
#            from the table eumetcast_source.
#   Author: Jurriaan van 't Klooster
#   Date: 2014/05/16
#   Input: source_id        - The eumetcast_id of the specific eumetcast source requested. Default=''
#          allrecs          - If True return all products. Default=False
#          echo             - If True echo the query result in the console for debugging purposes. Default=False
#   Output: Return the fields of all or a specific eumetcast source record from the table eumetcast_source.
def get_eumetcast(source_id='', allrecs=False, echo=False):
    try:
        if allrecs:
            eumetcasts = db.eumetcast_source.order_by(asc(db.eumetcast_source.eumetcast_id)).all()
            #eumetcasts.sort()
            if echo:
                for row in eumetcasts:
                    print row
        else:
            where = db.eumetcast_source.eumetcast_id == source_id
            eumetcasts = db.eumetcast_source.filter(where).one()
            if echo:
                print eumetcasts
        return eumetcasts
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        raise logger.error("get_eumetcast: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_eumetcast: Database query error!\n ->%s" % exceptionvalue)
    #finally:
        #if session:
        #    session.close()


######################################################################################
#   get_internet(internet_id='', allrecs=False, echo=False)
#   Purpose: Query the database to get the records of all internet sources or one specific internet source
#            from the table internet_source.
#   Author: Jurriaan van 't Klooster
#   Date: 2014/05/16
#   Input: internet_id      - The internet_id of the specific internet source requested. Default=''
#          allrecs          - If True return all products. Default=False
#          echo             - If True echo the query result in the console for debugging purposes. Default=False
#   Output: Return the fields of all or a specific internet source record from the table internet_source.
def get_internet(internet_id='', allrecs=False, echo=False):
    try:
        if allrecs:
            internet = db.internet_source.order_by(asc(db.internet_source.internet_id)).all()
            if echo:
                for row in internet:
                    print row
        else:
            where = db.internet_source.internet_id == internet_id
            internet = db.internet_source.filter(where).one()
            if echo:
                print internet
        return internet
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_internet: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_internet: Database query error!\n ->%s" % exceptionvalue)


######################################################################################
#   get_mapset(mapsetcode='', allrecs=False, echo=False)
#   Purpose: Query the database to get the records of all mapsets or one specific mapset
#            from the table mapset.
#   Author: Jurriaan van 't Klooster
#   Date: 2014/05/16
#   Input: mapsetcode       - The mapsetcode of the specific mapset requested. Default=''
#          allrecs          - If True return all products. Default=False
#          echo             - If True echo the query result in the console for debugging purposes. Default=False
#   Output: Return the fields of all or a specific mapset record from the table mapset.
def get_mapset(mapsetcode='', allrecs=False, echo=False):
    try:
        mapset = []
        if allrecs:
            if db.mapset.order_by(asc(db.mapset.mapsetcode)).count() >= 1:
                mapset = db.mapset.order_by(asc(db.mapset.mapsetcode)).all()
                if echo:
                    for row in mapset:
                        print row
        else:
            where = db.mapset.mapsetcode == mapsetcode
            if db.mapset.filter(where).count() == 1:
                mapset = db.mapset.filter(where).one()
                if echo:
                    print mapset
        return mapset
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        raise logger.error("get_mapset: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_mapset: Database query error!\n ->%s" % exceptionvalue)


######################################################################################
#   get_ingestion_product(allrecs=False, echo=False, productcode_in='', version_in='')
#   Purpose: Query the database to get the COUNT of all product ingestion definitions or one specific
#            product ingestion definition at product level from the table ingestion.
#   Author: Jurriaan van 't Klooster
#   Date: 2014/05/16
#   Input: allrecs          - If True return all products. Default=False
#          echo             - If True echo the query result in the console for debugging purposes. Default=False
#          productcode      - The productcode of the specific product ingestion definition requested. Default=''
#          version          - The version of the specific product ingestion definition requested. Default='undefined'
#   Output: Return the productcode, version and count() of subproducts of all [or a specific product ingestion definition] from the table
#           ingestion.
def get_ingestion_product(allrecs=False, echo=False, productcode='', version='undefined'):
    try:
        session = db.session
        ingest = aliased(db.ingestion)

        # Get all defined ingestion definitions with the amount of subproducts per product/version (count).
        ingestion_product = session.query(ingest.productcode,
                                          ingest.version,
                                          func.count(ingest.subproductcode), ). \
            group_by(ingest.productcode, ingest.version)

        active_ingestions = []
        if allrecs:
            ingestion_product = ingestion_product.filter(ingest.activated == True)

            if ingestion_product.count() >= 1:      # At least 1 product ingestion definition has to exist.
                active_ingestions = ingestion_product.all()
                if echo:
                    for row in active_ingestions:
                        print row
        else:
            where = and_(ingest.productcode == productcode,
                         ingest.activated == True,
                         ingest.version == version)
            if ingestion_product.filter(where).count() == 1:    # Exactly 1 product ingestion definition has to exist.
                active_ingestions = ingestion_product.filter(where).one()
                if echo:
                    print active_ingestions
        return active_ingestions
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_ingestion_product: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_ingestion_product: Database query error!\n ->%s" % exceptionvalue)


######################################################################################
#   get_ingestion_subproduct(allrecs=False, echo=False, productcode='', version='')
#   Purpose: Query the database to get the records of all product ingestion definitions or one specific
#            product ingestion definition  at subproduct level (not product level) from the table ingestion.
#   Author: Jurriaan van 't Klooster
#   Date: 2014/05/16
#   Input: allrecs          - If True return all products. Default=False
#          echo             - If True echo the query result in the console for debugging purposes. Default=False
#          productcode      - The productcode of the specific product ingestion definition requested. Default=''
#          version          - The version of the specific product ingestion definition requested. Default='undefined'
#   Output: Return all relevant fields of all [or a specific ingestion definition record] from the table ingestion.
def get_ingestion_subproduct(allrecs=False, echo=False, productcode='', version=''):
    try:
        ingestion = []
        if allrecs:
            if db.ingestion.filter(db.ingestion.activated == True).count() >= 1:
                ingestion = db.ingestion.filter(db.ingestion.activated == True).\
                    order_by(asc(db.ingestion.productcode)).all()
                if echo:
                    for row in ingestion:
                        print row
        else:
            where = and_(db.ingestion.productcode == productcode,
                         db.ingestion.activated,
                         #db.ingestion.subproductcode == subproductcode,
                         db.ingestion.version == version)
            if db.ingestion.filter(where).count() >= 1:
                ingestion = db.ingestion.filter(where).all()
                if echo:
                    print ingestion
        return ingestion
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_ingestion_subproduct: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_ingestion_subproduct: Database query error!\n ->%s" % exceptionvalue)


######################################################################################
#   get_product_sources(echo=False, productcode='', subproductcode='', version='')
#   Purpose: Query the database to get all the activated data sources defined for a specific product (INTERNET
#            and EUMETCAST), from the table product_acquisition_data_source
#   Author: Jurriaan van 't Klooster
#   Date: 2014/05/16
#   Input: echo                 - If True echo the query result in the console for debugging purposes. Default=False
#          productcode          - The productcode of the specific product datasource info requested.
#                                 If given also subproductcode, version have to be given. Default=''
#          subproductcode       - The subproductcode of the specific product info requested. Default=''
#          version              - The version of the specific product info requested. Default='undefined'
#
#   Output: Return all the activated data sources defined for a specific product
#           from the table product_acquisition_data_source.
def get_product_sources(echo=False, productcode='', subproductcode='', version=''):
    try:
        sources = []
        where = and_(db.product_acquisition_data_source.productcode == productcode,
                     db.product_acquisition_data_source.subproductcode == subproductcode,
                     db.product_acquisition_data_source.version == version)

        if db.product_acquisition_data_source.filter(where).count() >= 1:
            sources = db.product_acquisition_data_source.filter(where). \
                order_by(asc(db.product_acquisition_data_source.type)).all()
            if echo:
                for row in sources:
                    print row
        return sources
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_product_sources: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_product_sources: Database query error!\n ->%s" % exceptionvalue)


######################################################################################
#   get_datasource_descr(echo=False, source_type='', source_id='')
#   Purpose: Query the database to get the datasource description and filter expression of a specific datasource
#            (INTERNET or EUMETCAST).
#   Author: Jurriaan van 't Klooster
#   Date: 2014/05/16
#   Input: echo             - If True echo the query result in the console for debugging purposes. Default=False
#          source_type      - The data source type. Values: INTERNET or EUMETCAST   Default=''
#          source_id        - The eumetcast_id or internet_id of the specific data source description requested.
#                             Default=''
#
#   Output: Return the datasource description and filter expression of the requested data source.
def get_datasource_descr(echo=False, source_type='', source_id=''):
    try:
        session = db.session
        if source_type == 'EUMETCAST':
            #q = "select e.filter_expression_jrc, dd.* \
            #     from products.datasource_description dd \
            #     inner join products.eumetcast_source e \
            #     on e.datasource_descr_id = dd.datasource_descr_id \
            #     where e.eumetcast_id = '%s' " % source_id
            es = aliased(db.eumetcast_source)
            dsd = aliased(db.datasource_description)
            datasource_descr = session.query(es.filter_expression_jrc, dsd).join(dsd). \
                filter(es.eumetcast_id == source_id).all()

        else:   # source_type == 'INTERNET'
            datasource_descr = session.query(db.internet_source, db.datasource_description). \
                join(db.datasource_description). \
                filter(db.internet_source.internet_id == source_id).all()

        if echo:
            for row in datasource_descr:
                print row
        return datasource_descr
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_datasource_descr: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_ingestion: Database query error!\n ->%s" % exceptionvalue)


######################################################################################
#   get_eumetcast_sources(echo=False)
#   Purpose: Query the database to get the filter_expression of all the active product EUMETCAST data sources.
#            Mainly used in get_eumetcast.py
#   Author: Jurriaan van 't Klooster
#   Date: 2014/05/16
#   Input: echo             - If True echo the query result in the console for debugging purposes. Default=False
#
#   Output: Return the filter_expression of all the active product EUMETCAST data sources.
def get_eumetcast_sources(echo=False):
    try:
        session = db.session

        es = session.query(db.eumetcast_source.eumetcast_id, db.eumetcast_source.filter_expression_jrc).subquery()
        pads = aliased(db.product_acquisition_data_source)

        # The columns on the subquery "es" are accessible through an attribute called "c"
        # e.g. es.c.filter_expression_jrc
        eumetcast_sources = session.query(pads, es.c.eumetcast_id, es.c.filter_expression_jrc).\
            outerjoin(es, pads.data_source_id == es.c.eumetcast_id).\
            filter(and_(pads.type == 'EUMETCAST', pads.activated == True)).all()

        if echo:
            for row in eumetcast_sources:
                print row

        return eumetcast_sources

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_eumetcast_sources: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_ingestion: Database query error!\n ->%s" % exceptionvalue)

######################################################################################
#   get_active_internet_sources(echo=False)
#   Purpose: Query the database to get the internet_id of all the active product INTERNET data sources.
#            Mainly used in get_internet.py
#   Author: Marco Clerici
#   Date: 2014/09/03
#   Input: echo             - If True echo the query result in the console for debugging purposes. Default=False
#
#   Output: Return the internet of all the active product INTERNET data sources.
def get_active_internet_sources(echo=False):
    try:
        session = db.session

        es = session.query(db.internet_source).subquery()
        pads = aliased(db.product_acquisition_data_source)

        # The columns on the subquery "es" are accessible through an attribute called "c"
        # e.g. es.c.filter_expression_jrc

        args = tuple(x for x in (pads, es.c.internet_id, es.c.defined_by ,
                                 es.c.descriptive_name, es.c.description,
                                 es.c.modified_by, es.c.update_datetime,
                                 es.c.url, es.c.user_name, es.c.password,
                                 es.c.list, es.c.period, es.c.scope ,
                                 es.c.include_files_expression ,
                                 es.c.exclude_files_expression,
                                 es.c.status, es.c.pull_frequency ,
                                 es.c.datasource_descr_id)
                    if x != es.c.update_datetime or not CrudDB.is_testing())
        internet_sources = session.query(*args).outerjoin(es,
                pads.data_source_id == es.c.internet_id).filter(
                and_(pads.type == 'INTERNET', pads.activated == 1.0)).all()

        if echo:
            for row in internet_sources:
                print row

        return internet_sources

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_internet_sources: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_ingestion: Database query error!\n ->%s" % exceptionvalue)


