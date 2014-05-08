import os
#base_dir = os.environ['ESTATION2PATH']
execfile('/srv/www/eStation2/locals.py')

from config.es2 import *
import time

start = time.clock()

import test_ingestion as t
cl = t.TestIngestion()
cl.test_ingest_vgt_ndvi_africa()            # ok on 26.03
#cl.test_ingest_msg_mpe_native()             # ok on 26.03
#cl.test_ingest_fewsnet_rfe_africa()         # ok on 26.03
#cl.test_ingest_tamsat_rfe_africa()          # ok on 26.03
#
#cl.test_ingest_amodis_chl_global()          # ok on 26.03
#cl.test_ingest_modis_ba_tile()              # ok on 26.03
#cl.test_ingest_lsasaf_lst()                 # ok on 27.03
#cl.test_ingest_modis_ba_windows()           # ok on 27.03

elapsed = time.clock()-start
print elapsed

exit()
