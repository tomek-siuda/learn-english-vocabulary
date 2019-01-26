from dict_viewer_plugin.main_classes import ParseError


def load_word(word):
    """
    :type word: str
    :rtype: SectionContainer
    """
    if not word.strip():
        raise ParseError('Word is empty.')

