
# coding: utf-8

# In[30]:

import sys
import os
import json
import csv

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))


# In[94]:

from time import time

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


# In[24]:

import settings


# In[39]:

from models.tokenizer import PretaggedTokenizer


# In[40]:

punct_tags = list(',.:)"') + ['CD', 'IN']
pt_tokenizer = PretaggedTokenizer(stopword_list=None, filter_tags=punct_tags)


# In[87]:

from gensim import corpora, matutils
from gensim.corpora import dictionary


# In[64]:

corpus = corpora.MmCorpus('../persistence/corpus.mm')


# In[68]:

dct = dictionary.Dictionary.load('../persistence/my_dict')


# In[73]:

dct.token2id


# In[17]:

get_ipython().magic(u'pinfo corpus.index')


# In[70]:

corpus.index[0]


# In[71]:

dct[0]


# In[72]:

[(dct[d[0]], d[1]) for d in corpus.docbyoffset(97)]


# In[74]:

def retokenize_doc(doc, dic):
    return [(dic[d[0]], d[1]) for d in doc]


# Realizing that document IDs are going to be tough. Forgot to output the order of reading them in.  Let's see if glob is deterministic.

# In[75]:

from glob import glob


# In[76]:

fnames = glob(os.path.join(settings.PROC_DIR, '*.json'))


# In[77]:

len(fnames)


# In[78]:

corpus.num_docs


# In[79]:

fnames[0]


# In[80]:

json.load(open(fnames[0]))


# looks good for doc 1 anyway

# In[81]:

doc = corpus.docbyoffset(corpus.index[300000])
tokenized_doc = retokenize_doc(doc, dct)
tokenized_doc


# In[82]:

jd = json.load(open(fnames[300000]))
test_doc = dct.doc2bow(pt_tokenizer.tokenize(jd['tagged']))
tokenized_test = retokenize_doc(test_doc, dct)
tokenized_test


# In[83]:

tokenized_test == tokenized_doc


# WHEW

# In[84]:

for docid, doc in enumerate(fnames[0:10]):
    print docid, os.path.basename(doc)


# In[59]:

#writer = csv.writer(open('../persistence/document_index.csv', 'w'))
#writer.writerow(['document_id', 'document_filename'])
#writer.writerows(((docid, os.path.basename(doc)) for docid, doc in enumerate(fnames)))


# In[63]:

get_ipython().system(u'head ../persistence/document_index.csv')


# In[85]:

corpus_lda = corpora.MmCorpus('../persistence/corpus_lda.mm')


# In[90]:

corpus_lda_matrix = matutils.corpus2dense(corpus_lda, corpus_lda.num_terms,
                                          num_docs=corpus_lda.num_docs)


# In[91]:

corpus_lda_matrix


# # LSA: Mini-Batch KMeans

# In[92]:

from sklearn.cluster import MiniBatchKMeans


# In[93]:

mbk = MiniBatchKMeans(init='k-means++', n_clusters=10, n_init=1,
                      init_size=1000, batch_size=1000, verbose=True)


# In[ ]:

t0 = time()
mbk.fit(corpus_lda_matrix)
print("done in %0.3fs" % (time() - t0))


# In[ ]:



