from collections import defaultdict

class InvertedIndex(object):
    def __init__(self, lazy_corpus, dictionary):
        self.word_dictionary = dictionary
        self.invert_corpus(lazy_corpus)

    def invert_corpus(self, lazy_corpus):
        self.token2docs = defaultdict(list)
        for docid, doc in enumerate(lazy_corpus):
            for token, count in doc:
                self.token2docs[token].append((docid,count))
