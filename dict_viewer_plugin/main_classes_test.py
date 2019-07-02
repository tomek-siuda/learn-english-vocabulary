#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

import main_classes


class TestMainClasses(unittest.TestCase):

    def test_add_bold_tags__simple(self):
        words = ['cat']
        s = 'No one was about except a black and white cat asleep in the sun.'
        expected = 'No one was about except a black and white <b>cat</b> asleep in the sun.'
        self.assertEqual(expected, main_classes.add_bold_tags(s, words))

    def test_add_bold_tags__many_words(self):
        words = ['cat', 'was', 'black']
        s = 'No one was about except a black and white cat asleep in the sun.'
        expected = 'No one <b>was</b> about except a <b>black</b> and white <b>cat</b> asleep in the sun.'
        self.assertEqual(expected, main_classes.add_bold_tags(s, words))
