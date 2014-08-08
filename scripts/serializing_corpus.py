
# coding: utf-8

# In[2]:

import sys
import os
import pdb

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))


# In[3]:

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


# In[4]:

import settings
#reload(settings)


# In[5]:

from models import tokenizer
from models import corpus
#reload(tokenizer)
#reload(corpus)


# In[6]:

from gensim import corpora
from gensim.corpora import dictionary


# In[7]:

my_dict = dictionary.Dictionary.load('persistence/my_dict')


# In[8]:

punct_tags = list(',.:)"') + ['CD', 'IN']


# In[9]:

pt_tokenizer = tokenizer.PretaggedTokenizer(stopword_list=None, filter_tags=punct_tags)


# In[11]:

lj_corpus = corpus.LazyJSONCorpus(tokenizer=pt_tokenizer, dictionary=my_dict, path_to_text='tagged')


# In[12]:

glob_pattern = os.path.join(settings.PROC_DIR, '*.json')

lj_corpus.glob_documents(glob_pattern)


# In[16]:
corpora.MmCorpus.serialize('persistence/corpus.mm', lj_corpus, my_dict)



