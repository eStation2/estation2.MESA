from apps.es2system.es2system import *
from lib.python.functions import *

settings = getSystemSettings()
role = settings['role']
status = system_db_sync_full(role)
