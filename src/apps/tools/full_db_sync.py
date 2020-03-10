from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from apps.es2system.es2system import *
from lib.python.functions import *

settings = getSystemSettings()
role = settings['role']
status = system_db_sync_full(role)
