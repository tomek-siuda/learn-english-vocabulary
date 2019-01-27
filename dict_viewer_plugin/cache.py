import os
import random
import urllib2


class FileExistsError(Exception):
    pass


def random_string(length):
    pool = '0123456789abcdef'
    return ''.join(random.choice(pool) for i in xrange(length))


def create_path(filename):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache', filename)


def save_file(content, filename):
    path = create_path(filename)
    if os.path.isfile(path):
        raise FileExistsError()
    with open(path, "wb") as f:
        f.write(content)


def open_file(filename):
    path = create_path(filename)
    with open(path, "rb") as f:
        content = f.read()
    return content


def remove_file(filename):
    path = create_path(filename)
    os.remove(path)


def download_file(url):
    response = urllib2.urlopen(url)
    content = response.read()
    return content


class File:
    def __init__(self, url, extension):
        """
        :type url: str
        :type extension: str
        """
        self.url = url
        self.extension = extension
        self.ready = False
        self.absolute_path = None

    def get_absolute_path(self):
        if self.ready:
            return self.absolute_path

        content = download_file(self.url)

        for i in range(0, 10):
            filename = random_string(24) + '.' + self.extension
            try:
                save_file(content, filename)
            except FileExistsError:
                pass
            else:
                self.ready = True
                self.absolute_path = create_path(filename)
                break

        if not self.ready:
            raise RuntimeError("Can't save a file.")

        return self.absolute_path
