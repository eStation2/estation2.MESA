__author__ = "Jurriaan van 't Klooster"

from config.es2 import *
import lib.python.crud as crudDB

#dbglobals = {
#    'host': 'h05-dev-vm19',
#    'port': '5432',
#    'dbUser': 'estation',
#    'dbPass': 'mesadmin',
#    'dbName': 'estationdb',
#    'schema': 'products',
#    'basedir': '/srv/www/eStation2/',
#    'data_path': '',
#    'static_data_path': ''
#}

#url_dns = "postgresql://%s:%s@%s/%s" % (dbglobals['dbUser'], dbglobals['dbPass'], dbglobals['host'], dbglobals['dbName'])

#crud = crud.DBInterface(url_dns, 'products', False)

logger = log.my_logger(__name__)

crud = crudDB.CrudDB()

######################################################################################
#   TEST CRUD FOR TABLE products.datetype
######################################################################################
print "get all the records from date_format table"
for result in crud.read('products.date_format'):
    print result

print "create a new date_format for testing crud"
record = {'date_format': 'TESTING123', 'definition': 'We are testing crud!'}
lucky = crud.create('products.date_format', record)

print "get the record from table date_format with id TESTING123"
for result in crud.read('products.date_format', date_format='TESTING123'):
    print result

print "update date_format for testing crud"
record = {'date_format': 'TESTING123', 'definition': 'Updating this record!'}
crud.update('products.date_format', record)

print "get the record from table date_format with id TESTING123"
for result in crud.read('products.date_format', date_format='TESTING123'):
    print result

#print "deleting date_format 'TESTING123'"
#crud.delete('products.date_format', date_format='TESTING123')

print "get all the records from date_format table"
for result in crud.read('products.date_format'):
    print result


######################################################################################
#   TEST CRUD FOR TABLE products.distribution_frequency
######################################################################################
print "get all the records from frequency table"
for result in crud.read('products.frequency'):
    print result

print "create a new distribution_frequency"
record = {'frequency': 'DAILY', 'definition': 'We are testing crud!'}
crud.create('products.frequency', record)

print "get the record from table frequency with id DAILY"
for result in crud.read('products.frequency', frequency='DAILY'):
    print result

print "update frequency 'DAILY'"
record = {'frequency': 'DAILY', 'definition': 'Updating this record!'}
crud.update('products.frequency', record)

print "get the updated record from table frequency with id DAILY"
for result in crud.read('products.frequency', frequency='DAILY'):
    print result

print "deleting frequency 'DAILY'"
crud.delete('products.frequency', frequency='DAILY')

print "get all the records from frequency table"
for result in crud.read('products.frequency'):
    print result
