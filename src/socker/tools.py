def base_words(integer):
    """
    Convert a positive integer to a memorable string based on words from
    /usr/share/dict/words.

    :param integer: positive base 10 number
    :type integer: int
    :return: str containing capitalized words
    """
    if integer < 0:
        raise ValueError('base_words does not support negative integers')

    # Save the words in an in-memory cache attached to this method.
    if not hasattr(base_words, 'cache'):
        base_words.cache = words = []
        for word in open('/usr/share/dict/words', 'r'):
            # Filter out plurals, possessive form and conjugations.
            if '\'' not in word:
                words.append(word.strip().capitalize())

    words = base_words.cache

    new_base = len(words)

    result = ''

    current = integer

    while current != 0:
        current, remainder = divmod(current, new_base)
        result += words[remainder]

    return result