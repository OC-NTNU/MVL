#!/usr/bin/env python3

from collections import defaultdict


def stand_off_to_inline(text, annot):
    """
    Convert stand-off annotation to inline annotation

    Parameters
    ----------
    text : str
        unannotated text
    annot: list of tuples
        stand-off annotation as tuples in the form (i, j, tag)
        where integers i and j are the start and end character offset,
        and tag is a string for the tag label and - optionally - attributes.

    Returns
    -------
    inline: str
        text in xml format with inline annotation

    Notes
    -----
    Will not detect partly overlapping text spans, which will give rise
    to ill-formed xml.
    """
    # sort on decreasing span size
    annot.sort(key=lambda t: t[1] - t[0], reverse=True)

    # create dict mapping offsets to tags
    offsets2tags = defaultdict(list)

    for start, end, tag in annot:
        offsets2tags[start].append('<{}>'.format(tag))
        offsets2tags[end].insert(0, '</{}>'.format(tag.split()[0]))

    # merge text and tags
    parts = []
    i = None

    for j in sorted(offsets2tags.keys()) + [None]:
        parts.append(text[i:j])
        tags = ''.join(offsets2tags[j])
        parts.append(tags)
        i = j

    return ''.join(parts)


if __name__ == '__main__':
    text = 'Float like a butterfly, sting like a bee.'

    # consecutive spans
    stand_off = [(0, 5, 'a'),
                 (6, 22, 'b'),
                 (24, len(text), 'c')]
    inline = stand_off_to_inline(text, stand_off)
    print(inline)
    assert (inline ==
            '<a>Float</a> <b>like a butterfly</b>, <c>sting like a bee.</c>')

    # embedded spans
    stand_off = [(11, 12, 'a'),
                 (6, 22, 'b'),
                 (0, len(text), 'c')]
    inline = stand_off_to_inline(text, stand_off)
    assert (inline ==
            '<c>Float <b>like <a>a</a> butterfly</b>, sting like a bee.</c>')

    # embedded spans sharing start point
    stand_off = [(6, 10, 'a'),
                 (6, 22, 'b')]
    inline = stand_off_to_inline(text, stand_off)
    assert (inline ==
            'Float <b><a>like</a> a butterfly</b>, sting like a bee.')

    # embedded spans sharing end point
    stand_off = [(13, 22, 'a'),
                 (6, 22, 'b')]
    inline = stand_off_to_inline(text, stand_off)
    assert (inline ==
            'Float <b>like a <a>butterfly</a></b>, sting like a bee.')

    # overlapping spans lead to ill-formed xml
    stand_off = [(6, 22, 'a'),
                 (13, 29, 'b')]
    inline = stand_off_to_inline(text, stand_off)
    assert (inline ==
            'Float <a>like a <b>butterfly</a>, sting</b> like a bee.')

    # adding tags
    stand_off = [(0, 5, 'a x="1"'),
                 (6, 22, 'b'),
                 (24, len(text), 'c y="2"')]
    inline = stand_off_to_inline(text, stand_off)
    assert (inline ==
            '<a x="1">Float</a> <b>like a butterfly</b>, <c y="2">sting like a bee.</c>')
