from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
_author__ = "Marco Clerici"

#
#   Main module in acquisition, driving the services
#

from apps.acquisition import get_eumetcast
from apps.acquisition import get_internet
from apps.acquisition import ingestion
from lib.python import functions

from lib.python.daemon import DaemonDryRunnable

class IngestionDaemon(DaemonDryRunnable):
    def run(self):
        ingestion.loop_ingestion(dry_run=self.dry_run)


class GetEumetcastDaemon(DaemonDryRunnable):
    def run(self):
        systemsettings = functions.getSystemSettings()
        # Special case for mesa-proc @ JRC
        if systemsettings['type_installation'] == 'Server':
            get_eumetcast.loop_eumetcast(dry_run=self.dry_run)
        else:
            get_eumetcast.loop_eumetcast_ftp(dry_run=self.dry_run)

class GetInternetDaemon(DaemonDryRunnable):
    def run(self):
        get_internet.loop_get_internet(dry_run=self.dry_run)


