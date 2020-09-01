from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
from builtins import object

import sys
import sqlalchemy
import sqlsoup
from sqlalchemy.orm import *

from lib.python import es_logging as log
from config import es_constants

standard_library.install_aliases()

logger = log.my_logger(__name__)


######################################################################################
#   connect_db()
#   Purpose: Create a connection to the database
#   Author: Marco Clerici and Jurriaan van 't Klooster
#   Date: 2014/05/16
#   Input: schema='products', usesqlsoup=True
#   Output: Return connection handler to the database
class ConnectDB(object):

    @staticmethod
    def get_db_url():
        db_url = "postgresql://%s:%s@%s:%s/%s" % (es_constants.es2globals['dbuser'],
                                                  es_constants.es2globals['dbpass'],
                                                  es_constants.es2globals['host'],
                                                  es_constants.es2globals['port'],
                                                  es_constants.es2globals['dbname']
                                                  )

        # logger.debug("Connect string: %s " % db_url)
        return db_url

    @staticmethod
    def get_db_engine():
        return sqlalchemy.create_engine(ConnectDB.get_db_url())

    # Initialize the DB
    def __init__(self, schema='products', usesqlsoup=True):

        try:
            self.schema = schema or es_constants.es2globals['schema_products']
            if usesqlsoup:
                dburl = self.get_db_url()
                self.db = sqlsoup.SQLSoup(dburl)
                # myengine = self.db.engine
                self.session = sqlsoup.Session  # self.db.session
            else:
                self.db = self.get_db_engine()
                mysession = sessionmaker(bind=self.db, autoflush=False)
                self.db.session = mysession()
                self.session = mysession()

            self.db.schema = self.schema

            import logging
            self.db.engine.echo = False
            self.db.engine.logger.setLevel(logging.NOTSET)
            self.db.engine.logger.disabled = True
            self.db.engine.logger.level = logging.NOTSET
            logging.basicConfig(level=logging.NOTSET)
            # sqllogger = logging.getLogger('sqlalchemy.engine')
            logging.getLogger('sqlalchemy.engine').setLevel(logging.NOTSET)  # NOTSET
        except:
            exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
            # print traceback.format_exc()
            # Exit the script and print an error telling what happened.
            logger.error("Database connection failed!\n -> {}".format(exceptionvalue))
