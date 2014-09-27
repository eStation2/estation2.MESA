_author__ = "Marco Clerici"

from apps.acquisition import get_eumetcast

import time

start = time.clock()

get_eumetcast.drive_eumetcast()

elapsed = time.clock()-start
print elapsed


