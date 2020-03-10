from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
####################################################################################################################
#	purpose: Define functions to access and query the postgresql db
#	author:  Jurriaan van 't Klooster
#	date:	 20.03.2014
#   descr:	 Functions to access and query the DB using SQLSoup and SQLAlchemy as Database Abstraction Layer and ORM.
####################################################################################################################

from future import standard_library
standard_library.install_aliases()
import sys
import traceback
# import sqlsoup
# import datetime

from sqlalchemy.sql import func, select, or_, and_, desc, asc, expression

from lib.python import es_logging as log
from database import connectdb
logger = log.my_logger(__name__)


######################################################################################
#   get_product_out_info(allrecs=False, productcode='', subproductcode='', version='undefined')
#   Purpose: Query the database to get the records of all or a specific product from the table product
#   Author: Jurriaan van 't Klooster
#   Date: 2014/05/16
#   Input: allrecs          - If True return all products. Default=False
#          productcode      - The productcode of the specific product info requested.
#                             If given also subproductcode and version have to be given. Default=''
#          subproductcode   - The subproductcode of the specific product info requested. Default=''
#          version          - The version of the specific product info requested. Default='undefined'
#   Output: Return the fields of all or a specific product record from the table product.
def get_product_out_info(allrecs=False, productcode='', subproductcode='', version='undefined'):

    db = connectdb.ConnectDB().db
    try:
        if allrecs:
            product_out_info = db.product.order_by(asc(db.product.productcode)).all()
        else:
            where = and_(db.product.productcode == productcode,
                         db.product.subproductcode == subproductcode,
                         db.product.version == version)
            product_out_info = db.product.filter(where).all()

        return product_out_info
    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        # Exit the script and print an error telling what happened.
        logger.error("get_product_out_info: Database query error!\n -> {}".format(exceptionvalue))
        #raise Exception("get_product_out_info: Database query error!\n ->%s" % exceptionvalue)
    finally:
        if db.session:
            db.session.close()
        db = None

