# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from config import es_constants

__author__ = "Jurriaan van 't Klooster"

from apps.es2system import es2system



class TestSystem(unittest.TestCase):
    def test_manage_lock(self):

        # Check the management of the lock files
        lock_id = 'test_operation'
        # Delete all existing locks
        status = es2system.system_manage_lock('All_locks', 'Delete')
        self.assertEquals(status, 0)

        # Check a (not existing) lock
        status = es2system.system_manage_lock(lock_id, 'Check')
        self.assertEquals(status, 0)

        # Create a lock
        status = es2system.system_manage_lock(lock_id, 'Create')
        self.assertEquals(status, 0)

        # Check an (existing) lock
        status = es2system.system_manage_lock(lock_id, 'Check')
        self.assertEquals(status, 1)
