import os

from dict_viewer_plugin import cache


class Ipa:
    def __init__(self):
        self.ipa = ''
        self.region = ''
        self.audio = None  # type: cache.File


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


class SectionType:
    DEFINITION = 1
    SENTENCE = 2
    PRONUNCIATION = 3


class Style:
    NORMAL = 1
    BOLD = 2
    ITALIC = 3


class Element:
    def __init__(self, text, style=Style.NORMAL):
        self.style = style  # type: Style
        self.text = text

    def __unicode__(self):
        if self.style == Style.NORMAL:
            return self.text
        if self.style == Style.BOLD:
            return u'<b>{}</b>'.format(self.text)
        if self.style == Style.ITALIC:
            return u'<i>{}</i>'.format(self.text)


class Section:
    def __init__(self):
        self.elements = []   # type: List[Element]
        self.type = None  # type: SectionType
        self.audio = None
        self.copy_text = False
        self.copy_audio = False

    def __unicode__(self):
        result = u''
        for element in self.elements:
            result += unicode(element)
        return result


class SectionContainer:
    def __init__(self):
        self.sections = []  # type: List[Section]


def ipa_to_section(ipa):
    """
    :type ipa: Ipa
    :rtype: Section
    """
    section = Section()
    section.type = SectionType.PRONUNCIATION
    section.audio = ipa.audio
    section.elements.append(Element(u'{}: '.format(ipa.region), Style.NORMAL))
    section.elements.append(Element(u'/{}/'.format(ipa.ipa), Style.NORMAL))
    return section


def word_to_section_container(word):
    """
    :type word: Word
    :rtype: SectionContainer
    """
    container = SectionContainer()
    for ipa in word.ipas:
        container.sections.append(ipa_to_section(ipa))
    return container


def section_container_to_text(section_container):
    """
    :type section_container: SectionContainer
    """
    result = u''
    for section in section_container.sections:
        if section.copy_text:
            result += unicode(section)
            result += '</br></br>'
    return result
