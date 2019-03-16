import oxford
import main_classes
import longman
from main_classes import ParseError


def load_word(word_str):
    """
    :type word_str: str
    :rtype: SectionContainer
    """
    if not word_str.strip():
        raise ParseError('Word is empty.')
    words = longman.load_word(word_str)
    return main_classes.words_to_section_container(words)
