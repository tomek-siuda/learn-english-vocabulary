import os
import re

from dict_viewer_plugin import cache
from dict_viewer_plugin.utils import create_variations


class Ipa:
    def __init__(self):
        self.ipa = ''
        self.region = ''
        self.description = ''
        self.audio = None  # type: cache.File


class Sentence:
    def __init__(self):
        self.content = ''
        self.audio = None  # type: cache.File


class Definition:
    def __init__(self):
        self.definition = ''
        self.definition_additional = ''
        self.sentences = []  # type: list[Sentence]


class Word:
    def __init__(self):
        self.word = ''
        self.source = ''
        self.url = ''
        self.pos = ''
        self.pos_additional = ''
        self.ipas = []
        self.definitions = []  # type: list[Definition]


class ParseError(Exception):
    pass


class ClassNotFound(Exception):
    pass


class TooManyClasses(Exception):
    pass


class WordNotFoundError(Exception):
    def __init__(self, message, word=''):
        super(Exception, self).__init__(message)
        self.word = word


class SectionType:
    NAME = 0
    DEFINITION = 1
    SENTENCE = 2
    PRONUNCIATION = 3
    DEFINITION_TYPE = 4


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
        self.audio = None  # type: cache.File
        self.copy_text = False
        self.copy_audio = False
        self.source = ''

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
    section.elements.append(Element(u'{} '.format(ipa.description)))
    section.elements.append(Element(u'{}: '.format(ipa.region), Style.NORMAL))
    if ipa.ipa != '':
        section.elements.append(Element(u'/{}/'.format(ipa.ipa), Style.NORMAL))
    return section


def word_and_pos_to_section(word):
    """
    :type word: Word
    :rtype: Section
    """
    section = Section()
    section.type = SectionType.NAME
    section.elements.append(Element(u'{} '.format(word.word), Style.BOLD))
    section.elements.append(Element(u'{} '.format(word.pos), Style.ITALIC))
    section.elements.append(Element(u'{} '.format(word.pos_additional), Style.ITALIC))
    return section


def definition_to_sections(definition):
    """
    :type definition: Definition
    :rtype: list[Section]
    """
    sections = []

    if definition.definition_additional:
        definition_type_section = Section()
        definition_type_section.type = SectionType.DEFINITION_TYPE
        definition_type_section.elements.append(Element(u'{}'.format(definition.definition_additional), Style.ITALIC))
        sections.append(definition_type_section)

    definition_section = Section()
    definition_section.type = SectionType.DEFINITION
    definition_section.elements.append(Element(u'{}'.format(definition.definition)))
    sections.append(definition_section)

    for sentence in definition.sentences:
        section = Section()
        section.type = SectionType.SENTENCE
        section.elements.append(Element(u'{}'.format(sentence.content)))
        section.audio = sentence.audio
        sections.append(section)

    return sections


def words_to_section_container(words):
    """
    :type words: list of Word
    :rtype: SectionContainer
    """
    container = SectionContainer()
    for word in words:
        sections = []
        sections.append(word_and_pos_to_section(word))
        for ipa in word.ipas:
            sections.append(ipa_to_section(ipa))
        for definition in word.definitions:
            sections.extend(definition_to_sections(definition))
        for section in sections:
            section.source = word.source
        container.sections.extend(sections)
    return container


def add_bold_tags(sentence, words):
    r = re.compile(r'(\s*)((?:\s*\b(?:{})\b)+)'.format('|'.join(words)), re.I)
    return r.sub(r'\1<b>\2</b>', sentence)


def section_container_to_text(section_container, file_saver, word_to_bold):
    """
    :type section_container: SectionContainer
    """
    result = u''
    sections = [s for s in section_container.sections if s.copy_text or s.copy_audio]
    for i, section in enumerate(sections):
        if section.type == SectionType.DEFINITION:
            result += u"<i>{}</i>".format(unicode(section))
        elif section.type == SectionType.SENTENCE:
            result += add_bold_tags(
                unicode(section),
                create_variations(word_to_bold)
            )
        else:
            result += unicode(section)

        if section.copy_audio:
            fname = file_saver(unicode(section.audio.get_absolute_path()))
            result += ' [sound:%s]' % fname

        if i == len(sections) - 1:
            continue
        if section.type == SectionType.DEFINITION_TYPE \
                and sections[i+1].type == SectionType.DEFINITION:
            result += '</br>'
            continue
        if sections[i+1].type == SectionType.DEFINITION \
                and section.type != SectionType.DEFINITION:
            result += '</br></br></br>'
            continue
        result += '</br></br>'

    return result
