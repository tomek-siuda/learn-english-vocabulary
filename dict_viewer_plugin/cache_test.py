import unittest

from dict_viewer_plugin import cache


class TestOxford(unittest.TestCase):
    def test_save_and_open_file(self):
        content = 'abcd'
        cache.save_file(content, 'test.txt')
        self.assertEqual(content, cache.open_file('test.txt'))
        cache.remove_file('test.txt')

    def test_save_when_file_exists(self):
        content = 'abcd'
        cache.save_file(content, 'test.txt')
        with self.assertRaises(cache.FileExistsError):
            cache.save_file(content, 'test.txt')
        cache.remove_file('test.txt')
        
    def test_remove_file(self):
        cache.save_file('abcd', 'testtest.txt')
        cache.remove_file('testtest.txt')
        with self.assertRaises(IOError):
            cache.open_file('testtest.txt')

    def test_download_file(self):
        url = 'https://www.oxfordlearnersdictionaries.com/media/english/us_pron/d/dog/dog__/dog__us_1_rr.mp3'
        content = cache.download_file(url)
        self.assertTrue(len(content) > 1000)
