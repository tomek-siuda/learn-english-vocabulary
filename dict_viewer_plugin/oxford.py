#!/usr/bin/python
# -*- coding: utf-8 -*-
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:
    # Fall back to Python 2
    from urllib2 import urlopen
    from urllib2 import HTTPError
from bs4 import BeautifulSoup
import parsing_tools
from dict_viewer_plugin import cache

from main_classes import ParseError, ClassNotFound, TooManyClasses, \
    Word, Ipa, WordNotFoundError, Definition, Sentence


def download(url):
    try:
        response = urlopen(url)
    except HTTPError as e:
        if e.code == 404:
            raise WordNotFoundError('')
        raise e
    return response.read()


def load_word(word_str):
    word_str = '-'.join(word_str.split())
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
    return content.split(u'/')[1]

def try_to_parse_html(html, url):
    try:
        w = parse_html(html)
    except (ParseError, TooManyClasses, ClassNotFound) as e:
        e.message += '\nUrl: {}'.format(url)
        raise e
    return w


def parse_html(html):
    top_container_class = 'webtop'
    name_class = 'headword'
    pos_class = 'pos'
    pos_additional_classes = ['labels', 'inflections', 'variants']
    verb_form_root_class = 'verb_form'
    verb_form_description_class = 'verb_form'
    pron_top_class = 'phonetics'
    ipa_class = 'phon'
    audio_class = 'sound'
    audio_url_param_name = 'data-src-mp3'
    idioms_parent = 'idioms'
    definition_parent_class = 'sense'
    definition_class = 'def'
    definition_additional_class = 'grammar' # "uncountable", etc
    definition_label_class = 'labels'  # "informal", "especially north american", etc
    sentence_class = 'x'
    collapse_class = 'collapse'
    synonyms_title = 'Synonyms'
    collocations_title = 'Collocations'
    soup = parsing_tools.html_to_soup(html)

    # there are many class with this name, get the first one
    top_container = soup.find(class_=top_container_class)
    word = Word()
    word.source = 'Oxford'
    word.word = parsing_tools.find_single_class(top_container, name_class).text
    try:
        word.pos = parsing_tools.find_single_class(top_container, pos_class).string
    except ClassNotFound:
        word.pos = 'undefined'

    pos_additionals = []
    for c in pos_additional_classes:
        pos_additional = top_container.find(class_=c, recursive=False)
        if pos_additional:
            pos_additionals.append(pos_additional.text.replace('(', '[').replace(')', ']'))

    word.pos_additional = ' '.join(pos_additionals)

    try:
        pron_collections = parsing_tools.find_all_classes(top_container, pron_top_class)
    except ClassNotFound:
        pass
    else:
        for pron_collection in pron_collections:
            prons = pron_collection.find_all('div', recursive=False)
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
                pron_section = pron.find_parent(class_=verb_form_root_class)
                if pron_section:
                    description_words = pron_section.find(class_=verb_form_description_class).text.split(' ')
                    description_words[-1] = '<b>' + description_words[-1] + '</b>'
                    ipa.description = ' '.join(description_words)
                word.ipas.append(ipa)

    # remove idiom div, it also has definitions we don't need
    idiom_div = soup.find(class_=idioms_parent)
    if idiom_div:
        idiom_div.decompose()
    try:
        definitions = parsing_tools.find_all_classes(soup, definition_parent_class)
    except ClassNotFound:
        pass
    else:
        for def_parent in definitions:
            definition = Definition()
            try:
                definition_header = parsing_tools.find_single_class(
                    def_parent, definition_class)
            except ClassNotFound:
                # Probably a link to some other page
                continue
            definition.definition = definition_header.text

            # remove synonyms etc., they can have labels we don't need
            collapsed = soup.find_all(class_=collapse_class)
            for c in collapsed:
                c.decompose()

            label = def_parent.find(class_=definition_label_class)
            if label and len(label.text.strip())>0:
                definition.definition = label.text.replace('(', '[').replace(')', ']') \
                                        + ' ' + definition.definition

            try:
                definition.definition_additional = parsing_tools.find_single_class(
                    def_parent, definition_additional_class).text
            except ClassNotFound:
                definition.definition_additional = ''

            sentences = def_parent.find_all(class_=sentence_class)
            for s in sentences:
                sentence = Sentence()
                sentence.content = s.text
                definition.sentences.append(sentence)

            word.definitions.append(definition)

    return word
