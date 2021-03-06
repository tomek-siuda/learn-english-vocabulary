import oxford
import main_classes
import longman
from main_classes import ParseError, ClassNotFound, TooManyClasses, WordNotFoundError, Word
from aqt.utils import showInfo, showWarning


def load_word(word_str):
    """
    :type word_str: str
    :rtype: list of Word
    """
    if not word_str.strip():
        raise ParseError('Word is empty.')
    words = []
    words.extend(load_from_dict(oxford, word_str, 'Oxford'))
    words.extend(load_from_dict(longman, word_str, 'Longman'))
    if len(words) == 0:
        raise WordNotFoundError('')

    def comparator(a, b):
        if a == '':
            return 1
        if b == '':
            return -1
        if a < b:
            return -1
        else:
            return 1

    words.sort(key=lambda w: w.pos, cmp=comparator)
    return words


def load_from_dict(module, word, module_name):
    words = []
    try:
        words.extend(module.load_word(word))
    except (ParseError, ClassNotFound, TooManyClasses), e:
        showWarning('{} parsing error: {}'.format(module_name, e.message))
    except WordNotFoundError, e:
        showWarning('{} word not found'.format(module_name, e.message))
    return words
