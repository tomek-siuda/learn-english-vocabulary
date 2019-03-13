word_dict = {}

with open('files/en_50k 2016.txt') as f:
    i = 1
    for line in f:
        word_dict[line.split()[0]] = i
        i += 1


def get_position(word):
    if word in word_dict:
        return word_dict[word]
    else:
        return -1
