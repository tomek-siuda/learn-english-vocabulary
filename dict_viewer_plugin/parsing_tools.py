from main_classes import ParseError


def find_all_classes(soup, class_name, expected_length=0):
    result = soup.find_all(class_=class_name)
    if len(result) == 0:
        raise ParseError("Can't find a class '{}'".format(class_name))
    if expected_length > 0 and len(result) != expected_length:
        raise ParseError("Too many classes '{}'".format(class_name))
    return result


def find_single_class(soup, class_name):
    return find_all_classes(soup, class_name, 1)[0]
