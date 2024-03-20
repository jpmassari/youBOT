def remove_non_bmp_characters(text):
    #return ''.join(char for char in text if unicodedata.category(char) != 'So')
    return ''.join(char for char in text if (ord(char) <= 0xFFFF) or char.isspace())
