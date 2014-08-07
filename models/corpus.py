import json
from glob import glob

from gensim.corpora import Dictionary

from .tokenizer import DefaultTokenizer


class LazyCorpus(object):

    def __init__(self, tokenizer=None):
        if not tokenizer:
            self.tokenizer = DefaultTokenizer()
        else:
            self.tokenizer = tokenizer
        self._dictionary = False
        self.documents = []
        self.dictionary_tokenizer_match = False

    def __len__(self):
        return len(self._document_list)

    def __iter__(self):
        doc = self.extract_doctext(self.documents.next())
        if self.tokenizer:
            yield self.dictionary.doc2bow(self.tokenizer.tokenize(doc))
        else:
            yield self.dictionary.doc2bow(doc.rstrip().lower().split())

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

    @dictionary.deleter
    def dictionary(self):
        del self._dictionary

    @property
    def tokenizer(self):
        return self._tokenizer

    @tokenizer.setter
    def tokenizer(self, new_tokenizer):
        self._tokenizer = new_tokenizer
        self.dictionary_tokenizer_match = False

    @tokenizer.deleter
    def tokenizer(self):
        del self._tokenizer

    def glob_documents(self, path_glob_pattern):
        self.documents = glob(path_glob_pattern)

    def rewind(self):
        self._document_iter = iter(self._document_list)


class LazyJSONCorpus(LazyCorpus):

    def __init__(self, tokenizer=None, path_to_text='text'):
        self.path_to_text = path_to_text
        super(LazyJSONCorpus, self).__init__(tokenizer)

    def extract_doctext(self, file_loc):
        with open(file_loc, 'r') as file_in:
            data = json.load(file_in)
            text = reduce(dict.get, self.path_to_text.split("."), data)
            return text or ""
