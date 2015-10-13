####################################################################################################################
#	purpose: Define functions to access and query the postgresql db
#	author:  Jurriaan van 't Klooster
#	date:	 20.03.2014
#   descr:	 Functions to access and query the DB using SQLSoup and SQLAlchemy as Database Abstraction Layer and ORM.
####################################################################################################################

import sys
import traceback
# import sqlsoup
# import datetime

from sqlalchemy.sql import func, select, or_, and_, desc, asc, expression
from sqlalchemy.orm import aliased
from sqlalchemy.orm import exc

from lib.python import es_logging as log
from database import connectdb
from database import crud
from config import es_constants
logger = log.my_logger(__name__)

db = connectdb.ConnectDB().db
dbschema_analysis = connectdb.ConnectDB(schema='analysis').db


def get_enabled_ingest_derived_of_product(productcode, version, mapsetcode=None, echo=False):
    global db
    try:
        if mapsetcode is None:
            query = "select p.productcode, p.version, i.mapsetcode, p.subproductcode, p.product_type " + \
                    "from products.product p " + \
                    "     inner join products.ingestion i on p.productcode = i.productcode and p.subproductcode = i.subproductcode and p.version = i.version " + \
                    "where p.productcode = '"+productcode+"' and p.version = '"+version+"' and p.product_type = 'Ingest' and i.enabled = true " + \
                    "union " + \
                    "select p.productcode, p.version, derived.mapsetcode, p.subproductcode, p.product_type " + \
                    "from products.product p " + \
                    "     inner join ( " + \
                    "        select pp.productcode, pp.subproductcode, pp.version, pp.mapsetcode, proc.activated " + \
                    "        from products.process_product pp " + \
                    "             inner join products.processing proc on pp.process_id = proc.process_id where proc.enabled = true and pp.type = 'OUTPUT' and pp.final = true " + \
                    "        ) derived " + \
                    "     on p.productcode = derived.productcode and p.subproductcode = derived.subproductcode and p.version = derived.version " + \
                    "where p.productcode = '"+productcode+"' and p.version = '"+version+"' and p.product_type = 'Derived' " + \
                    "order by mapsetcode"
        else:
            query = "select p.productcode, p.version, i.mapsetcode, p.subproductcode, p.product_type " + \
                    "from products.product p " + \
                    "     inner join products.ingestion i on p.productcode = i.productcode and p.subproductcode = i.subproductcode and p.version = i.version " + \
                    "where p.productcode = '"+productcode+"' and p.version = '"+version+"' and p.product_type = 'Ingest' and i.enabled = true " + \
                    " and i.mapsetcode = '"+mapsetcode+"'" + \
                    "union " + \
                    "select p.productcode, p.version, derived.mapsetcode, p.subproductcode, p.product_type " + \
                    "from products.product p " + \
                    "     inner join ( " + \
                    "        select pp.productcode, pp.subproductcode, pp.version, pp.mapsetcode, proc.activated " + \
                    "        from products.process_product pp " + \
                    "             inner join products.processing proc on pp.process_id = proc.process_id where proc.enabled = true and pp.type = 'OUTPUT' and pp.final = true " + \
                    "        ) derived " + \
                    "     on p.productcode = derived.productcode and p.subproductcode = derived.subproductcode and p.version = derived.version " + \
                    "where p.productcode = '"+productcode+"' and p.version = '"+version+"' and p.product_type = 'Derived' " + \
                    "and derived.mapsetcode = '"+mapsetcode+"'" + \
                    "order by mapsetcode"

        result = db.execute(query)
        result = result.fetchall()

        return result
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_enabled_ingest_derived_of_product: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()


def update_product_info(productinfo, echo=False):
    global db
    status = False
    try:
        query = "UPDATE products.product SET " + \
                "  subproductcode = '" + productinfo['productcode'] + "_native', " + \
                "  descriptive_name = '" + productinfo['descriptive_name'] + "', " + \
                "  description = '" + productinfo['description'] + "' " + \
                "WHERE productcode = '" + productinfo['orig_productcode'] + "' " + \
                "  AND subproductcode = '" + productinfo['orig_productcode'] + "_native' " + \
                "  AND version = '" + productinfo['orig_version'] + "' "

        result = db.execute(query)
        db.commit()

        query = "UPDATE products.product SET " + \
                "  productcode = '" + productinfo['productcode'] + "', " + \
                "  version = '" + productinfo['version'] + "', " + \
                "  provider = '" + productinfo['provider'] + "', " + \
                "  category_id = '" + productinfo['category_id'] + "' " + \
                " WHERE productcode = '" + productinfo['orig_productcode'] + "' " + \
                "  AND version = '" + productinfo['orig_version'] + "' "

        result = db.execute(query)
        db.commit()

        status = True

        return status
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("update_product_info: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()
        return status



def get_categories(echo=False):
    global db
    try:
        query = "SELECT * FROM products.product_category ORDER BY category_id"
        categories = db.execute(query)
        categories = categories.fetchall()

        return categories
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_categories: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()


def get_frequencies(echo=False):
    global db
    try:
        query = "SELECT * FROM products.frequency ORDER BY frequency_id"
        result = db.execute(query)
        result = result.fetchall()

        return result
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_frequencies: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()


def get_dateformats(echo=False):
    global db
    try:
        query = "SELECT * FROM products.date_format ORDER BY date_format"
        result = db.execute(query)
        result = result.fetchall()

        return result
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_dateformats: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()


def get_datatypes(echo=False):
    global db
    try:
        query = "SELECT * FROM products.data_type ORDER BY data_type_id"
        result = db.execute(query)
        result = result.fetchall()

        return result
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_datatypes: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()


def get_eumetcastsources(echo=False):
    global db
    try:
        query = "SELECT * FROM products.eumetcast_source e LEFT OUTER JOIN products.datasource_description dsd " + \
                " ON e.datasource_descr_id = dsd.datasource_descr_id " + \
                "ORDER BY eumetcast_id ASC "
        eumetcastsources = db.execute(query)
        eumetcastsources = eumetcastsources.fetchall()

        return eumetcastsources
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_eumetcastsources: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()


def get_internetsources(echo=False):
    global db
    try:
        query = "SELECT * FROM products.internet_source i LEFT OUTER JOIN products.datasource_description dsd " + \
                " ON i.datasource_descr_id = dsd.datasource_descr_id " + \
                "ORDER BY descriptive_name ASC "
        internetsources = db.execute(query)
        internetsources = internetsources.fetchall()

        return internetsources
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_internetsources: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()


def get_themas(echo=False):
    global db
    try:
        query = "SELECT thema_id, description FROM products.thema ORDER BY thema_id ASC"
        themas = db.execute(query)
        themas = themas.fetchall()

        return themas
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_themas: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()


def set_thema(themaid='', echo=False):
    global db
    try:
        query = "select * from products.set_thema('" + themaid + "'); COMMIT;"
        setthema = db.execute(query)
        # setthemaresult = setthema.fetchall()

        return True     # setthemaresult[0]
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("set_thema: Database query error!\n -> {}".format(exceptionvalue))
        return False
    finally:
        if db.session:
            db.session.close()


def get_i18n(lang='eng', echo=False):

    global dbschema_analysis
    try:
        query = "SELECT DISTINCT label, CASE WHEN " + lang + " is null or trim(" + lang + ")='' THEN " + 'eng' + \
                " ELSE " + lang + " END as langtranslation " + "FROM analysis.i18n ORDER BY label ASC"
        i18n = dbschema_analysis.execute(query)
        i18n = i18n.fetchall()

        return i18n
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_i18n: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if dbschema_analysis.session:
            dbschema_analysis.session.close()
        #dbschema_analysis = None


def get_languages(echo=False):

    global dbschema_analysis

    try:
        l = dbschema_analysis.languages._table

        s = select([l.c.langcode,
                    l.c.langdescription,
                    l.c.active])

        s = s.alias('lang')
        lang = dbschema_analysis.map(s, primary_key=[s.c.langcode])

        where = and_(lang.active == 't')

        languages = []
        if lang.filter(where).count() >= 1:
            languages = lang.filter(where).all()
            # if echo:
            #     for row in languages:
            #         print row

        return languages
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_languages: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if dbschema_analysis.session:
            dbschema_analysis.session.close()
        #dbschema_analysis = None


######################################################################################
#   get_timeseries_drawproperties(prodcut, echo=False)
#   Purpose: get the timeseries drawproperties for the subproduct passed
#   Author: Jurriaan van 't Klooster
#   Date: 2015/05/11
#   Input: echo                 - If True echo the query result in the console for debugging purposes. Default=False
#          product              - List of productcode, subproductcode, version
#
#   Output: Return all the timeseries drawproperties for the requested subproducts.
def get_timeseries_drawproperties(product, echo=False):

    global dbschema_analysis

    try:
        timeseries_drawproperties = []

        where = and_(dbschema_analysis.timeseries_drawproperties.productcode == product['productcode'],
                     dbschema_analysis.timeseries_drawproperties.subproductcode == product['subproductcode'],
                     dbschema_analysis.timeseries_drawproperties.version == product['version'])

        if dbschema_analysis.timeseries_drawproperties.filter(where).count() >= 1:
            timeseries_drawproperties = dbschema_analysis.timeseries_drawproperties.filter(where).all()
            # if echo:
            #     for row in timeseries_drawproperties:
            #         print row
        return timeseries_drawproperties
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_timeseries_drawproperties: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if dbschema_analysis.session:
            dbschema_analysis.session.close()
        #dbschema_analysis = None


def get_timeseries_yaxes(products, echo=False):

    global dbschema_analysis
    try:
        timeseries_yaxes = []

        session = dbschema_analysis.session
        ts_drawprobs = aliased(dbschema_analysis.timeseries_drawproperties)

        timeseries_drawproperties = session.query(
                                                  ts_drawprobs.yaxes_id,
                                                  ts_drawprobs.title,
                                                  ts_drawprobs.unit,
                                                  ts_drawprobs.min,
                                                  ts_drawprobs.max,
                                                  ts_drawprobs.oposite)

        whereall = ''
        count = 0
        for myproduct in products:
            count += 1
            where = and_(ts_drawprobs.productcode == myproduct['productcode'],
                         ts_drawprobs.subproductcode == myproduct['subproductcode'],
                         ts_drawprobs.version == myproduct['version'])
            if count == 1:
                whereall = where
            else:
                whereall = or_(where, whereall)

        if timeseries_drawproperties.filter(whereall).distinct().count() >= 1:
            timeseries_yaxes = timeseries_drawproperties.filter(whereall).distinct().all()
            # if echo:
            #     for row in timeseries_yaxes:
            #         print row
        return timeseries_yaxes
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_timeseries_yaxes: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if dbschema_analysis.session:
            dbschema_analysis.session.close()
        #dbschema_analysis = None


######################################################################################
#   get_timeseries_subproducts(echo=False, productcode=None,version='undefined', subproductcode=None, masked=None)
#   Purpose: Query the database to get the sub product list of the selected product.
#            with their product category that are available for time series.
#            The passed product is of type "Ingest" and must have the timeseries_role set to "Initial".
#            Mainly used in the GUI Analysis tab.
#   Author: Jurriaan van 't Klooster
#   Date: 2015/04/15
#   Input: echo             - If True echo the query result in the console for debugging purposes. Default=False
#          productcode      - The productcode of the specific product requested. Default=None
#          subproductcode   - The subproductcode of the specific product requested. Default=None
#          version          - The version of the specific product requested. Default='undefined'
#          masked           - If given, the result with contain all sub products which are not masked!
#
#   Output: Product list with their product category.
#           The products are in general of type "Ingest" or "Derived" and must have the
#           timeseries_role set to "<subproductcode>"
#           Ordered by product category order_index and productcode.
#
#   SELECT p.productcode, p.version, p.subproductcode, p.activated, pc.category_id, pc.descriptive_name, pc.order_index
#   FROM products.product p
#   WHERE p.productcode = 'fewsnet-rfe'
#     AND p.version = '2.0'
#     AND (p.timeseries_role = '10d' or p.subproductcode = '10d')
#   ORDER BY p.productcode
#
def get_timeseries_subproducts(echo=False,  productcode=None, version='undefined', subproductcode=None, masked=None):

    global db
    try:
        p = db.product._table

        s = select([func.CONCAT(p.c.productcode, '_', p.c.version).label('productid'),
                    p.c.productcode,
                    p.c.subproductcode,
                    p.c.version,
                    p.c.defined_by,
                    p.c.activated,
                    p.c.product_type,
                    p.c.descriptive_name.label('prod_descriptive_name'),
                    p.c.description,
                    p.c.masked,
                    p.c.timeseries_role])

        s = s.alias('pl')
        pl = db.map(s, primary_key=[s.c.productcode, s.c.subproductcode, s.c.version])

        if masked is None:
            where = and_(pl.c.productcode == productcode,
                         pl.c.version == version,
                         or_(pl.c.timeseries_role == subproductcode, pl.c.subproductcode == subproductcode))
        else:
            if not masked:
                where = and_(pl.c.masked == 'f',
                             pl.c.productcode == productcode,
                             pl.c.version == version,
                             or_(pl.c.timeseries_role == subproductcode, pl.c.subproductcode == subproductcode))
            else:
                where = and_(pl.c.masked == 't',
                             pl.c.productcode == productcode,
                             pl.c.version == version,
                             or_(pl.c.timeseries_role == subproductcode, pl.c.subproductcode == subproductcode))

        productslist = pl.filter(where).order_by(asc(pl.c.productcode), asc(pl.c.subproductcode)).all()

        # if echo:
        #     for row in productslist:
        #         print row

        return productslist

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and log the error telling what happened.
        logger.error("get_timeseries_subproducts: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()
        # db = None


######################################################################################
#   get_timeseries_products(echo=False, masked=None)
#   Purpose: Query the database to get the product list with their product category that are available for time series.
#            The products are in general of type "Ingest" and must have the timeseries_role set to "Initial"
#            Mainly used in the GUI Analysis tab.
#   Author: Jurriaan van 't Klooster
#   Date: 2015/04/15
#   Input: echo             - If True echo the query result in the console for debugging purposes. Default=False
#          masked           - If given, the result with contain all Native products which are not masked!
#                             (used by the Analysis tool in the Product Navigator)
#
#   Output: Product list with their product category.
#           The products are in general of type "Ingest" and must have the timeseries_role set to "Initial"
#           Ordered by product category order_index and productcode.
#
#   SELECT p.productcode, p.version, p.activated, pc.category_id, pc.descriptive_name, pc.order_index
#   FROM products.product p outer join products.product_category pc on p.category_id = pc.category_id
#   WHERE p.timeseries_role = 'Initial'
#   ORDER BY pc.order_index, productcode
#
def get_timeseries_products(echo=False,  masked=None):

    global db
    try:
        pc = db.product_category._table
        p = db.product._table

        s = select([func.CONCAT(p.c.productcode, '_', p.c.version).label('productid'),
                    p.c.productcode,
                    p.c.subproductcode,
                    p.c.version,
                    p.c.defined_by,
                    p.c.activated,
                    p.c.product_type,
                    p.c.descriptive_name.label('prod_descriptive_name'),
                    p.c.description,
                    p.c.masked,
                    p.c.timeseries_role,
                    pc.c.category_id,
                    pc.c.descriptive_name.label('cat_descr_name'),
                    pc.c.order_index]).select_from(p.outerjoin(pc, p.c.category_id == pc.c.category_id))

        s = s.alias('pl')
        pl = db.map(s, primary_key=[s.c.productid])

        if masked is None:
            where = and_(pl.c.timeseries_role == 'Initial')
        else:
            if not masked:
                where = and_(pl.c.timeseries_role == 'Initial', pl.c.masked == 'f')
            else:
                where = and_(pl.c.timeseries_role == 'Initial', pl.c.masked == 't')

        productslist = pl.filter(where).order_by(asc(pl.c.order_index), asc(pl.c.productcode)).all()

        # if echo:
        #     for row in productslist:
        #         print row

        return productslist

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and log the error telling what happened.
        logger.error("get_timeseries_products: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()
        # db = None


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

    global dbschema_analysis
    try:

        legend = dbschema_analysis.legend._table
        product_legend = dbschema_analysis.product_legend._table

        productlegends = select([legend.c.legend_id,
                                 legend.c.legend_name,
                                 product_legend.c.default_legend,
                                 product_legend.c.productcode,
                                 product_legend.c.subproductcode,
                                 product_legend.c.version
                                ]).\
            select_from(legend.outerjoin(product_legend, legend.c.legend_id == product_legend.c.legend_id))

        s = productlegends.alias('pl')
        pl = dbschema_analysis.map(s, primary_key=[s.c.legend_id])

        where = and_(pl.c.productcode == productcode,
                     pl.c.subproductcode == subproductcode,
                     pl.c.version == version)
        productlegends = pl.filter(where).all()


        # session = dbschema_analysis.session
        # legend = aliased(dbschema_analysis.legend)
        #
        # product_legend = session.query(dbschema_analysis.product_legend).subquery()
        #
        # productlegends = session.query(legend.legend_id,
        #                                legend.legend_name,
        #                                product_legend.c.default_legend).\
        #     outerjoin(product_legend, legend.legend_id == product_legend.c.legend_id)
        #
        # where = and_(product_legend.c.productcode == productcode,
        #              product_legend.c.subproductcode == subproductcode,
        #              product_legend.c.version == version)
        # productlegends = productlegends.filter(where).all()

        # if echo:
        #     for row in productlegends:
        #         print row

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
        #dbschema_analysis = None


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

    global dbschema_analysis
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
        legend_steps = ls.filter(where).order_by(asc(ls.c.from_step)).all()

        # if echo:
        #     for row in legend_steps:
        #         print row

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
        #dbschema_analysis = None


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

    global dbschema_analysis
    try:

        ls = dbschema_analysis.legend_step._table
        l = dbschema_analysis.legend._table

        s = select([func.MIN(ls.c.from_step).label('realminstep'),
                    func.MAX(ls.c.to_step).label('realmaxstep'),
                    func.MIN(ls.c.to_step-ls.c.from_step).label('minstepwidth'),
                    func.MAX(ls.c.to_step-ls.c.from_step).label('maxstepwidth'),
                    (func.MAX(ls.c.to_step)-func.MIN(ls.c.from_step)).label('totwidth'),
                    func.COUNT(ls.c.legend_id).label('totsteps'),
                    l.c.legend_id,
                    l.c.legend_name,
                    l.c.min_value,
                    l.c.max_value,
                    l.c.min_real_value,
                    l.c.max_real_value,
                    l.c.step_range_from,
                    l.c.step_range_to,
                    l.c.unit
                    ],
                    group_by=[l.c.legend_id,
                              l.c.legend_name,
                              l.c.min_value,
                              l.c.max_value,
                              l.c.min_real_value,
                              l.c.max_real_value,
                              l.c.step_range_from,
                              l.c.step_range_to,
                              l.c.unit]
                   ).select_from(l.outerjoin(ls, l.c.legend_id == ls.c.legend_id))

        s = s.alias('legend_info')
        ls = dbschema_analysis.map(s, primary_key=[s.c.legend_id])

        where = and_(ls.c.legend_id == legendid)
        legend_info = ls.filter(where).all()

        # if echo:
        #     for row in legend_info:
        #         print row

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
        #dbschema_analysis = None


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

    global db
    try:
        i = db.ingestion._table
        m = db.mapset._table
        p = db.product._table

        s = select([func.CONCAT(i.c.productcode, '_', i.c.version).label('productid'),
                    i.c.productcode,
                    i.c.subproductcode,
                    i.c.version,
                    i.c.mapsetcode,
                    p.c.frequency_id,
                    i.c.defined_by,
                    i.c.activated,
                    m.c.descriptive_name.label('mapsetname')]).\
            select_from(i.outerjoin(m, i.c.mapsetcode == m.c.mapsetcode).outerjoin(p, and_(i.c.productcode == p.c.productcode,
                                            i.c.subproductcode == p.c.subproductcode,
                                            i.c.version == p.c.version)))

        s = s.alias('ingest')
        i = db.map(s, primary_key=[s.c.productid, i.c.subproductcode, i.c.mapsetcode])

        where = and_(i.c.defined_by != 'Test_JRC')
        ingestions = i.filter(where).order_by(desc(i.productcode)).all()
        #ingestions = i.order_by(desc(i.productcode)).all()

        # if echo:
        #     for row in ingestions:
        #         print row

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
        # db = None


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
    global db
    try:
        # pa = db.product_acquisition_data_source._table
        # s = select([ func.CONCAT(pa.c.productcode, '_', pa.c.version).label('productid'),
        #              pa.c.productcode,
        #              pa.c.subproductcode,
        #              pa.c.version,
        #              pa.c.data_source_id,
        #              pa.c.defined_by,
        #              pa.c.type,
        #              pa.c.activated,
        #              pa.c.store_original_data,
        #              expression.literal("05/06/2014").label('latest')], from_obj=[pa])
        #
        # s = s.alias('mypa')
        # pa = db.map(s, primary_key=[s.c.productid])
        # dataacquisitions = pa.order_by(desc(pa.productcode)).all()

        query = " SELECT CONCAT(products.product_acquisition_data_source.productcode, '_', products.product_acquisition_data_source.version) AS productid, " + \
                "        productcode, " + \
                "        subproductcode, " + \
                "        version, " + \
                "        data_source_id, " + \
                "        defined_by, " + \
                "        type, " + \
                "        activated, " + \
                "        store_original_data, " + \
                "        '05/06/2014' AS latest " + \
                " FROM products.product_acquisition_data_source ORDER BY productcode DESC"
        dataacquisitions = db.execute(query)
        dataacquisitions = dataacquisitions.fetchall()

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
        # db = None


def get_products_acquisition(echo=False, activated=None):
    global db
    try:
        pc = db.product_category._table
        p = db.product._table

        pads = db.product_acquisition_data_source._table
        s = select([func.COUNT(pads.c.data_source_id).label('totgets'),
                    pads.c.productcode.label('pads_productcode'),
                    pads.c.subproductcode.label('pads_subproductcode'),
                    pads.c.version.label('pads_version')],
                    group_by=[pads.c.productcode,
                              pads.c.subproductcode,
                              pads.c.version],
                    from_obj=[pads])

        s = s.alias('pa')
        db.pa = db.map(s, primary_key=[pads.c.productcode,
                                       pads.c.subproductcode,
                                       pads.c.version])

        s = select([func.CONCAT(p.c.productcode, '_', p.c.version).label('productid'),
                    p.c.productcode,
                    p.c.subproductcode,
                    p.c.version,
                    p.c.defined_by,
                    p.c.activated,
                    p.c.product_type,
                    func.coalesce(p.c.descriptive_name, '').label('prod_descriptive_name'),
                    func.coalesce(p.c.description, '').label('description'),
                    func.coalesce(p.c.provider, '').label('provider'),
                    p.c.masked,
                    pc.c.category_id,
                    pc.c.descriptive_name.label('cat_descr_name'),
                    pc.c.order_index]).select_from(p.outerjoin(pc, p.c.category_id == pc.c.category_id))

        s = s.alias('pl')
        db.pl = db.map(s, primary_key=[s.c.productid])

        if activated is True or activated in ['True', 'true', '1', 't', 'y', 'Y', 'yes', 'Yes']:
            where = and_(db.pl.c.product_type == 'Native',
                         db.pl.c.activated,
                         db.pa.c.totgets > 0)
        elif activated is False or activated in ['False', 'false', '0', 'f', 'n', 'N', 'no', 'No']:
            where = and_(db.pl.c.product_type == 'Native',
                         db.pl.c.activated != 't',
                         db.pa.c.totgets > 0)
        else:
            where = and_(db.pl.c.product_type == 'Native', db.pa.c.totgets > 0)

        productslist = db.join(db.pa, db.pl, and_(db.pa.pads_productcode == db.pl.productcode,
                                                  db.pa.pads_subproductcode == db.pl.subproductcode,
                                                  db.pa.pads_version == db.pl.version), isouter=True)

        productslist = productslist.filter(where).order_by(asc(db.pl.c.order_index), asc(db.pl.c.productcode)).all()

        # if echo:
        #     for row in productslist:
        #         print row

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
        # db = None


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
    global db
    try:
        pc = db.product_category._table
        p = db.product._table

        s = select([func.CONCAT(p.c.productcode, '_', p.c.version).label('productid'),
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
        pl = db.map(s, primary_key=[s.c.productid])

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

        # if echo:
        #     for row in productslist:
        #         print row

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
        # db = None


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
    global db
    try:
        #where = and_(db.frequency.frequency_id == frequency_id)
        #frequency = db.frequency.filter(where).one()
        frequency = db.frequency.get(frequency_id)

        return frequency
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_frequency: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()
        # db = None


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

    global db
    try:
        if allrecs:
            product_out_info = db.product.order_by(asc(db.product.productcode)).all()
            # if echo:
            #     for row in product_out_info:
            #         print row
        else:
            where = and_(db.product.productcode == productcode,
                         db.product.subproductcode == subproductcode,
                         db.product.version == version)
            product_out_info = db.product.filter(where).all()
            # if echo:
            #     print product_out_info
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
        # db = None

######################################################################################
#   get_product_out_info_connect(allrecs=False, echo=False, productcode='', subproductcode='', version='undefined')
#   Purpose: Duplicate the get_product_out_info, by establishing a dedicated connection
#            This is used by processing_merge, which is forked and the connection terminated afterwards
#   Author: Jurriaan van 't Klooster
#   Date: 2014/05/16
#   Input: allrecs          - If True return all products. Default=False
#          echo             - If True echo the query result in the console for debugging purposes. Default=False
#          productcode      - The productcode of the specific product info requested.
#                             If given also subproductcode and version have to be given. Default=''
#          subproductcode   - The subproductcode of the specific product info requested. Default=''
#          version          - The version of the specific product info requested. Default='undefined'
#   Output: Return the fields of all or a specific product record from the table product.
def get_product_out_info_connect(allrecs=False, echo=False, productcode='', subproductcode='', version='undefined'):

    my_db = connectdb.ConnectDB().db
    try:
        if allrecs:
            product_out_info = my_db.product.order_by(asc(db.product.productcode)).all()
            # if echo:
            #     for row in product_out_info:
            #         print row
        else:
            where = and_(my_db.product.productcode == productcode,
                         my_db.product.subproductcode == subproductcode,
                         my_db.product.version == version)
            product_out_info = my_db.product.filter(where).all()
            # if echo:
            #     print product_out_info
        return product_out_info
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_product_out_info: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_product_out_info: Database query error!\n ->%s" % exceptionvalue)
    finally:
        if my_db.session:
            my_db.session.close()
        my_db = None


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
    global db
    try:
        if allrecs:
            product_in_info = db.sub_datasource_description.order_by(asc(db.sub_datasource_description.productcode)).all()
        else:
            where = and_(db.sub_datasource_description.productcode == productcode,
                         db.sub_datasource_description.subproductcode == subproductcode,
                         db.sub_datasource_description.version == version,
                         db.sub_datasource_description.datasource_descr_id == datasource_descr_id)
            product_in_info = db.sub_datasource_description.filter(where).first()
        if product_in_info is None:
            product_in_info = []
        return product_in_info
    except exc.NoResultFound:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_product_in_info: Database query error!\n -> {}".format(exceptionvalue))
        product_in_info = []
        return product_in_info
    finally:
        if db.session:
            db.session.close()
        # db = None


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
    global db
    try:
        if allrecs:
            where = db.product.product_type == 'Native'
            product = db.product.filter(where).order_by(asc(db.product.productcode)).all()
        else:
            where = and_(db.product.productcode == productcode,
                         db.product.product_type == 'Native',
                         db.product.version == version)
            product = db.product.filter(where).first()
        if product is None:
            product = []
        return product
    except exc.NoResultFound:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_product_native : Database query error!\n -> {}".format(exceptionvalue))
        product = []
        return product
    finally:
        if db.session:
            db.session.close()
        # db = None


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
def get_subproduct(productcode='', version='undefined', subproductcode='', masked=False, echo=False):
    global db
    try:
        if masked:
            where = and_(db.product.productcode == productcode,
                         db.product.subproductcode == subproductcode,
                         db.product.version == version,
                         db.product.masked == 'f')
        else:
            where = and_(db.product.productcode == productcode,
                         db.product.subproductcode == subproductcode,
                         db.product.version == version)
        subproduct = db.product.filter(where).first()
        #if subproduct is None:
        #    subproduct = []
        return subproduct
    except exc.NoResultFound:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_subproduct: Database query error!\n -> {}".format(exceptionvalue))
        subproduct = []
        return subproduct
    finally:
        if db.session:
            db.session.close()
        # db = None


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
    global db
    try:
        if allrecs:
            eumetcasts = db.eumetcast_source.order_by(asc(db.eumetcast_source.eumetcast_id)).all()
        else:
            where = db.eumetcast_source.eumetcast_id == source_id
            eumetcasts = db.eumetcast_source.filter(where).first()
        if eumetcasts is None:
            eumetcasts = []
        return eumetcasts
    except exc.NoResultFound:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_eumetcast: Database query error!\n -> {}".format(exceptionvalue))
        eumetcasts = []
        return eumetcasts
    finally:
        if db.session:
            db.session.close()
        # db = None


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
    global db
    try:
        if allrecs:
            internet = db.internet_source.order_by(asc(db.internet_source.internet_id)).all()
        else:
            where = db.internet_source.internet_id == internet_id
            internet = db.internet_source.filter(where).first()
        if internet is None:
            internet = []
        return internet
    except exc.NoResultFound:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_internet: Database query error!\n -> {}".format(exceptionvalue))
        internet = []
        return internet
    finally:
        if db.session:
            db.session.close()
        # db = None


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
    global db
    try:
        mapset = []
        if allrecs:
            if db.mapset.order_by(asc(db.mapset.mapsetcode)).count() >= 1:
                mapset = db.mapset.order_by(asc(db.mapset.mapsetcode)).all()
        else:
            where = db.mapset.mapsetcode == mapsetcode
            if db.mapset.filter(where).count() == 1:
                mapset = db.mapset.filter(where).one()

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
        # db = None


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
    global db
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
                # if echo:
                #     for row in active_ingestions:
                #         print row
        else:
            where = and_(ingest.productcode == productcode,
                         ingest.activated == True,
                         ingest.version == version)
            if ingestion_product.filter(where).count() == 1:    # Exactly 1 product ingestion definition has to exist.
                active_ingestions = ingestion_product.filter(where).one()
                # if echo:
                #     print active_ingestions
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
        # db = None


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
    global db
    try:
        ingestion = []
        if allrecs:
            if db.ingestion.filter(db.ingestion.activated is True).count() >= 1:
                ingestion = db.ingestion.filter(db.ingestion.activated is True).\
                    order_by(asc(db.ingestion.productcode)).all()
                # if echo:
                #     for row in ingestion:
                #         print row
        else:
            where = and_(db.ingestion.productcode == productcode,
                         db.ingestion.activated,
                         #db.ingestion.subproductcode == subproductcode,
                         db.ingestion.version == version)
            if db.ingestion.filter(where).count() >= 1:
                ingestion = db.ingestion.filter(where).all()
                # if echo:
                #     print ingestion
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
        # db = None


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
    global db
    try:
        sources = []
        where = and_(db.product_acquisition_data_source.productcode == productcode,
                     db.product_acquisition_data_source.subproductcode == subproductcode,
                     db.product_acquisition_data_source.version == version)

        if db.product_acquisition_data_source.filter(where).count() >= 1:
            sources = db.product_acquisition_data_source.filter(where). \
                order_by(asc(db.product_acquisition_data_source.type)).all()
            # if echo:
            #     for row in sources:
            #         print row
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
        # db = None


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
    global db
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

        # if echo:
        #     for row in datasource_descr:
        #         print row
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
        # db = None


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
    global db
    try:
        session = db.session

        es = session.query(db.eumetcast_source.eumetcast_id, db.eumetcast_source.filter_expression_jrc).subquery()
        pads = aliased(db.product_acquisition_data_source)

        # The columns on the subquery "es" are accessible through an attribute called "c"
        # e.g. es.c.filter_expression_jrc
        eumetcast_sources = session.query(pads, es.c.eumetcast_id, es.c.filter_expression_jrc).\
            outerjoin(es, pads.data_source_id == es.c.eumetcast_id).\
            filter(and_(pads.type == 'EUMETCAST', pads.activated)).all()

        # if echo:
        #     for row in eumetcast_sources:
        #         print row

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
        # db = None


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

    global db

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
                                 intsrc.c.files_filter_expression,
                                 intsrc.c.status,
                                 intsrc.c.pull_frequency,
                                 intsrc.c.datasource_descr_id)
                     if x != intsrc.c.update_datetime)

        internet_sources = session.query(*args).outerjoin(intsrc, pads.data_source_id == intsrc.c.internet_id).\
            filter(and_(pads.type == 'INTERNET', pads.activated)).all()

        # if echo:
        #     for row in internet_sources:
        #         print row

        return internet_sources

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_active_internet_sources: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()
        # db = None


######################################################################################
#   __get_processing_chains(echo=False)
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
def __get_processing_chains(echo=False):
    global db

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
        # db = None


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
def get_processingchains_input_products(process_id=None):
    global db
    try:
        in_process_id = process_id

        process = db.processing._table
        processinput = db.process_product._table  # session.query(db.process_product).subquery()
        product = db.product._table   # session.query(db.product).subquery()
        pc = db.product_category._table     # session.query(db.product_category).subquery()

        s = select([process.c.process_id,
                    process.c.defined_by.label('process_defined_by'),
                    process.c.activated,
                    process.c.output_mapsetcode,
                    process.c.derivation_method,
                    process.c.algorithm,
                    process.c.priority,

                    processinput.c.productcode,
                    processinput.c.subproductcode,
                    processinput.c.version,
                    processinput.c.mapsetcode,
                    processinput.c.date_format,
                    processinput.c.start_date,
                    processinput.c.end_date,
                    processinput.c.type]).\
            select_from(process.outerjoin(processinput, process.c.process_id == processinput.c.process_id))

        s = s.alias('pi')
        pi = db.map(s, primary_key=[s.c.process_id])
        db.pi = pi

        s = select([func.CONCAT(product.c.productcode, '_', product.c.version).label('productid'),
                    product.c.productcode.label('prod_productcode'),
                    product.c.subproductcode.label('prod_subproductcode'),
                    product.c.version.label('prod_version'),
                    product.c.defined_by,
                    product.c.product_type,
                    product.c.descriptive_name.label('prod_descriptive_name'),
                    product.c.description,

                    pc.c.category_id,
                    pc.c.descriptive_name.label('cat_descr_name'),
                    pc.c.order_index]).\
            select_from(product.outerjoin(pc, product.c.category_id == pc.c.category_id))

        s = s.alias('p')
        p = db.map(s, primary_key=[s.c.productid])
        db.p = p

        processing_chains = db.join(db.pi, db.p, and_(db.pi.productcode == db.p.prod_productcode,
                                    db.pi.subproductcode == db.p.prod_subproductcode,
                                    db.pi.version == db.p.prod_version), isouter=True)

        if in_process_id is not None:
            where = and_(db.pi.c.process_id == in_process_id,
                         db.pi.c.type == 'INPUT')
        else:
            where = and_(db.pi.c.type == 'INPUT')

        processing_chains = processing_chains.filter(where).all()
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
        # db = None


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
    global db
    try:
        if process_id is not None:
            myprocess_id = process_id
            processfinaloutput = db.process_product._table
            product = db.product._table
            pc = db.product_category._table

            s = select([processfinaloutput.c.process_id,
                        processfinaloutput.c.productcode,
                        processfinaloutput.c.subproductcode,
                        processfinaloutput.c.version,
                        processfinaloutput.c.mapsetcode,
                        processfinaloutput.c.type,
                        processfinaloutput.c.activated.label('subactivated'),
                        processfinaloutput.c.final,
                        processfinaloutput.c.date_format,
                        processfinaloutput.c.start_date,
                        processfinaloutput.c.end_date])

            s = s.alias('pfo')
            pfo = db.map(s, primary_key=[s.c.process_id])
            db.pfo = pfo

            s = select([func.CONCAT(product.c.productcode, '_',
                                    product.c.subproductcode, '_',
                                    product.c.version).label('productid'),
                        product.c.productcode.label('prod_productcode'),
                        product.c.subproductcode.label('prod_subproductcode'),
                        product.c.version.label('prod_version'),
                        product.c.defined_by,
                        product.c.product_type,
                        product.c.descriptive_name.label('prod_descriptive_name'),
                        product.c.description,
                        pc.c.category_id,
                        pc.c.descriptive_name.label('cat_descr_name'),
                        pc.c.order_index]).\
                select_from(product.outerjoin(pc, product.c.category_id == pc.c.category_id))

            s = s.alias('p')
            p = db.map(s, primary_key=[s.c.productid])
            db.p = p

            where = and_(db.pfo.c.process_id == myprocess_id,
                         db.pfo.c.type == 'OUTPUT',
                         db.pfo.c.final == True)

            processing_chain_output_products = db.join(db.pfo, db.p, and_(db.pfo.productcode == db.p.prod_productcode,
                                                       db.pfo.subproductcode == db.p.prod_subproductcode,
                                                       db.pfo.version == db.p.prod_version), isouter=True)
            processing_chain_output_products = processing_chain_output_products.filter(where).all()

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
        # db = None

######################################################################################
#   get_processing_chains(echo=False)
#   Purpose: Query the database to get all the defined processing chain definitions
#   Author: Jur van 't Klooster
#   Date: 2015/02/26
#   Input: echo   - If True echo the query result in the console for debugging purposes. Default=False
#   Output: Return a list of all the processing chains definitions
#
#   SELECT * FROM products.processing
#
def get_processing_chains(echo=False):

    global db
    try:
        p = db.processing._table

        s = select([p.c.process_id,
                    p.c.defined_by.label('process_defined_by'),
                    p.c.activated.label('process_activated'),
                    p.c.output_mapsetcode,
                    p.c.derivation_method,
                    p.c.algorithm,
                    p.c.priority,
                    p.c.enabled])

        s = s.alias('pc')
        pc = db.map(s, primary_key=[s.c.process_id])
        where = and_(pc.enabled == 't')
        processing_chains = pc.filter(where).all()

        # session = db.session
        # process = aliased(db.processing)
        #
        # processing_chains = session.query(process.process_id,
        #                                   process.defined_by,
        #                                   process.output_mapsetcode,
        #                                   process.derivation_method,
        #                                   process.algorithm,
        #                                   process.priority).all()

        return processing_chains

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        if echo:
            print traceback.format_exc()
        # Exit the script and print an error telling what happened.
        logger.error("get_active_processing_chains: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()
        # db = None


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

    global db
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
        logger.error("get_active_processing_chains: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()
        # db = None


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

    global db
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
        logger.error("get_processing_chain_products: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()
        # db = None



######################################################################################
#   update_processing_output_products(productcode, version, subproductcode, activated)
#   Purpose: Make sure that a subproduct exist in products table and processing_products
#   Author: M. Clerici
#   Date: 2015/06/08
#   Input:  process_id: process ID (integer)
#           productcode/version/mapset: key identifiers
#           proc_sub_product: 'ProcSubProd' object (as generated by the pipeline)
#           product_out_info: metadata from the input product (as from get_product_out_info)
#
#   Output: OK / error
#
def update_processing_chain_products(process_id, productcode, version, mapsetcode, proc_sub_product, product_out_info):

    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    # 'Hard-coded' definitions
    product_type='Derived'
    defined_by= 'JRC'                       # TEMP: To be changed !???????

    # Extract info from proc_sub_product
    subproductcode=proc_sub_product.sprod
    final=proc_sub_product.final
    descriptive_name=proc_sub_product.descriptive_name
    description= proc_sub_product.description
    frequency_id=proc_sub_product.frequency_id
    date_format=proc_sub_product.date_format
    masked=proc_sub_product.masked
    timeseries_role=proc_sub_product.timeseries_role
    activated=proc_sub_product.active_user

    # Extract info from input_sub_product
    category_id=product_out_info[0].category_id
    provider=product_out_info[0].provider
    scale_factor=product_out_info[0].scale_factor
    scale_offset=product_out_info[0].scale_offset
    nodata=product_out_info[0].nodata
    unit=product_out_info[0].unit
    data_type_id=product_out_info[0].data_type_id

    try:
        productinfo = {'productcode': productcode,
                       'subproductcode': subproductcode,
                       'version': version}

        if crud_db.read('product', **productinfo):
            updatestatus = '{"success":true, "message":"Product already exist in products table!"}'
        else:
            try:
                # Manage product table
                productinfo = {'productcode': productcode,
                               'subproductcode': subproductcode,
                               'version': version,
                               'defined_by': defined_by,
                               'activated': activated,
                               'category_id': category_id,
                               'product_type':product_type,
                               'descriptive_name':descriptive_name,
                               'description':description,
                               'provider':provider,
                               'frequency_id':frequency_id,
                               'date_format':date_format,
                               'scale_factor':scale_factor,
                               'scale_offset':scale_offset,
                               'nodata':nodata,
                               'unit':unit,
                               'data_type_id':data_type_id,
                               'masked':masked,
                               'timeseries_role':timeseries_role}
                crud_db.create('product',productinfo)
                updatestatus = '{"success":true, "message":"Product created in products table!"}'
            except:
                updatestatus = '{"success":false, "message":"Error in creating prod in products table!"}'

        # Manage process_product table
        process_productinfo_pkey = {'process_id': process_id,
                                    'productcode': productcode,
                                    'version': version,
                                    'subproductcode': subproductcode,
                                    'mapsetcode':mapsetcode,
                                    'type':"OUTPUT"}

        if crud_db.read('process_product', **process_productinfo_pkey):
            updatestatus = '{"success":true, "message":"Product already exist in products table!"}'
        else:
            try:
                process_productinfo = {'process_id': process_id,
                                       'productcode': productcode,
                                       'version': version,
                                       'subproductcode': subproductcode,
                                       'mapsetcode':mapsetcode,
                                       'type':"OUTPUT",
                                       'activated': activated,
                                       'final': final,
                                       'date_format': date_format}
                crud_db.create('process_product',process_productinfo)
                updatestatus = '{"success":true, "message":"Product created in products table!"}'
            except:
                updatestatus = '{"success":false, "message":"Error in creating prod in products table!"}'

    # except:
    #     exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
    #     if echo:
    #         print traceback.format_exc()
    #     # Exit the script and print an error telling what happened.
    #     logger.error("get_processing_chain_products: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if crud_db:
            crud_db = None
