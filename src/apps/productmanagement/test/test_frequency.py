# -*- coding: utf-8 -*-

#
#	purpose: Test dataset functions
#	author:  Marco Beri marcoberi@gmail.com
#	date:	 09.07.2014
#

from __future__ import absolute_import

import unittest

from ..datasets import Frequency
from ..exceptions import (WrongFrequencyValue, WrongFrequencyUnit,
        WrongFrequencyType, WrongFrequencyDateFormat )


class TestFrequency(unittest.TestCase):
    def test_class(self):
        self.assertIsInstance(Frequency(1, Frequency.UNIT.DEKAD, Frequency.TYPE.PER), Frequency)

    def test_wrong_value_1(self):
        self.assertRaises(WrongFrequencyValue, Frequency, *('a', Frequency.UNIT.DEKAD, Frequency.TYPE.PER))

    def test_wrong_unit(self):
        self.assertRaises(WrongFrequencyUnit, Frequency, *(1, '-' + Frequency.UNIT.DEKAD, Frequency.TYPE.PER))

    def test_wrong_type(self):
        self.assertRaises(WrongFrequencyType, Frequency, *(1, Frequency.UNIT.DEKAD, '-' + Frequency.TYPE.PER))

    def test_dataformat_default_1(self):
        frequency =  Frequency(1, Frequency.UNIT.DEKAD, Frequency.TYPE.PER)
        self.assertEqual(frequency.dateformat, Frequency.DATEFORMAT.DATE)

    def test_dataformat_default_2(self):
        frequency =  Frequency(4, Frequency.UNIT.HOUR, Frequency.TYPE.PER)
        self.assertEqual(frequency.dateformat, Frequency.DATEFORMAT.DATETIME)

    def test_wrong_dataformat(self):
        self.assertRaises(WrongFrequencyDateFormat, Frequency, *(4, Frequency.UNIT.HOUR, Frequency.TYPE.PER, '-' + Frequency.DATEFORMAT.DATETIME))
