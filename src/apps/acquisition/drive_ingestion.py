_author__ = "Jurriaan van 't Klooster"

from apps.acquisition import ingestion

import time

start = time.clock()

ingestion.drive_ingestion()

elapsed = time.clock()-start
print elapsed


