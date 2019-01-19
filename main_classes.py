class Ipa:
    def __init__(self):
        self.ipa = ''
        self.region = ''


class Word:
    def __init__(self):
        self.word = ''
        self.pos = ''
        self.ipas = []


class ParseError(Exception):
    pass


class WordNotFoundError(Exception):

    def __init__(self, message, word):
        super(Exception, self).__init__(message)
        self.word = word
