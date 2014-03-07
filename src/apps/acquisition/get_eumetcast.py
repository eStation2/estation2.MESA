#
#	purpose: Define the get_eumetcast service
#	author:  M.Clerici
#	date:	 19.02.2014
#   descr:	 Reads the definition from eStation DB and execute the copy to local disk
#	history: 1.0

import sys
sys.path.append('/srv/www/eStation2/config/')

# eStation2 base definitions
import es2
logger=es2.log.myLogger(__name__)
print es2.baseDir