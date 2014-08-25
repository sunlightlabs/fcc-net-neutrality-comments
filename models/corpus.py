import json
from glob import glob

from .tokenizer import DefaultTokenizer
from .util import clean_text


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
            if text:
                cleaned_text = clean_text(text)
                return cleaned_text or ""
            else:
                return ""
