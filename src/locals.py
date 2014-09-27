
#
#   File defining 'local' variables, i.e. variables referring to the local machine (quigon, vm19, aniston)
#   Indeed, this is not to be synchronized through machines
#

es2globals = {
    'host': 'localhost',
    'port': '5432',
    'dbUser': 'estation',
    'dbPass': 'mesadmin',
    'dbName': 'estationdb',
    'schema': 'products',
    'base_dir': '/srv/www/eStation2/',              # eStation2 installation dir
    'data_dir': '',                                 # root dir for all eStation2 operational data
    'ingest_dir': '',                               # 'pool' dir for all retrieved files (GET service)
    'static_data_path': '',
    'temp_dir': '/tmp/eStation2/'
}


# Add testing directories
es2globals['test_base_dir'] = es2globals['base_dir'] + 'TestFiles/'
es2globals['test_data_in_dir'] = es2globals['test_base_dir'] + 'Inputs/'
es2globals['test_data_refs_dir'] = es2globals['test_base_dir'] + 'RefsOutput/'
es2globals['test_data_out'] = es2globals['test_base_dir'] + 'Outputs/'
es2globals['db_test_mode'] = 0

try:
    from my_locals import *
except ImportError:
    pass

