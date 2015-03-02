####################################################################################################################
#	purpose: Define functions to access and query the postgresql db
#	author:  Jurriaan van 't Klooster
#	date:	 20.03.2014
#   descr:	 Functions to access and query the DB using SQLSoup and SQLAlchemy as Database Abstraction Layer and ORM.
####################################################################################################################

import sys
import traceback
import sqlsoup
import datetime

from sqlalchemy.sql import func, select, or_, and_, desc, asc, expression
from sqlalchemy.orm import aliased
from lib.python import es_logging as log
from database import connectdb

logger = log.my_logger(__name__)

db = connectdb.ConnectDB().db
dbschema_analysis = connectdb.ConnectDB(schema='analysis').db


######################################################################################
#   get_legend_steps(legendid, echo=False)
#   Purpose: Query the database to get the legend info needed for mapserver mapfile SCALE_BUCKETS setting.
#   Author: Jurriaan van 't Klooster
#   Date: 2014/07/31
#   Input: echo             - If True echo the query result in the console for debugging purposes. Default=False
#
#   Output: Return legend steps of the given legendid, needed for mapserver mapfile LAYER CLASS settings.
#
#   SELECT pl.default_legend,
#          pl.legend_id,
#          l.legend_name,
#          CASE WHEN pl.default_legend THEN 'x-grid3-radio-col-on' ELSE 'x-grid3-radio-col' END as "defaulticon"
#   FROM analysis.product_legend  pl join analysis.legend l on pl.legend_id = l.legend_id
#   WHERE productcode =  param_productcode
#     AND version = param_version
#     AND subproductcode = param_subproductcode
#
def get_product_legends(productcode=None, subproductcode=None, version=None, echo=False):
    try:
        session = db.session
        legend = aliased(dbschema_analysis.legend)

        product_legend = session.query(dbschema_analysis.product_legend).subquery()

        productlegends = session.query(legend.legend_id,
                                       legend.legend_name,
                                       product_legend.c.default_legend).\
            outerjoin(product_legend,
                      legend.productcode == product_legend.c.productcode,
                      legend.version == product_legend.c.version,
                      legend.subproductcode == product_legend.c.subproductcode).all()

        if echo:
            for row in productlegends:
                print row

        return productlegends

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and log the error telling what happened.
        logger.error("get_product_legends: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if dbschema_analysis.session:
            dbschema_analysis.session.close()


######################################################################################
#   get_legend_steps(legendid, echo=False)
#   Purpose: Query the database to get the legend info needed for mapserver mapfile SCALE_BUCKETS setting.
#   Author: Jurriaan van 't Klooster
#   Date: 2014/07/31
#   Input: echo             - If True echo the query result in the console for debugging purposes. Default=False
#
#   Output: Return legend steps of the given legendid, needed for mapserver mapfile LAYER CLASS settings.
#
#    SELECT ls.*
#    FROM analysis.legend_step ls
#    WHERE ls.legend_id = legendid
#    ORDER BY from_step
#
def get_legend_steps(legendid=None, echo=False):
    try:

        ls = dbschema_analysis.legend_step._table

        s = select([ls.c.legend_id,
                    ls.c.from_step,
                    ls.c.to_step,
                    ls.c.color_rgb,
                    ls.c.color_label,
                    ls.c.group_label
                    ]
                   )

        s = s.alias('legend_steps')
        ls = dbschema_analysis.map(s, primary_key=[s.c.legend_id, s.c.from_step, s.c.to_step])

        where = and_(ls.c.legend_id == legendid)
        legend_steps = ls.filter(where).all()

        if echo:
            for row in legend_steps:
                print row

        return legend_steps

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and log the error telling what happened.
        logger.error("get_legend_steps: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if dbschema_analysis.session:
            dbschema_analysis.session.close()


######################################################################################
#   get_legend_info(legendid, echo=False)
#   Purpose: Query the database to get the legend info needed for mapserver mapfile SCALE_BUCKETS setting.
#   Author: Jurriaan van 't Klooster
#   Date: 2014/07/31
#   Input: echo             - If True echo the query result in the console for debugging purposes. Default=False
#
#   Output: Return legend info of the given legendid, needed for mapserver mapfile SCALE_BUCKETS setting.
#
#    SELECT MIN(analysis.legend_step.from_step) AS minstep,
#           MAX(analysis.legend_step.to_step) AS maxstep,
#           MIN(analysis.legend_step.to_step - analysis.legend_step.from_step) AS minstepwidth,
#           MAX(analysis.legend_step.to_step - analysis.legend_step.from_step) AS maxstepwidth,
#           MAX(analysis.legend_step.to_step) - MIN(analysis.legend_step.from_step) AS totwidth,
#           COUNT(analysis.legend_step.legend_id) AS totsteps,
#           analysis.legend_step.legend_id
#    FROM analysis.legend_step
#    WHERE analysis.legend_step.legend_id = legendid
#    GROUP BY analysis.legend_step.legend_id
#
def get_legend_info(legendid=None, echo=False):
    try:

        ls = dbschema_analysis.legend_step._table

        s = select([func.MIN(ls.c.from_step).label('minstep'),
                    func.MAX(ls.c.to_step).label('maxstep'),
                    func.MIN(ls.c.to_step-ls.c.from_step).label('minstepwidth'),
                    func.MAX(ls.c.to_step-ls.c.from_step).label('maxstepwidth'),
                    (func.MAX(ls.c.to_step)-func.MIN(ls.c.from_step)).label('totwidth'),
                    func.COUNT(ls.c.legend_id).label('totsteps'),
                    ls.c.legend_id
                    ],
                    group_by=[ls.c.legend_id]
                   )

        s = s.alias('legend_info')
        ls = dbschema_analysis.map(s, primary_key=[s.c.legend_id])

        where = and_(ls.c.legend_id == legendid)
        legend_info = ls.filter(where).all()

        if echo:
            for row in legend_info:
                print row

        return legend_info

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and log the error telling what happened.
        logger.error("get_legend_info: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if dbschema_analysis.session:
            dbschema_analysis.session.close()


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
#    SELECT productcode, subproductcode, version, mapsetcode, defined_by,  activated, mapsetname
#    FROM products.ingestion;
#
def get_ingestions(echo=False):
    try:
        i = db.ingestion._table
        m = db.mapset._table
        s = select([func.CONCAT(i.c.productcode, '_', i.c.version).label('productID'),
                    i.c.productcode,
                    i.c.subproductcode,
                    i.c.version,
                    i.c.mapsetcode,
                    i.c.defined_by,
                    i.c.activated,
                    m.c.descriptive_name.label('mapsetname')]).select_from(i.outerjoin(m, i.c.mapsetcode == m.c.mapsetcode))

        s = s.alias('ingest')
        i = db.map(s, primary_key=[s.c.productID, i.c.subproductcode, i.c.mapsetcode])

        where = and_(i.c.defined_by != 'Test_JRC')
        ingestions = i.filter(where).order_by(desc(i.productcode)).all()
        #ingestions = i.order_by(desc(i.productcode)).all()

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
    finally:
        if db.session:
            db.session.close()


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
def get_dataacquisitions(echo=False):
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

        if echo:
            for row in dataacquisitions:
                print row

        return dataacquisitions

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and log the error telling what happened.
        logger.error("get_dataacquisitions: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()


######################################################################################
#   get_products(echo=False, activated=None, masked=None)
#   Purpose: Query the database to get the (Native) product list with their product category.
#            Mainly used in the GUI Acquisition tab.
#   Author: Jurriaan van 't Klooster
#   Date: 2014/07/08
#   Input: echo             - If True echo the query result in the console for debugging purposes. Default=False
#          activated        - If not given the result with contain all Native products
#                             (used for acquisition, ingestion and processing)
#          masked           - If given, the result with contain all Native products which are not masked!
#                             (used by the Analysis tool in the Product Navigator)
#
#   Output: Return the (Native) product list with their product category
#           ordered by product category order_index and productcode.
#
#   SELECT p.productcode, p.version, p.activated, pc.category_id, pc.descriptive_name, pc.order_index
#   FROM products.product p inner join products.product_category pc on p.category_id = pc.category_id
#   WHERE p.product_type = 'Native'
#   ORDER BY pc.order_index, productcode
#
def get_products(echo=False, activated=None, masked=None):
    try:
        pc = db.product_category._table
        p = db.product._table

        s = select([func.CONCAT(p.c.productcode, p.c.version).label('productID'),
                    p.c.productcode,
                    p.c.subproductcode,
                    p.c.version,
                    p.c.defined_by,
                    p.c.activated,
                    p.c.product_type,
                    p.c.descriptive_name.label('prod_descriptive_name'),
                    p.c.description,
                    p.c.masked,
                    pc.c.category_id,
                    pc.c.descriptive_name.label('cat_descr_name'),
                    pc.c.order_index]).select_from(p.outerjoin(pc, p.c.category_id == pc.c.category_id))

        s = s.alias('pl')
        pl = db.map(s, primary_key=[s.c.productID])

        if masked is None:
            if activated is True or activated in ['True', 'true', '1', 't', 'y', 'Y', 'yes', 'Yes']:
                where = and_(pl.c.product_type == 'Native', pl.c.activated)
            elif activated is False or activated in ['False', 'false', '0', 'f', 'n', 'N', 'no', 'No']:
                where = and_(pl.c.product_type == 'Native', pl.c.activated != 't')
            else:
                where = and_(pl.c.product_type == 'Native')
        else:
            if not masked:
                where = and_(pl.c.product_type == 'Native', pl.c.masked == 'f')
            else:
                where = and_(pl.c.product_type == 'Native', pl.c.masked == 't')

        productslist = pl.filter(where).order_by(asc(pl.c.order_index), asc(pl.c.productcode)).all()

        if echo:
            for row in productslist:
                print row

        return productslist

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and log the error telling what happened.
        logger.error("get_products: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()


######################################################################################
#   get_frequency(frequency_id='', echo=False)
#   Purpose: Query the database to get the record of a specific frequency
#            given its frequency_id, from the table frequency.
#   Author: Jurriaan van 't Klooster
#   Date: 2015/01/22
#   Input: frequency_id     - The frequency_id of the specific frequency info requested. Default=''
#          echo             - If True echo the query result in the console for debugging purposes. Default=False
#   Output: Return the fields of all or a specific product record with product_type='Native' from the table product.
def get_frequency(frequency_id='', echo=False):
    try:
        #where = and_(db.frequency.frequency_id == frequency_id)
        #frequency = db.frequency.filter(where).one()
        frequency = db.frequency.get(frequency_id)

        if echo:
            print frequency

        return frequency
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_frequency : Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()


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
    finally:
        if db.session:
            db.session.close()


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
    finally:
        if db.session:
            db.session.close()


######################################################################################
#   get_product_native(productcode='', version='undefined', allrecs=False, echo=False)
#   Purpose: Query the database to get the records of all products or one specific product
#            with product_type='Native' from the table product.
#   Author: Jurriaan van 't Klooster
#   Date: 2014/05/16
#   Input: productcode      - The productcode of the specific product info requested. Default=''
#          version          - The product version
#          allrecs          - If True return all products. Default=False
#          echo             - If True echo the query result in the console for debugging purposes. Default=False
#   Output: Return the fields of all or a specific product record with product_type='Native' from the table product.
def get_product_native(productcode='', version='undefined', allrecs=False, echo=False):
    try:
        if allrecs:
            where = db.product.product_type == 'Native'
            product = db.product.filter(where).order_by(asc(db.product.productcode)).all()
            if echo:
                for row in product:
                    print row
        else:
            where = and_(db.product.productcode == productcode,
                         db.product.product_type == 'Native',
                         db.product.version == version)
            product = db.product.filter(where).one()

            if echo:
                print product
        return product
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_product_native : Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_product_native: Database query error!\n ->%s" % exceptionvalue)
    finally:
        if db.session:
            db.session.close()


######################################################################################
#   get_subproduct(productcode='', version='undefined', subproductcode='', echo=False)
#   Purpose: Query the database to get the records of all products or one specific product
#            with product_type='Native' from the table product.
#   Author: Jurriaan van 't Klooster
#   Date: 2014/05/16
#   Input: productcode      - The productcode of the specific product info requested. Default=''
#          version          - The product version
#          allrecs          - If True return all products. Default=False
#          echo             - If True echo the query result in the console for debugging purposes. Default=False
#   Output: Return the fields of all or a specific product record with product_type='Native' from the table product.
def get_subproduct(productcode='', version='undefined', subproductcode='', echo=False):
    try:
        where = and_(db.product.productcode == productcode,
                     db.product.subproductcode == subproductcode,
                     db.product.version == version)
        subproduct = db.product.filter(where).one()

        if echo:
            print subproduct

        return subproduct
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_subproduct: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_subproduct: Database query error!\n ->%s" % exceptionvalue)
    finally:
        if db.session:
            db.session.close()


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
    finally:
        if db.session:
            db.session.close()


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
    finally:
        if db.session:
            db.session.close()


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
    finally:
        if db.session:
            db.session.close()


######################################################################################
#   get_ingestion_product(allrecs=False, echo=False, productcode_in='', version_in='')
#   Purpose: Query the database to get all product ingestion (allrecs==True) definitions or one specific
#            product ingestion definition at product level from the table ingestion.
#   Author: Jurriaan van 't Klooster
#   Date: 2014/05/16
#   Input: allrecs          - If True return all products. Default=False
#          echo             - If True echo the query result in the console for debugging purposes. Default=False
#          productcode      - The productcode of the specific product ingestion definition requested. Default=''
#          version          - The version of the specific product ingestion definition requested. Default='undefined'
#   Output: Return the productcode, version and count() of subproducts of all
#           [or a specific product ingestion definition] from the table ingestion.
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
    finally:
        if db.session:
            db.session.close()


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
            if db.ingestion.filter(db.ingestion.activated is True).count() >= 1:
                ingestion = db.ingestion.filter(db.ingestion.activated is True).\
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
    finally:
        if db.session:
            db.session.close()


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
    finally:
        if db.session:
            db.session.close()


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
    finally:
        if db.session:
            db.session.close()


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
        logger.error("get_eumetcast_sources: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()


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

        intsrc = session.query(db.internet_source).subquery()
        pads = aliased(db.product_acquisition_data_source)
        # The columns on the subquery "intsrc" are accessible through an attribute called "c"
        # e.g. intsrc.c.filter_expression_jrc

        args = tuple(x for x in (pads,
                                 intsrc.c.internet_id,
                                 intsrc.c.defined_by,
                                 intsrc.c.descriptive_name,
                                 intsrc.c.description,
                                 intsrc.c.modified_by,
                                 intsrc.c.update_datetime,
                                 intsrc.c.url,
                                 intsrc.c.user_name,
                                 intsrc.c.password,
                                 intsrc.c.type,
                                 intsrc.c.frequency_id,
                                 intsrc.c.start_date,
                                 intsrc.c.end_date,
                                 intsrc.c.include_files_expression,
                                 intsrc.c.exclude_files_expression,
                                 intsrc.c.status,
                                 intsrc.c.pull_frequency,
                                 intsrc.c.datasource_descr_id)
                     if x != intsrc.c.update_datetime)

        internet_sources = session.query(*args).outerjoin(intsrc, pads.data_source_id == intsrc.c.internet_id).\
            filter(and_(pads.type == 'INTERNET', pads.activated)).all()

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
    finally:
        if db.session:
            db.session.close()


######################################################################################
#   get_processing_chains(echo=False)
#   Purpose: Query the database to get all the processing chains definitions or one specific
#            product definition at product level from the table processing (and related).
#   Author: Jurriaan van 't Klooster
#   Date: 2014/12/17
#   Input: echo   - If True echo the query result in the console for debugging purposes. Default=False
#   Output: Return a list of all the processing chains definitions and it's input product
#
#   SELECT p.*, pin.*
#   FROM products.processing p
#   INNER JOIN (SELECT * FROM products.process_product WHERE type = 'INPUT') pin
#   ON p.process_id = pin.process_id
#
def get_processing_chains(echo=False):

    active_processing_chains = []
    try:
        session = db.session
        process = aliased(db.processing)

        processinput = session.query(db.process_product).subquery()

        # The columns on the subquery "processinput" are accessible through an attribute called "c"
        # e.g. es.c.productcode
        active_processing_chains = session.query(process.process_id,
                                                 process.defined_by,
                                                 process.output_mapsetcode,
                                                 process.derivation_method,
                                                 process.algorithm,
                                                 process.priority,

                                                 processinput.c.productcode,
                                                 processinput.c.subproductcode,
                                                 processinput.c.version,
                                                 processinput.c.mapsetcode,
                                                 processinput.c.date_format,
                                                 processinput.c.start_date,
                                                 processinput.c.end_date).\
            outerjoin(processinput, process.process_id == processinput.c.process_id).\
            filter(and_(processinput.c.type == 'INPUT', process.activated == True)).all()

        return active_processing_chains

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_processing_chains: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()


######################################################################################
#   get_processingchains_input_products()
#   Purpose: Query the database to get all the processing chains definitions or one specific
#            product definition at product level from the table processing (and related).
#   Author: Jurriaan van 't Klooster
#   Date: 2014/12/17
#   Input: echo   - If True echo the query result in the console for debugging purposes. Default=False
#   Output: Return a list of all the processing chains definitions and it's input product
#
#   SELECT p.*, pin.*
#   FROM products.processing p
#   INNER JOIN (SELECT * FROM products.process_product WHERE type = 'INPUT') pin
#   ON p.process_id = pin.process_id
#
def get_processingchains_input_products():
    processing_chains = []
    try:
        session = db.session

        process = aliased(db.processing)
        #processinput = aliased(db.process_product)
        #product = aliased(db.product)
        #pc = aliased(db.product_category)

        processinput = session.query(db.process_product).subquery()
        product = session.query(db.product).subquery()
        pc = session.query(db.product_category).subquery()

        # The columns on the subquery "processinput" are accessible through an attribute called "c"
        # e.g. processinput.c.productcode
        processing_chains = session.query(process.process_id,
                                          process.defined_by.label('process_defined_by'),
                                          process.activated,
                                          process.output_mapsetcode,
                                          process.derivation_method,
                                          process.algorithm,
                                          process.priority,

                                          processinput.c.productcode,
                                          processinput.c.subproductcode,
                                          processinput.c.version,
                                          processinput.c.mapsetcode,
                                          processinput.c.date_format,
                                          processinput.c.start_date,
                                          processinput.c.end_date,

                                          func.CONCAT(product.c.productcode, '_', product.c.version).label('productID'),
                                          #product.c.productcode,
                                          #product.c.subproductcode,
                                          #product.c.version,
                                          product.c.defined_by,
                                          #product.c.activated,
                                          product.c.product_type,
                                          product.c.descriptive_name.label('prod_descriptive_name'),
                                          product.c.description,
                                          pc.c.category_id,
                                          pc.c.descriptive_name.label('cat_descr_name'),
                                          pc.c.order_index).\
            outerjoin(processinput, process.process_id == processinput.c.process_id).\
            outerjoin(product, and_(processinput.c.productcode == product.c.productcode,
                      processinput.c.subproductcode == product.c.subproductcode,
                      processinput.c.version == product.c.version)).\
            outerjoin(pc, product.c.category_id == pc.c.category_id).\
            filter(and_(processinput.c.type == 'INPUT')).all()

        return processing_chains

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        #if echo:
        #    print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_processingchains_input_products: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()


######################################################################################
#   get_processingchain_output_products(process_id=None, echo=False)
#   Purpose: Query the database to get the final output (sub) products of a given processing chain (process_id)
#            from the table process_product (and product table).
#   Author: Jurriaan van 't Klooster
#   Date: 2015/01/02
#   Input: echo   - If True echo the query result in the console for debugging purposes. Default=False
#   Output: Return a list of the final output (sub) products of a given processing chain (process_id)
#
def get_processingchain_output_products(process_id=None):

    processing_chain_output_products = []
    try:
        if process_id is not None:
            session = db.session

            processfinaloutput = aliased(db.process_product)

            product = session.query(db.product).subquery()
            pc = session.query(db.product_category).subquery()

            # The columns on the subquery "processinput" are accessible through an attribute called "c"
            # e.g. processinput.c.productcode
            processing_chain_output_products = session.query(processfinaloutput.process_id,
                                                             processfinaloutput.productcode,
                                                             processfinaloutput.subproductcode,
                                                             processfinaloutput.version,
                                                             processfinaloutput.mapsetcode,
                                                             processfinaloutput.type,
                                                             processfinaloutput.activated.label('subactivated'),
                                                             processfinaloutput.final,
                                                             processfinaloutput.date_format,
                                                             processfinaloutput.start_date,
                                                             processfinaloutput.end_date,

                                                             func.CONCAT(product.c.productcode, '_',
                                                                         product.c.subproductcode, '_',
                                                                         product.c.version).label('productID'),
                                                             product.c.defined_by,
                                                             product.c.product_type,
                                                             product.c.descriptive_name.label('prod_descriptive_name'),
                                                             product.c.description,
                                                             pc.c.category_id,
                                                             pc.c.descriptive_name.label('cat_descr_name'),
                                                             pc.c.order_index).\
                outerjoin(product, and_(processfinaloutput.productcode == product.c.productcode,
                          processfinaloutput.subproductcode == product.c.subproductcode,
                          processfinaloutput.version == product.c.version)).\
                outerjoin(pc, product.c.category_id == pc.c.category_id).\
                filter(and_(processfinaloutput.process_id == process_id,
                            processfinaloutput.type == 'OUTPUT',
                            processfinaloutput.final == True)).all()

        return processing_chain_output_products

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        #if echo:
        #    print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_processingchain_output_products: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()


######################################################################################
#   get_active_processing_chains(echo=False)
#   Purpose: Query the database to get all the active processing chains definitions or one specific
#   Author: M. Clerici
#   Date: 2015/02/26
#   Input: echo   - If True echo the query result in the console for debugging purposes. Default=False
#   Output: Return a list of all the processing chains definitions
#
#   SELECT p.*, pin.*
#   FROM products.processing p
#   INNER JOIN (SELECT * FROM products.process_product WHERE type = 'INPUT') pin
#   ON p.process_id = pin.process_id
#
def get_active_processing_chains(echo=False):

    active_processing_chains = []
    try:
        session = db.session
        process = aliased(db.processing)

        #processinput = session.query(db.process_product).subquery()

        # The columns on the subquery "processinput" are accessible through an attribute called "c"
        # e.g. es.c.productcode
        active_processing_chains = session.query(process.process_id,
                                                 process.defined_by,
                                                 process.output_mapsetcode,
                                                 process.derivation_method,
                                                 process.algorithm,
                                                 process.priority).\
            filter(process.activated == True).all()

        return active_processing_chains

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_processing_chains: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()


######################################################################################
#   get_processing_chains_products(process_id,echo=False, type='')
#   Purpose: Query the database to get all input products for a processing chains
#   Author: M. Clerici
#   Date: 2015/02/26
#   Input: echo   - If True echo the query result in the console for debugging purposes. Default=False
#   Output: Return a list of all the processing chains definitions and it's input product
#
#   SELECT p.*, pin.*
#   FROM products.processing p
#   INNER JOIN (SELECT * FROM products.process_product WHERE type = 'INPUT') pin
#   ON p.process_id = pin.process_id
#
def get_processing_chain_products(process_id,echo=False, type='All'):

    products = []
    try:
        session = db.session
        process = aliased(db.processing)

        processinput = session.query(db.process_product).subquery()

        # The columns on the subquery "processinput" are accessible through an attribute called "c"
        # e.g. es.c.productcode
        if type == 'All':
            products = session.query(process.process_id,
                                                 processinput.c.productcode,
                                                 processinput.c.subproductcode,
                                                 processinput.c.version,
                                                 processinput.c.mapsetcode,
                                                 processinput.c.date_format,
                                                 processinput.c.start_date,
                                                 processinput.c.end_date).\
                outerjoin(processinput, process.process_id == processinput.c.process_id)

        elif type == 'input':
            products = session.query(process.process_id,
                                                 processinput.c.productcode,
                                                 processinput.c.subproductcode,
                                                 processinput.c.version,
                                                 processinput.c.mapsetcode,
                                                 processinput.c.date_format,
                                                 processinput.c.start_date,
                                                 processinput.c.end_date).\
                outerjoin(processinput, process.process_id == processinput.c.process_id).\
                filter(and_(processinput.c.type == 'INPUT',processinput.c.process_id == process_id)).all()

        elif type == 'output':
            products = session.query(process.process_id,
                                                 processinput.c.productcode,
                                                 processinput.c.subproductcode,
                                                 processinput.c.version,
                                                 processinput.c.mapsetcode,
                                                 processinput.c.date_format,
                                                 processinput.c.start_date,
                                                 processinput.c.end_date).\
                outerjoin(processinput, process.process_id == processinput.c.process_id).\
                filter(and_(processinput.c.type == 'OUTPUT',processinput.c.process_id == process_id)).all()

        else:
            logger.error("get_processing_chain_products: type must be all/input/output")

        return products

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_processing_chains: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()

