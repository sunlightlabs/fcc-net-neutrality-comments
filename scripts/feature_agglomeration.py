import sys
import os
import json
import csv

from glob import glob

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    filename='log/feature_agglomeration.log', filemode='a',
                    level=logging.INFO)

logger = logging.getLogger(__file__)

import settings

from gensim import corpora
from gensim.models import lsimodel
from gensim.similarities.docsim import MatrixSimilarity

from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import pairwise_distances
from scipy.cluster.hierarchy import fcluster
from fastcluster import linkage

import numpy as np
import pandas as pd


def print_orig_doc(ix):
    json_doc = json.load(open(fnames[ix]))
    print json_doc['text']


def parse_term(t):
    t = t.split('*')
    t[0] = float(t[0])
    t[1] = t[1].replace('"', '')
    return tuple(t)


def parse_topic(topic):
    return [parse_term(t) for t in topic.split(' + ')]


def show_n_docs(n, corpus):
    counter = 0
    for doc in corpus:
        if counter > n:
            break
        else:
            print doc
            counter += 1


def nclusters_for_d(wcl):
    return len(np.bincount(wcl))


def silhouette_for_d(wcl):
    return silhouette_score(top_topic_words_u, wcl, metric="cosine")


def get_stats(arange):
    for dist in arange:
        wcl = fcluster(word_linkage, dist, 'distance')
        yield (dist, nclusters_for_d(wcl), silhouette_for_d(wcl))


def write_topics(g):
    return ' '.join(g['token'].tolist())


logger.info("listing all paths to documents")
fnames = glob(os.path.join(settings.PROC_DIR, '*.json'))

logger.info("loading tf_idf corpus")
tfidf_corpus_lsi = corpora.MmCorpus('persistence/tfidf_corpus_lsi-200')
logger.info("loading LSI model")
lsi_model = lsimodel.LsiModel.load('persistence/lsi_model-200')
logger.info("loading dictionary")
dct = corpora.dictionary.Dictionary.load('persistence/my_dict')

logger.info("getting the top 75 words for each topic")
topics = [parse_topic(t) for t in lsi_model.show_topics(num_words=75)]

logger.info("unionizing top 75 words per topic")
top_topic_words = set()
for topic in topics:
    for w, t in topic:
        top_topic_words.add(t)

logger.info("in total, there were %d topic words"%len(top_topic_words))


logger.info("building word-topic matrix")
lsi_u = np.matrix(lsi_model.projection.u)
lsi_u_df = pd.DataFrame(lsi_u)
lsi_u_df.columns = ["topic_"+str(a) for a in lsi_u_df.columns]


dct_df = pd.DataFrame(dct.iteritems())
dct_df.columns = ['token_id', 'token']
dct_df.set_index('token_id', inplace=True)
dct_df.to_csv('persistence/my_dict_lookup.csv', encoding='utf8')

dct_with_u = dct_df.join(lsi_u_df, how='inner')

top_topic_words_u_df = dct_with_u[dct_with_u.token.isin(top_topic_words)]
top_topic_words_u_df.to_csv('persistence/lsi_topic-agglom_top-words-u-df.csv')

top_topic_words_u = top_topic_words_u_df.ix[:, 'topic_0':'topic_199'].as_matrix()

logger.info("pairwise distances for words")
wt_cos_dist = pairwise_distances(top_topic_words_u, metric='cosine', n_jobs=-2)
np.save('persistence/lsi_topic-agglom_distances', wt_cos_dist)

logger.info("word linkage matrix")
word_linkage = linkage(wt_cos_dist, method='ward')
np.save('persistence/lsi_topic-agglom_linkage', word_linkage)

# TODO: formalize this - http://stackoverflow.com/questions/2018178/finding-the-best-trade-off-point-on-a-curve
#wt_tradeoff_df = pd.DataFrame(get_stats(np.arange(1, 12, 0.25) ))
#wt_tradeoff_df.set_index(0)[1].plot()
#wt_tradeoff_df.set_index(0)[2].plot()

logger.info("assigning clusters to topic words")
word_cluster_labels = fcluster(word_linkage, 2.75, 'distance')
top_topic_words_u_df['cluster_number'] = word_cluster_labels
top_topic_words_u_df.to_csv('persistence/lsi_topic-agglom_clustered.csv')

cluster_lookup = {grp_num: write_topics(group) for grp_num, group in
                  top_topic_words_u_df.groupby('cluster_number')}

logger.info("getting centroids of each cluster")
centroid_index = []
group_centroids = []

for cluster_no, group in top_topic_words_u_df.groupby('cluster_number'):
    gsum = group.ix[:, 'topic_0':'topic_199'].as_matrix().sum(axis=0)
    gsize = len(group)
    c = gsum / gsize
    centroid_index.append(cluster_no)
    group_centroids.append(c)

group_centroids = np.array(group_centroids)
centroid_df = pd.DataFrame(group_centroids, index=centroid_index)
centroid_df.to_csv('persistence/lsi_topic-agglom_centroids.csv')
cluster_centroid_matrix = centroid_df.as_matrix()

logger.info('bulding similarity matrix')
word_mat_sim = MatrixSimilarity(cluster_centroid_matrix, num_features=200)

tfidf_corpus_lsi = np.load('persistence/tfidf_corpus_lsi-200_matrix_similarity.index.npy')
word_mat_sim.num_best = 1
word_mat_sim.save('persistence/lsi_word-agglom_word-similarity-matrix')
with open('persistence/tfidf-lsi_sim_word-topic-hier.csv','w') as fout:
    with open('stats/tfidf-lsi_sim_problems.txt', 'w') as errout:
        csvw = csv.writer(fout)
        for doc_id, sim in enumerate(word_mat_sim[tfidf_corpus_lsi]):
            try:
                csvw.writerow((doc_id, sim[0][0], sim[0][1]))
            except Exception as e:
                errout.write(str(fnames[doc_id])+'\n')
                logger.error(e)
                continue
