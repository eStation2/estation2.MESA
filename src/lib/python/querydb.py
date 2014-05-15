####################################################################################################################
#	purpose: Define functions to access and query the postgresql db
#	author:  Jurriaan van 't Klooster
#	date:	 20.03.2014
#   descr:	 Functions to access and query the DB using SQLSoup and SQLAlchemy as Database Abstraction Layer and ORM.
####################################################################################################################

__author__ = "Jurriaan van 't Klooster"
from config.es2 import *
import sys
import traceback
import sqlsoup
#from sqlsoup import Session
from sqlalchemy.sql import or_, and_, desc, asc
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
#from lib.python.es_constants import *

logger = log.my_logger(__name__)

# TODO: Working with SQLAlchemy Sessions?


def connect_db():

    try:
        sqlsoup_dns = "postgresql://%s:%s@%s/%s" % (dbglobals['dbUser'],
                                                    dbglobals['dbPass'],
                                                    dbglobals['host'],
                                                    dbglobals['dbName'])

        dbconn = sqlsoup.SQLSoup(sqlsoup_dns)
        dbconn.schema = dbglobals['schema_products']
        return dbconn
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        #print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        raise logger.error("Database connection failed!\n -> {}".format(exceptionvalue))
        #raise Exception("Database connection failed!\n ->%s" % exceptionvalue)

db = connect_db()


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
            product_out_info = db.product.filter(where).one()
            if echo:
                print product_out_info
        return product_out_info
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        raise logger.error("get_product_out_info: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_product_out_info: Database query error!\n ->%s" % exceptionvalue)


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
        raise logger.error("get_product_out_info: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_product_in_info: Database query error!\n ->%s" % exceptionvalue)


def get_product_native(pkid='', allrecs=False, echo=False):
    try:
        if allrecs:
            where = db.product.product_type == 'Native'
            product = db.product.filter(where).order_by(asc(db.product.productcode)).all()
            if echo:
                for row in product:
                    print row
        else:
            where = and_(db.product.productcode == pkid, db.product.product_type == 'Native')
            product = db.product.filter(where).one()
            if echo:
                print product
        return product
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        raise logger.error("get_product_native: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_product_native: Database query error!\n ->%s" % exceptionvalue)


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


def get_internet(pkid='', allrecs=False, echo=False):
    try:
        if allrecs:
            internet = db.internet_source.order_by(asc(db.internet_source.internet_id)).all()
            if echo:
                for row in internet:
                    print row
        else:
            where = db.internet_source.internet_id == pkid
            internet = db.internet_source.filter(where).one()
            if echo:
                print internet
        return internet
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        raise logger.error("get_internet: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_internet: Database query error!\n ->%s" % exceptionvalue)


def get_mapset(pkid='', allrecs=False, echo=False):
    try:
        mapset = []
        if allrecs:
            if db.mapset.order_by(asc(db.mapset.mapsetcode)).count() >= 1:
                mapset = db.mapset.order_by(asc(db.mapset.mapsetcode)).all()
                if echo:
                    for row in mapset:
                        print row
        else:
            where = db.mapset.mapsetcode == pkid
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


def get_ingestion_product(allrecs=False, echo=False, productcode='', version=''):
    try:
        session = db.session
        ingest = aliased(db.ingestion)

        ingestion_product = session.query(ingest.productcode,
                                          ingest.version,
                                          func.count(ingest.subproductcode), ). \
            group_by(ingest.productcode, ingest.version)
        active_ingestions = []
        if allrecs:
            where = ingest.activated
            ingestion_product = ingestion_product.filter(where)

            if ingestion_product.count() >= 1:
                active_ingestions = ingestion_product.all()
                if echo:
                    for row in active_ingestions:
                        print row
        else:
            where = and_(ingest.productcode == productcode,
                         ingest.activated,
                         ingest.version == version)
            if ingestion_product.filter(where).count() == 1:
                active_ingestions = ingestion_product.filter(where).one()
                if echo:
                    print active_ingestions
        return active_ingestions
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        raise logger.error("get_ingestion_product: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_ingestion_product: Database query error!\n ->%s" % exceptionvalue)


def get_ingestion_subproduct(allrecs=False, echo=False, productcode='', subproductcode='', version=''):
    try:
        ingestion = []
        if allrecs:
            where = db.ingestion.activated
            if db.ingestion.filter(where).count() >= 1:
                ingestion = db.ingestion.filter(where).order_by(asc(db.ingestion.productcode)).all()
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
        raise logger.error("get_ingestion_subproduct: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_ingestion_subproduct: Database query error!\n ->%s" % exceptionvalue)


def get_product_sources(echo=False, productcode='', subproductcode='', version=''):
    try:
        sources = []
        where = and_(db.product_acquisition_data_source.productcode == productcode,
                     db.product_acquisition_data_source.subproductcode == subproductcode,
                     db.product_acquisition_data_source.version == version,
                     db.product_acquisition_data_source.activated)

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
        raise logger.error("get_product_sources: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_product_sources: Database query error!\n ->%s" % exceptionvalue)


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
        raise logger.error("get_datasource_descr: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_ingestion: Database query error!\n ->%s" % exceptionvalue)


def get_eumetcast_sources(echo=False):
    try:
        session = db.session

        es = session.query(db.eumetcast_source.eumetcast_id, db.eumetcast_source.filter_expression_jrc).subquery()
        pads = aliased(db.product_acquisition_data_source)

        # The columns on the subquery "es" are accessible through an attribute called c , es.c.filter_expression_jrc
        eumetcast_sources = session.query(pads, es.c.eumetcast_id, es.c.filter_expression_jrc).\
            outerjoin(es, pads.data_source_id == es.c.eumetcast_id).\
            filter(and_(pads.type == 'EUMETCAST', pads.activated)).all()

        if echo:
            for row in eumetcast_sources:
                print row

        return eumetcast_sources

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        raise logger.error("get_eumetcast_sources: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_ingestion: Database query error!\n ->%s" % exceptionvalue)

