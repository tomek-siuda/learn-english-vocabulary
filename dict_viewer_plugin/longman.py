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
    return html


def valid(soup):
    links = soup.find_all('link', rel='canonical')
    if len(links) != 1:
        raise ParseError("Unexpected count of links with 'canonical' rel. Count: {}".format(len(links)))
    href = links[0]['href']
    if 'www.ldoceonline.com/spellcheck/' in href:
        raise WordNotFoundError("Can't find the word")
    return True


