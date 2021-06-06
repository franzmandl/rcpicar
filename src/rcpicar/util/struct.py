"""
see https://docs.python.org/3/library/struct.html#format-characters
"""
size_map = {
    'c': 1,
    'b': 1,
    'B': 1,
    '?': 1,
    'h': 2,
    'H': 2,
    'i': 4,
    'I': 4,
    'l': 4,
    'L': 4,
    'q': 8,
    'Q': 8,
    'e': 2,
    'f': 4,
    'd': 8,
}


def get_required_size(format_string: str) -> int:
    format_list = list(format_string)
    size = 0
    if format_list[0] == '<':
        format_list.pop(0)
    while len(format_list) != 0:
        size += size_map[format_list.pop(0)]
    return size
