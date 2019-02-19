#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib2
import parsing_tools
from dict_viewer_plugin import cache

from main_classes import ParseError, Word, Ipa, WordNotFoundError, Definition, Sentence


def load_word(word):
    url = 'https://www.oxfordlearnersdictionaries.com/definition/english/'
    url += word
    try:
        response = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        if e.code == 404:
            raise WordNotFoundError('', word)
    html = response.read()
    return parse_html(html)


def extract_ipa(content):
    # IPA content example: 'NAmE//rɪˈmɑːrkəbl//'
    split = content.split(u'/')
    if len(split) != 5:
        raise ParseError(u'IPA content format has changed. Length after split should be equal to 5.\n'
                         u'Content: ' + content)
    if len(split[2]) == 0:
        raise ParseError(u'IPA is empty.')
    return content.split(u'/')[2]


def parse_html(html):
    word_header_class = 'webtop-g'
    name_class = 'h'
    pos_class = 'pos'
    pron_top_class = 'pron-g'
    ipa_class = 'phon'
    audio_class = 'sound'
    audio_url_param_name = 'data-src-mp3'
    idioms_parent = 'idm-gs'
    definition_parent_class = 'sn-g'
    definition_class = 'def'
    sentence_class = 'x'
    soup = BeautifulSoup(html, 'html.parser')

    header = parsing_tools.find_single_class(soup, word_header_class)
    word = Word()
    word.word = parsing_tools.find_single_class(header, name_class).string
    word.pos = parsing_tools.find_single_class(header, pos_class).string

    prons = parsing_tools.find_all_classes(soup, pron_top_class)
    for pron in prons:
        ipa = Ipa()
        ipa_content = parsing_tools.find_single_class(pron, ipa_class)
        ipa.ipa = extract_ipa(ipa_content.text)
        audio_div = parsing_tools.find_single_class(pron, audio_class)
        audio_url = audio_div[audio_url_param_name]
        ipa.audio = cache.File(audio_url, 'mp3')
        try:
            geo = pron['geo']
        except KeyError:
            raise ParseError("Can't find 'geo' attribute in a pronunciation class {}".format(str(pron)))
        if 'br' in geo and 'am' in geo:
            raise ParseError("Can't decide if IPA is UK or US, geo name: '{}'".format(geo))
        if 'br' in geo:
            ipa.region = 'BR'
        elif 'am' in geo:
            ipa.region = 'US'
        else:
            raise ParseError("Can't decide if IPA is UK or US, geo name: '{}'".format(geo))
        word.ipas.append(ipa)

    # remove idiom div, it also has definitions we don't need
    parsing_tools.find_single_class(soup, idioms_parent).decompose()
    definitions = parsing_tools.find_all_classes(soup, definition_parent_class)
    for def_parent in definitions:
        definition = Definition()
        definition_header = parsing_tools.find_single_class(
            def_parent, definition_class)
        definition.definition = definition_header.text

        sentences = def_parent.find_all(class_=sentence_class)
        for s in sentences:
            sentence = Sentence()
            sentence.content = s.text
            definition.sentences.append(sentence)

        word.definitions.append(definition)

    return word
