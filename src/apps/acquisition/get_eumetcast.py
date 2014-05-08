#
#	purpose: Define the get_eumetcast service
#	author:  M.Clerici
#	date:	 19.02.2014
#   descr:	 Reads the definition from eStation DB and execute the copy to local disk
#	history: 1.0


from config.es2 import *

logger = log.my_logger(__name__)

#eumetcast_files_dir = '/home/esuser/my_eumetcast_dir/'
#internet_files_dir = '/home/esuser/my_data_ingest_dir/'
data_dir_in = test_data_dir_in
data_dir_out = test_data_dir_out
