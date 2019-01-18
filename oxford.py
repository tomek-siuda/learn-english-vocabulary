from bs4 import BeautifulSoup
import urllib2
import parsing_tools

from main_classes import ParseError, Word, Ipa


def load_word(word):
    url = 'https://www.oxfordlearnersdictionaries.com/definition/english/'
    url += word
    response = urllib2.urlopen(url)
    html = response.read()
    return parse_html(html)


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
    print len(prons)
    for pron in prons:
        ipa = Ipa()
        ipa.ipa = parsing_tools.find_single_class(pron, ipa_class).string
        word.ipas.append(ipa)

    return word