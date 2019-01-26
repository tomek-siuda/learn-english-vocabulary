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
        self.elements = []   # type: List[str]
        self.type = None  # type: SectionType
        self.audio = None

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
    section.elements.append(Element(u'{}: {}'.format(ipa.region, ipa.ipa)))
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

