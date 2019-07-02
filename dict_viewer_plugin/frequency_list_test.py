#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import frequency_list


class TestFrequencyList(unittest.TestCase):

    def test_get_position(self):
        self.assertEqual(1, frequency_list.get_position('you'))
        self.assertEqual(3, frequency_list.get_position('the'))
        self.assertEqual(208, frequency_list.get_position('every'))
        self.assertEqual(48194, frequency_list.get_position('belie'))
        self.assertEqual(-1, frequency_list.get_position('sdfgdfhdghh'))

    def test_get_position__unicode(self):
        self.assertEqual(1, frequency_list.get_position(u'you'))
        self.assertEqual(3, frequency_list.get_position(u'the'))
        self.assertEqual(208, frequency_list.get_position(u'every'))
        self.assertEqual(48194, frequency_list.get_position(u'belie'))


