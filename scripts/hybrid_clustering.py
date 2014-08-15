
# coding: utf-8
# In[86]:

import sys
import os
import json
import csv

from glob import glob

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))


# In[23]:

from time import time

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)

logger = logging.getLogger('debug_log')


# In[7]:

import settings


# In[76]:

from gensim import corpora, matutils
from gensim.corpora import dictionary
from gensim.models import ldamodel, lsimodel
from gensim.similarities import MatrixSimilarity


# In[104]:

from sklearn.cluster import MiniBatchKMeans


# In[9]:

import numpy as np                                                                                           
import pandas as pd 


# In[83]:

cluster_labels = np.load(os.path.join(settings.PERSIST_DIR,'cluster_labels_0-10.npy'))


# In[84]:

cluster_labels = pd.Series(cluster_labels)


# In[87]:

fnames = glob(os.path.join(settings.PROC_DIR,'*.json'))
doc_ids = pd.Series(map(lambda x: os.path.basename(x).split('.')[0], fnames), dtype=object)



unclustered_gensim_id = pd.Series(xrange(800954))


# In[90]:

bookie = pd.DataFrame({'original_id': unclustered_gensim_id,
                       'doc_id': doc_ids, 'cluster_r0': cluster_labels})


doc_topic = MatrixSimilarity.load(os.path.join(settings.PERSIST_DIR, 'tfidf_corpus_lsi-200_matrix_similarity')).index

bookie['cluster_r1'] = pd.Series((-1 for i in xrange(bookie.cluster_r0.shape[0])))
bookie['cluster_r2'] = pd.Series((-1 for i in xrange(bookie.cluster_r0.shape[0])))


# In[131]:

for cluster_num, group in bookie.groupby('cluster_r0'):
    if len(group) < 10000:
        continue
    mbk = MiniBatchKMeans(init='k-means++', n_clusters=5, n_init=1,
                          init_size=1000, batch_size=1000)
    mbk.fit(doc_topic[group['original_id']])
    bookie.loc[bookie.cluster_r0 == cluster_num,'cluster_r1'] = mbk.labels_
    np.save(os.path.join(settings.PERSIST_DIR, 'cluster_labels_1_%d-5'%cluster_num),
            mbk.labels_)
    np.save(os.path.join(settings.PERSIST_DIR, 'cluster_centers_1_%d-5'%cluster_num),
            mbk.cluster_centers_)


for cluster_num, group in bookie.groupby('cluster_r1'):
    if len(group) < 10000:
        continue
    mbk = MiniBatchKMeans(init='k-means++', n_clusters=3, n_init=1,
                          init_size=1000, batch_size=1000)
    mbk.fit(doc_topic[group['original_id']])
    bookie.loc[bookie.cluster_r1 == cluster_num,'cluster_r2'] = mbk.labels_
    np.save(os.path.join(settings.PERSIST_DIR, 'cluster_labels_2_%d-5'%cluster_num),
            mbk.labels_)
    np.save(os.path.join(settings.PERSIST_DIR, 'cluster_centers_2_%d-5'%cluster_num),
            mbk.cluster_centers_)

