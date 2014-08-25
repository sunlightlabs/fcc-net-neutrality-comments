import sys
import os
import csv
from glob import iglob


sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             os.path.pardir))

# In[2]:


import logging
logging.basicConfig(filename='log/lsi_matrix.log',
                    format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)


logger = logging.getLogger('debug_log')


# In[5]:

import settings


from gensim import corpora, matutils
from gensim.corpora import dictionary
from gensim.models import ldamodel, lsimodel



import numpy as np
#import pandas as pd

logger.info('deserializing tfidf_corpus_lsi')
tfidf_corpus_lsi = corpora.MmCorpus(os.path.join(settings.PERSIST_DIR, 'tfidf_corpus_lsi-200'))

logger.info('loading lsi model')
lsi_model = lsimodel.LsiModel.load(os.path.join(settings.PERSIST_DIR, 'lsi_model-200'))


logger.info('globbing filenames')
fnames = iglob(os.path.join(settings.PROC_DIR, '*.json'))


from gensim.similarities.docsim import MatrixSimilarity, SparseMatrixSimilarity, Similarity

logger.info('building matrix similarity')
sim_matrix = MatrixSimilarity(tfidf_corpus_lsi, num_features=tfidf_corpus_lsi.num_terms)

logger.info('persisting matrix similarity index')
sim_matrix.save(os.path.join(settings.PERSIST_DIR, 'tfidf_corpus_lsi_matrix_similarity'))

logger.info('survey of neighbor groupings')
with open(os.path.join(settings.STATS_DIR, 'num_neighbors.csv', 'w')) as fout:
    csv_writer = csv.writer(fout)

    for i, doc in fnames:
        try:
            result = sim_matrix[matutils.unitvec(tfidf_corpus_lsi.docbyoffset(tfidf_corpus_lsi.sim_matrix[i]))]
            n_similar = np.argwhere(result > 0.5).flatten().size
            csv_writer.writerow((doc, n_similar))
        except Exception as e:
            logger.error(e)
            continue

## MiniBatch K-means

# In[156]:

from sklearn.cluster import MiniBatchKMeans
from sklearn import metrics

logger.info('setting up kmeans')
mbk = MiniBatchKMeans(init='k-means++', n_clusters=8, n_init=1,
                      init_size=1000, batch_size=1000)

logger.info('fitting kmeans to index')
mbk.fit(sim_matrix.index)

# In[ ]:
logger.info('persisting_kmeans_model')
import pickle
pickle.dump(mbk, open(os.path.join(settings.PERSIST_DIR, 'cluster_labels_0-8'),'w'))

logger.info('persisting cluster_labels')
np.save(os.path.join(settings.PERSIST_DIR, 'cluster_labels_0-8'), mbk.labels_)

# In[ ]:

logger.info('persisting cluster_centers')
np.save(os.path.join(settings.PERSIST_DIR, 'cluster_centers_0-8'), mbk.cluster_centers_)


metrics.silhouette_score(sim_matrix.index, mbk.labels_, sample_size=100000)

logger.info('done.')
