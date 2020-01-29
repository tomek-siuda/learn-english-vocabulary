import os
import io

word_dict = {}
word_dict_lemmatized = {}

with io.open(os.path.join(os.path.dirname(__file__), "files", "en_50k 2016.txt"),
          encoding="utf8") as f:
    i = 1
    for line in f:
        word_dict[line.split()[0]] = i
        i += 1

with io.open(os.path.join(os.path.dirname(__file__), "files", "en_50k 2016_lemmatized.txt"),
          encoding="utf8") as f:
    i = 1
    for line in f:
        word_dict_lemmatized[line.strip()] = i
        i += 1

def get_position(word, lemmatized=False):
    d = word_dict
    if lemmatized:
        d = word_dict_lemmatized
    if word in d:
        return d[word]
    else:
        return -1
