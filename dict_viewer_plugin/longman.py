#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib2
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
sentence_class = 'EXAMPLE'
sentence_audio_class = 'exafile'
audio_url_param_name = 'data-src-mp3'


def load_word(word):
    url = 'https://www.ldoceonline.com/dictionary/'
    url += word
    try:
        response = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
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
    audio_url_param_name = 'data-src-mp3'

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
            def_parent, definition_class).text
    except ClassNotFound:
        # Can't find the definition, it's probably just a link to another page
        return
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
        try:
            word_object.pos = parsing_tools.find_single_class(word_head, pos_class).string.strip()
        except ClassNotFound:
            word_object.pos = ''
        try:
            word_object.pos_additional = parsing_tools\
                .find_single_class(word_head, pos_additional_class).text.strip()
        except ClassNotFound:
            word_object.pos_additional = ''

        word_object.ipas.append(extract_ipa(word_head, 'br'))
        word_object.ipas.append(extract_ipa(word_head, 'us'))

        definitions = parsing_tools.find_all_classes(word, definition_parent_class)
        for def_parent in definitions:
            subdefinitions = def_parent.find_all(class_=subdefinition_parent_class)
            if subdefinitions:
                for subdef in subdefinitions:
                    extract_definition(subdef, word_object)
            else:
                extract_definition(def_parent, word_object)

        word_objects.append(word_object)

    return word_objects
