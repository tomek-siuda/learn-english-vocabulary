from dict_viewer_plugin import oxford, main_classes
from dict_viewer_plugin.main_classes import ParseError


def load_word(word_str):
    """
    :type word_str: str
    :rtype: SectionContainer
    """
    if not word_str.strip():
        raise ParseError('Word is empty.')
    word = oxford.load_word(word_str)
    return main_classes.word_to_section_container(word)
