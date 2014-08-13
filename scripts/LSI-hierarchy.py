
# coding: utf-8

## Imports

# In[1]:

import sys
import os
import json
import csv

# In[2]:

from time import time

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


# In[12]:

from glob import glob


# In[13]:

import numpy as np

#lsi_u = np.load('persistence/lsi_model.projection.u.npy')
tfidf_corpus_lsi_matrix = np.load('persistence/tfidf_corpus_lsi_matrix.npy')


# In[38]:

from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import dendrogram
from fastcluster import centroid


document_linkage = centroid(tfidf_corpus_lsi_matrix.T[:,0:10])

np.save('persistence/document_linkage.npy', document_linkage)
