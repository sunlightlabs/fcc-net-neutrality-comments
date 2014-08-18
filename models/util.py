map_chars = {u'&deg;': u' degree',
             u'&eacute;': u'e',
             u'&frasl;': u'bkslsh',
             u'&lsquo;': u"'",
             u'&lt;': u" lt ",
             u'&mdash;': u" - ",
             u'&Ocirc;': u"O",
             u'&Otilde;': u"O",
             u'&pound;': u"pounds ",
             u'&#8226;': u"",
             u'\xc2\x97': u' - ',
             u'\xc2\x91': u"'",
             u'\xc2\x92': u"'",
             u'\xc2\x93': u'"',
             u'\xc2\x94': u'"',
             u'\xe2\x80\x98': u"'",
             u'\xe2\x80\x99': u"'",
             u'\xe2\x80\x9a': u"'",
             u'\xe2\x80\x9b': u"'",
             u'\xe2\x80\x9c': u'"',
             u'\xe2\x80\x9d': u'"',
             u'\xe2\x80\x9f': u'"',
             u'\xe2\x80\x9e': u'"',
             u'\x60\x60': u'"',
             u'/': u'',
             u'<': u'',
             u'\u2028': u' ',
             u'\xa0': u' ',
             u'\u00A0': u' ',
             u'\u201c': u'"',
             u'\u201d': u'"',
             u'\u2019': u"'",
             u'\t': u' '}


def clean_text(text):
    for s, r in map_chars.iteritems():
        text = text.replace(s, r)
    return text
