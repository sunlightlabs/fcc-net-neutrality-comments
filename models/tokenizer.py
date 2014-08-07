from nltk import word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords


class BaseTokenizer(object):

    def __init__(self, stopword_list=None):
        self.stemmer = PorterStemmer()
        if stopword_list:
            self.stopwords = stopword_list
        else:
            self.stopwords = stopwords.words('english')

    def tokenize(self, text):
        raise NotImplementedError


class DefaultTokenizer(BaseTokenizer):

    def tokenize(self, text):
        tokens = []
        try:
            words = word_tokenize(text)
        except:
            return tokens
        else:
            tokens = [self.stemmer.stem(word.lower())
                      for word in words
                      if word not in self.stopwords and word.isalnum()]
            return tokens
