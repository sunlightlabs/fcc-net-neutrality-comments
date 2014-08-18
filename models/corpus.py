import json
from glob import glob

from .tokenizer import DefaultTokenizer


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
             u'\u2019': u"'"}


def clean_text(text):
    for s, r in map_chars.iteritems():
        text = text.replace(s, r)
    return text


class LazyCorpus(object):

    def __init__(self, tokenizer=None, dictionary=None):
        if not tokenizer:
            self.tokenizer = DefaultTokenizer()
        else:
            self.tokenizer = tokenizer
        if dictionary:
            self.dictionary = dictionary
            self.return_doctext = self._return_bow
        else:
            self.return_doctext = self._return_tokens
        self.documents = []

    def __len__(self):
        return len(self._document_list)

    def __iter__(self):
        for doc in self.documents:
            doctext = self.extract_doctext(doc)
            yield self.return_doctext(doctext)

    def _return_tokens(self, doctext):
        return self.tokenizer.tokenize(doctext)

    def _return_bow(self, doctext):
        return self.dictionary.doc2bow(self.tokenizer.tokenize(doctext))

    def extract_doctext(self, file_loc):
        raise NotImplementedError

    @property
    def documents(self):
        return self._document_iter

    @documents.setter
    def documents(self, list_of_file_locs):
        self._document_list = list_of_file_locs
        self._document_iter = iter(self._document_list)

    @documents.deleter
    def documents(self):
        del self._document_list

    @property
    def dictionary(self):
        return self._dictionary

    @dictionary.setter
    def dictionary(self, new_dictionary):
        self._dictionary = new_dictionary
        self.return_doctext = self._return_bow

    @property
    def tokenizer(self):
        return self._tokenizer

    @tokenizer.setter
    def tokenizer(self, new_tokenizer):
        self._tokenizer = new_tokenizer

    @tokenizer.deleter
    def tokenizer(self):
        del self._tokenizer

    def glob_documents(self, path_glob_pattern):
        self.documents = glob(path_glob_pattern)

    def rewind(self):
        self._document_iter = iter(self._document_list)


class LazyJSONCorpus(LazyCorpus):

    def __init__(self, tokenizer=None, dictionary=None, path_to_text='text'):
        self.path_to_text = path_to_text
        super(LazyJSONCorpus, self).__init__(tokenizer, dictionary)

    def extract_doctext(self, file_loc):
        with open(file_loc, 'r') as file_in:
            data = json.load(file_in)
            text = reduce(dict.get, self.path_to_text.split("."), data)
            cleaned_text = clean_text(text)
            return cleaned_text or ""
