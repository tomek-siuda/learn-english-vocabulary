def create_variations(word):
    variations = [
        word,
        word + 's',
        word + 'ing',
        word[:-1] + 'ing', # 'ride' -> riding
        word + 'ed',
        word + 'd',
        word + word[-1] + 'ing', # 'cut' -> 'cutting'
    ]
    if word[-1] == 'd':
        variations.append(word[:-1] + 't') # 'build' -> 'built'
    return variations