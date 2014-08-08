import json
from glob import glob

from .tokenizer import DefaultTokenizer


class LazyCorpus(object):

    def __init__(self, tokenizer=None, dictionary=None):
        if not tokenizer:
            self.tokenizer = DefaultTokenizer()
        else:
            self.tokenizer = tokenizer
        if dictionary:
            self.next = self._iter_bow
        self.documents = []

    def __len__(self):
        return len(self._document_list)

    def __iter__(self):
        return self

    def next(self):
        doc = self.extract_doctext(self.documents.next())
        return self.tokenizer.tokenize(doc)

    def _iter_bow(self):
        doc = self.extract_doctext(self.documents.next())
        return self.dictionary.doc2bow(self.tokenizer.tokenize(doc))

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
        self.next = self._iter_bow

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
        super(LazyJSONCorpus, self).__init__(tokenizer)

    def extract_doctext(self, file_loc):
        with open(file_loc, 'r') as file_in:
            data = json.load(file_in)
            text = reduce(dict.get, self.path_to_text.split("."), data)
            return text or ""
