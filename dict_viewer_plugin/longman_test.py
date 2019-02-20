#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from dict_viewer_plugin import parsing_tools, longman
from main_classes import WordNotFoundError


class TestLongman(unittest.TestCase):

    def test_valid__word_not_found_should_rise(self):
        with open("test_data/longman/not_found.html") as f:
            data = f.read()
        soup = parsing_tools.html_to_soup(data)
        with self.assertRaises(WordNotFoundError):
            longman.valid(soup)

    def test_valid__ok(self):
        with open("test_data/longman/dog.html") as f:
            data = f.read()
        soup = parsing_tools.html_to_soup(data)
        self.assertTrue(longman.valid(soup))
