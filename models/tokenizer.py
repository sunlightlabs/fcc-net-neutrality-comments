import re
import sys

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
                      if word not in self.stopwords and word.isalpha()]
            return tokens


class PretaggedTokenizer(BaseTokenizer):

    def __init__(self, stopword_list=None, filter_tags=None):
        self.regexp = re.compile(r'(.+?)\|([A-Z\.\,:\)\(\$)\"#`\']+)\|(.+)')
        if filter_tags:
            self.filter_tags = filter_tags
        else:
            self.filter_tags = list()
        self.bad_juju = [u'/', u'<', u'\u2028']
        super(PretaggedTokenizer, self).__init__(stopword_list)

    def tokenize(self, tagged_text):
        tokens = []
        tagged_words = [tagged_word for tagged_word in
                        tagged_text.split(' ') if tagged_word]
        try:
            for tagged_word in tagged_words:
                try:
                    word, pos, lemma = self.regexp.findall(tagged_word)[0]
                    if lemma == '<unknown>':
                        lemma = word
                except (ValueError, IndexError):
                    sys.stderr.write('problem word: '+tagged_word+'\n')
                    raise
                else:
                    if (not word.isalpha()) or (word.lower() in self.stopwords) or (pos in self.filter_tags):
                        continue
                    else:
                        tokens.append(lemma)
        except Exception:
            sys.stderr.write('problem text: '+tagged_text+'\n')
            raise
        else:
            return tokens
