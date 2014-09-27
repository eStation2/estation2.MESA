_author__ = "Marco Clerici"

from apps.acquisition import get_internet

import time

start = time.clock()

get_internet.drive_get_internet()

elapsed = time.clock()-start
print elapsed


