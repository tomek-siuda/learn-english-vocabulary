import unittest

from main_classes import Word
from oxford import parse_html


class TestOxford(unittest.TestCase):

    def test_parse_html(self):
        with open("test_data/oxford/dog.html") as f:
            data = f.read()
            word = parse_html(data)  # type: Word
            self.assertEqual('dog', word.word)
            self.assertEqual('noun', word.pos)
            print str(word.ipas)
            self.assertEqual(2, len(word.ipas))
