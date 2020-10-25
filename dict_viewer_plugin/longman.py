#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:
    # Fall back to Python 2
    from urllib2 import urlopen
    from urllib2 import HTTPError
    from urllib2 import Request
import parsing_tools
import cache

from main_classes import ParseError, ClassNotFound, TooManyClasses, \
    Word, Ipa, WordNotFoundError, Definition, Sentence


word_section_class = 'dictentry'
word_head_class = 'Head'  # comprises Word, POS, IPA
name_class = 'HYPHENATION'
pos_class = 'POS'
pos_additional_class = 'GRAM'
definition_parent_class = 'Sense'
subdefinition_parent_class = 'Subsense'
definition_class = 'DEF'
definition_additional_class = 'GRAM'
definition_geo_class = 'GEO'
definition_register_class = 'REGISTERLAB'
sentence_class = 'EXAMPLE'
sentence_audio_class = 'exafile'
audio_url_param_name = 'data-src-mp3'
crossref_class = 'Crossref'


def load_word(word):
    word = '-'.join(word.split())
    url = 'https://www.ldoceonline.com/dictionary/'
    url += word
    try:
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = {'User-Agent': user_agent}
        r = Request(url, headers=headers)
        response = urlopen(r)
    except HTTPError as e:
        if e.code == 404:
            raise WordNotFoundError('', word)
    html = response.read()
    words = parse_html(html)
    for word in words:
        word.url = url
    return words


def valid(soup):
    links = soup.find_all('link', rel='canonical')
    if len(links) != 1:
        raise ParseError("Unexpected count of links with 'canonical' rel. Count: {}".format(len(links)))
    href = links[0]['href']
    if 'www.ldoceonline.com/spellcheck/' in href:
        raise WordNotFoundError("Can't find the word")
    return True


def extract_ipa(word_soup, region):
    ipa_class = 'PronCodes'
    br_ipa_audio_class = 'brefile'
    us_ipa_audio_class = 'amefile'
    inflections_class = 'Inflections'
    audio_url_param_name = 'data-src-mp3'

    # remove inflections (say -> said, says)
    # they contain only IPA without any audio
    inflections = word_soup.find(class_=inflections_class)
    if inflections:
        inflections.decompose()

    if region == 'br':
        audio_class = br_ipa_audio_class
    else:
        audio_class = us_ipa_audio_class

    ipa = Ipa()
    ipa.region = region
    try:
        ipa.ipa = parsing_tools.find_single_class(word_soup, ipa_class).text.strip().replace(u'/', '')
    except ClassNotFound:
        ipa.ipa = ''
    try:
        audio_div = parsing_tools.find_single_class(word_soup, audio_class)
    except ClassNotFound:
        return ipa
    audio_url = audio_div[audio_url_param_name]
    ipa.audio = cache.File(audio_url, 'mp3')
    return ipa


def extract_definition(def_parent, word_object):
    definition = Definition()
    try:
        definition.definition = parsing_tools.find_single_class(
            def_parent, definition_class).text.strip()
    except ClassNotFound:
        # Can't find the definition, it's probably just a link to another page
        return

    registers = []
    register_divs = def_parent.find_all(class_=definition_register_class)
    for register_div in register_divs:
        registers.append('[{}]'.format(register_div.text.strip()))
    if len(registers) > 0:
        definition.definition = ' '.join(registers) + ' ' + definition.definition

    geo = def_parent.find(class_=definition_geo_class)
    if geo:
        definition.definition = '[{}] '.format(geo.text.strip()) + definition.definition

    try:
        definition.definition_additional = parsing_tools.find_single_class(
            def_parent, definition_additional_class).text
    except ClassNotFound:
        definition.definition_additional = ''

    sentences = def_parent.find_all(class_=sentence_class)
    for s in sentences:
        sentence = Sentence()
        sentence.content = s.text.strip()
        audio = s.find(class_=sentence_audio_class)
        if audio:
            audio_url = audio[audio_url_param_name]
            sentence.audio = cache.File(audio_url, 'mp3')
        definition.sentences.append(sentence)

    word_object.definitions.append(definition)


def parse_html(html):
    soup = parsing_tools.html_to_soup(html)
    valid(soup)
    word_objects = []

    words = soup.find_all(class_=word_section_class)
    if len(words) == 0:
        raise ParseError("Can't find any '{}' classes.".format(word_section_class))
    for word in words:
        word_head = parsing_tools.find_single_class(word, word_head_class)
        word_object = Word()
        word_object.source = 'Longman'
        if word.find(class_='bussdictEntry'):
            word_object.source = 'Longman Business'
        word_object.word = parsing_tools.find_single_class(word_head, name_class).string.replace(u'‧', u'')

        pos = word_head.find_all(class_=pos_class)
        if len(pos) > 0:
            word_object.pos = ', '.join([p.text.replace(',', '').strip() for p in pos])
        else:
            word_object.pos = ''

        try:
            word_object.pos_additional = parsing_tools\
                .find_single_class(word_head, pos_additional_class).text.strip()
        except ClassNotFound:
            word_object.pos_additional = ''

        word_object.ipas.append(extract_ipa(word_head, 'br'))
        word_object.ipas.append(extract_ipa(word_head, 'us'))

        try:
            definitions = parsing_tools.find_all_classes(word, definition_parent_class)
        except ClassNotFound:
            pass
        else:
            for def_parent in definitions:
                cross_refs = soup.find_all(class_=crossref_class)
                for cr in cross_refs:
                    cr.decompose()

                subdefinitions = def_parent.find_all(class_=subdefinition_parent_class)
                if subdefinitions:
                    for subdef in subdefinitions:
                        extract_definition(subdef, word_object)
                else:
                    extract_definition(def_parent, word_object)

        word_objects.append(word_object)

    return word_objects
