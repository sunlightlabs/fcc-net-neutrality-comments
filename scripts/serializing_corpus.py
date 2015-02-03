
# coding: utf-8

# In[2]:

import sys
import os
import pdb

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))


# In[3]:

import logging
logging.basicConfig(filename='log/serialize_corpus.log', format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


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

if len(sys.argv) > 1:
    fname_suffix = sys.argv[1]
else:
    fname_suffix = ''

# In[7]:

my_dict = dictionary.Dictionary.load('persistence/my_dict')


# In[8]:

punct_tags = list(',.:)"') + ['CD', 'IN']


# In[9]:

pt_tokenizer = tokenizer.PretaggedTokenizer(stopword_list=None, filter_tags=punct_tags)


# In[11]:

lj_corpus = corpus.LazyJSONCorpus(tokenizer=pt_tokenizer, dictionary=my_dict, path_to_text='tagged')


large_doc_loc = os.path.join(settings.PERSIST_DIR, 'large_documents')
if os.path.exists(large_doc_loc):
    with open(large_doc_loc) as large_doc_file:
        large_documents = [line.strip() for line in large_doc_file]
else:
    large_documents = []

# In[12]:

document_index_fname = 'document_index' + fname_suffix

#lj_corpus.glob_documents(glob_pattern)
document_loc_template = os.path.join(settings.PROC_DIR, '{}.json')

if large_documents:
    lj_corpus.documents = [document_loc_template.format(line.strip()) for line in open(os.path.join(settings.PERSIST_DIR, document_index_fname)) if line.strip() not in large_documents]
else:
    lj_corpus.documents = [document_loc_template.format(line.strip()) for line in open(os.path.join(settings.PERSIST_DIR, document_index_fname))]

# In[16]:

corpus_fname = 'corpus' + fname_suffix + '.mm'
corpora.MmCorpus.serialize(os.path.join(settings.PERSIST_DIR, corpus_fname), lj_corpus, my_dict)



