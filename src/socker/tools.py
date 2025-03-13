def to_base(integer, base_list=None):
    """
    Convert an integer to an arbitrarily-represented arbitrary-base number
    system.

    The base representation must be defined in the `base list` parameter.
    The base is taken from the length of the list.

    :param integer: Base 10 int()
    :type integer: int()
    :param base_list: A list defining the order and number of representations.
    :type base_list: A list-like object. Needs to support len() and indexing.
    :return: A representation of the integer in the defined base.
    :rtype: str()

    Example:

    >>> # Hexadecimal
    >>> to_base(255, '0123456789abcdef')
    'ff'
    >>> # Base 62
    >>> to_base(99999999999999999999999999999999999999999999999,
    ...         '0123456789'
    ...         'abcdefghijklmnopqrstuvwxyz'
    ...         'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    '2uXfZBR6CN4F4MmXncUdm8QszFB'
    >>> # Base 10 capitalized word representation
    >>> to_base(13371234567890,
    ...         ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven',
    ...          'Eight', 'Nine'])
    'OneThreeThreeSevenOneTwoThreeFourFiveSixSevenEightNineZero'
    >>> # This one is not very useful, but possible
    >>> to_base(1337, ['', 'l', '', 'e', '', '', '', 't', '', ''])
    'leet'
    >>> # Simple custom base conversion function using partial
    >>> from functools import partial
    >>> to_binary_capitalized_words = partial(to_base,
    ...                                       base_list=['Zero', 'One'])
    >>> to_binary_capitalized_words(42)
    'OneZeroOneZeroOneZero'
    """
    if base_list is None:
        raise ValueError("base_list is not defined")

    new_base = len(base_list)

    result = []

    current = integer

    while current != 0:
        current, remainder = divmod(current, new_base)
        result.append(base_list[remainder])

    return "".join(reversed(result))


def base_words(integer):
    """
    Convert a positive integer to a memorable string based on words from
    /usr/share/dict/words.

    :param integer: positive base 10 number
    :type integer: int()
    :return: ConcatenatedCapitalizedWords
    :rtype: str()
    """
    if integer < 0:
        raise ValueError("base_words does not support negative integers")

    # Save the words in an in-memory cache attached to this method.
    if not hasattr(base_words, "cache"):
        words = []
        for word in open("/usr/share/dict/words", "r"):
            # Filter out plurals, possessive form and conjugations.
            if "'" not in word:
                words.append(word.strip().capitalize())

        base_words.cache = list(sorted(set(words)))

    words = base_words.cache

    return to_base(integer, words)
