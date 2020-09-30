# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from lib.python import functions
import unittest
import os
from config import es_constants

__author__ = "Marco Clerici"

from apps.es2system import es2system


class TestSystem(unittest.TestCase):
    systemsettings = functions.getSystemSettings()
    install_type = systemsettings['type_installation'].lower()

    def drive_push_ftp_aruba(self):

        try:
            import apps.es2system.test.aruba_credentials as ac
        except:
            return 1

        # Masked=FALSE means the masked products are pushed.
        status = es2system.push_data_ftp(url=ac.url, user=ac.user, psw=ac.psw, trg_dir=ac.trg_dir, masked=False)
        self.assertEqual(status, 0)

    def drive_push_ftp_jrc(self):

        # Execute w.o. arguments: they are read from config/server_ftp.py
        # The products/versions considered for sync are: the 'activated' ones - except the ones set as 'EXCLUDE' in server_ftp.py definitions
        # Masked=TRUE means the masked sub-products are not pushed (which is the default)

        status = es2system.push_data_ftp(masked=True)
        self.assertEqual(status, 0)


