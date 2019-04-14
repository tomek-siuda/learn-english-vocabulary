#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib2
import parsing_tools
from dict_viewer_plugin import cache

from main_classes import ParseError, ClassNotFound, TooManyClasses, \
    Word, Ipa, WordNotFoundError, Definition, Sentence


def download(url):
    try:
        response = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        if e.code == 404:
            raise WordNotFoundError('')
        raise e
    return response.read()


def load_word(word_str):
    main_url = 'https://www.oxfordlearnersdictionaries.com/definition/english/'
    html = download(main_url + word_str)
    word = try_to_parse_html(html, main_url + word_str)
    word.url = main_url + word_str
    words = [word]
    for i in range(2, 10):
        url = main_url + word_str + '_' + str(i)
        try:
            html = download(url)
        except WordNotFoundError:
            break
        w = try_to_parse_html(html, url)
        w.url = url
        words.append(w)
    return words


def extract_ipa(content):
    # IPA content example: 'NAmE//rɪˈmɑːrkəbl//'
    split = content.split(u'/')
    if len(split) != 5:
        raise ParseError(u'IPA content format has changed. Length after split should be equal to 5.\n'
                         u'Content: ' + content)
    if len(split[2]) == 0:
        raise ParseError(u'IPA is empty.')
    return content.split(u'/')[2]


def try_to_parse_html(html, url):
    try:
        w = parse_html(html)
    except (ParseError, TooManyClasses, ClassNotFound), e:
        e.message += '\nUrl: {}'.format(url)
        raise e
    return w


def parse_html(html):
    word_header_class = 'webtop-g'
    name_class = 'h'
    pos_class = 'pos'
    pron_section_class = 'vp-g'
    pron_top_class = 'pron-g'
    ipa_class = 'phon'
    audio_class = 'sound'
    audio_url_param_name = 'data-src-mp3'
    idioms_parent = 'idm-gs'
    definition_parent_class = 'sn-g'
    definition_class = 'def'
    definition_additional_class = 'gram-g'
    sentence_class = 'x'
    soup = parsing_tools.html_to_soup(html)

    header = parsing_tools.find_single_class(soup, word_header_class)
    word = Word()
    word.source = 'Oxford'
    word.word = parsing_tools.find_single_class(header, name_class).text
    try:
        word.pos = parsing_tools.find_single_class(header, pos_class).string
    except ClassNotFound:
        word.pos = 'undefined'

    prons = parsing_tools.find_all_classes(soup, pron_top_class)
    for pron in prons:
        ipa = Ipa()
        try:
            ipa_content = parsing_tools.find_single_class(pron, ipa_class)
        except ClassNotFound:
            pass
        else:
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
        pron_section = pron.find_parent(class_=pron_section_class)
        if pron_section:
            description_words = pron_section.find(class_='vp').text.split(' ')
            description_words[-1] = '<b>' + description_words[-1] + '</b>'
            ipa.description = ' '.join(description_words)
        word.ipas.append(ipa)

    # remove idiom div, it also has definitions we don't need
    idiom_div = soup.find(class_=idioms_parent)
    if idiom_div:
        idiom_div.decompose()
    definitions = parsing_tools.find_all_classes(soup, definition_parent_class)
    for def_parent in definitions:
        definition = Definition()
        try:
            definition_header = parsing_tools.find_single_class(
                def_parent, definition_class)
        except ClassNotFound:
            # Probably a link to some other page
            continue

        definition.definition = definition_header.text
        try:
            definition.definition_additional = parsing_tools.find_single_class(
                def_parent, definition_additional_class)
        except ClassNotFound:
            definition.definition_additional = ''

        sentences = def_parent.find_all(class_=sentence_class)
        for s in sentences:
            sentence = Sentence()
            sentence.content = s.text
            definition.sentences.append(sentence)

        word.definitions.append(definition)

    return word
