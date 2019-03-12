#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib2
import parsing_tools
import cache

from main_classes import ParseError, Word, Ipa, WordNotFoundError, Definition, Sentence


def load_word(word):
    url = 'https://www.ldoceonline.com/dictionary/'
    url += word
    try:
        response = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        if e.code == 404:
            raise WordNotFoundError('', word)
    html = response.read()
    return parse_html(html)


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
    ipa.ipa = parsing_tools.find_single_class(word_soup, ipa_class).text.strip()
    audio_div = parsing_tools.find_single_class(word_soup, audio_class)
    audio_url = audio_div[audio_url_param_name]
    ipa.audio = cache.File(audio_url, 'mp3')
    ipa.region = region
    return ipa


def parse_html(html):
    word_section_class = 'dictentry'
    name_class = 'HYPHENATION'
    pos_class = 'POS'
    definition_parent_class = 'Sense'
    definition_class = 'DEF'
    sentence_class = 'EXAMPLE'
    sentence_audio_class = 'exafile'
    audio_url_param_name = 'data-src-mp3'

    soup = parsing_tools.html_to_soup(html)
    valid(soup)
    word_object = Word()

    words = soup.find_all(class_=word_section_class)
    if len(words) == 0:
        raise ParseError("Can't find any '{}' classes.".format(word_section_class))
    word = words[0]
    word_object.word = parsing_tools.find_single_class(word, name_class).string
    word_object.pos = parsing_tools.find_single_class(word, pos_class).string.strip()

    word_object.ipas.append(extract_ipa(word, 'br'))
    word_object.ipas.append(extract_ipa(word, 'us'))

    definitions = parsing_tools.find_all_classes(word, definition_parent_class)
    for def_parent in definitions:
        definition = Definition()
        try:
            definition.definition = parsing_tools.find_single_class(
                def_parent, definition_class).text
        except ParseError:
            # Can't find the definition, it's probably just a link to another page
            continue

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

    return word_object



