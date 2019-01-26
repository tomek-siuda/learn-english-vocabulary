#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib2
import parsing_tools

from main_classes import ParseError, Word, Ipa, WordNotFoundError


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
    return content.split(u'/')[2]


def parse_html(html):
    word_header_class = 'webtop-g'
    name_class = 'h'
    pos_class = 'pos'
    pron_top_class = 'pron-g'
    ipa_class = 'phon'
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

    return word
