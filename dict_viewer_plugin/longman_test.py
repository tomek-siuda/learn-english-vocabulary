#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import parsing_tools
import longman
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

    def test_parse_html(self):
        with open("test_data/longman/dog.html") as f:
            data = f.read()
            word = longman.parse_html(data)  # type: Word
            self.assertEqual('dog', word.word)
            self.assertEqual('noun', word.pos)
