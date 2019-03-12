#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from main_classes import Word
from oxford import parse_html, extract_ipa


class TestOxford(unittest.TestCase):

    def test_parse_html(self):
        with open("test_data/oxford/dog.html") as f:
            data = f.read()
            word = parse_html(data)  # type: Word
            self.assertEqual('dog', word.word)
            self.assertEqual('noun', word.pos)
            self.assertEqual(2, len(word.ipas))

    def test_extract_ipa(self):
        content = u'NAmE//rɪˈmɑːrkəbl//'
        extracted = extract_ipa(content)
        self.assertEqual(u'rɪˈmɑːrkəbl', extracted)

