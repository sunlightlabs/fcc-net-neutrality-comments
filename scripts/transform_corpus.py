
# coding: utf-8

# In[1]:

import sys
import os

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.path.pardir))


# In[2]:

import logging
logging.basicConfig(filename='transform_corpus.log', format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


# In[3]:

import settings
#reload(settings)


# In[7]:

from gensim import corpora
from gensim.corpora import dictionary
from gensim import models


# In[6]:

my_dict = dictionary.Dictionary.load(os.path.join(settings.PERSIST_DIR, 'my_dict'))
corpus = corpora.MmCorpus(os.path.join(settings.PERSIST_DIR, 'corpus.mm'))


# In[8]:

tfidf = models.TfidfModel(corpus)


# In[10]:

tfidf_corpus = tfidf[corpus]

tfidf.save(os.path.join(settings.PERSIST_DIR, 'tfidf_model'))

# In[11]:

corpora.MmCorpus.serialize(os.path.join(settings.PERSIST_DIR, 'tfidf_corpus.mm'),
                           tfidf_corpus)


