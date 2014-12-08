import os
import sys
import json
import csv
import itertools
from glob import glob
from collections import defaultdict
from random import sample

from gensim import corpora
from gensim import models
from gensim.similarities import MatrixSimilarity

import pandas as pd
import numpy as np

import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    filename='log/kanopy_cluster_tree.log', filemode='a',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))

import settings

NODE_DOC_MAP = {}

NODE_DOC_INDEX = {}

NUM_LABELS = 5

if len(sys.argv) > 1:
    fname_suffix = sys.argv[1]
else:
    fname_suffix = '_part_two'

lsi_model = models.LsiModel.load(os.path.join(settings.PERSIST_DIR,
                                              'lsi_model{}-200'.format(
                                                  fname_suffix)))

tfidf_corpus = corpora.MmCorpus(os.path.join(settings.PERSIST_DIR,
                                             'tfidf_corpus{}.mm'.format(
                                                  fname_suffix)))

corpus = corpora.MmCorpus(os.path.join(settings.PERSIST_DIR,
                                       'corpus{}.mm'.format(
                                           fname_suffix)))

mydct = corpora.Dictionary.load(os.path.join(settings.PERSIST_DIR,
                                             'my_dict'))

term_corpus_counts_floc = os.path.join(settings.PERSIST_DIR, 'term_corpus_counts{}.csv'.format(fname_suffix))

if not os.path.exists(term_corpus_counts_floc):
    term_corpus_counts = defaultdict(int)

    for doc in corpus:
        for term, count in doc:
            term_corpus_counts[term] += count

    term_corpus_counts = pd.DataFrame.from_dict(term_corpus_counts, orient='index')
    term_corpus_counts.index.name = 'token_id'
    term_corpus_counts.columns = ['freq']

    term_corpus_counts.to_csv(os.path.join(settings.PERSIST_DIR,
                                           'term_corpus_counts.csv'))
else:
    term_corpus_counts = pd.read_csv()
    term_corpus_counts.set_index('token_id')

id2token = {v: k for k, v in mydct.token2id.iteritems()}

id2token_df = pd.DataFrame.from_dict(id2token, orient='index')
id2token_df.index.name = 'token_id'
id2token_df.columns = ['token', ]

column_means = np.abs(lsi_model.projection.u).mean(axis=0)
topic_maxes = (np.abs(lsi_model.projection.u) - column_means).max(axis=1)

fnames = [fname.strip() for fname in 
          open(os.path.join(settings.PERSIST_DIR,
                            'document_index{}'.format(fname_suffix)))]

index_to_fname = dict(enumerate(fnames))
fname_to_index = dict(((n, i) for i, n in enumerate(fnames)))


def terms_for_docid(docid):
    ix = fname_to_index[docid]
    terms = corpus.docbyoffset(corpus.index[ix])
    return [(t, w) for t, w in terms]


def get_keywords(doc_list):
    doc_ids = list(doc_list)
    counts = defaultdict(lambda: {'count': 0, 'doc_count': 0})
    ndocs = float(len(doc_ids))
    for doc_id in doc_ids:
        for term, count in terms_for_docid(doc_id):
            counts[term]['count'] += count
            counts[term]['doc_count'] += 1
    records = ({'token_id': k,
                'node_freq': cd['count'],
                'doc_count': cd['doc_count']}
               for k, cd in counts.items())
    node_freqs = pd.DataFrame(records)
    node_freqs.set_index('token_id', inplace=True)
    node_freqs = node_freqs[node_freqs.doc_count > (len(doc_ids) * 0.05)]
    node_freqs = node_freqs.join(term_corpus_counts, how='left')
    node_freqs = node_freqs.join(id2token_df, how='left')
    node_freqs['ratio'] = node_freqs.node_freq / node_freqs.freq
    node_freqs['z_score'] = (node_freqs.ratio - node_freqs.ratio.mean()) / node_freqs.ratio.std()
    node_freqs['dc_cover'] = node_freqs.doc_count / node_freqs.node_freq
    node_freqs['dc_spread'] = node_freqs.doc_count / ndocs
    node_freqs['dc_weighted'] = ((node_freqs.dc_spread + node_freqs.dc_cover)/2) * node_freqs.z_score
    keyword_df = node_freqs.sort('dc_weighted', ascending=False)
    return list(keyword_df['token'])


def get_node_keywords(doc_lists):
    keyword_lists = []
    for doc_list in doc_lists:
        kl = get_keywords(doc_list)
        #logger.info('found keywords:\n{kl}'.format(kl=kl))
        keyword_lists.append(kl)
    keywords = itertools.chain.from_iterable(
        itertools.izip_longest(*keyword_lists))
    return list(set(list(keywords)[:NUM_LABELS]))


def cluster_name(r, lev):
    prev = r['level_'+str(lev-1)]
    this = r['cluster_r'+str(lev)]
    _prev_path = prev.split('_')[1]
    n = str(lev)+'_'
    if this >= 0:
        n += str(_prev_path) + '-' + str(this)
    else:
        n += str(_prev_path)
    return n


def add_level_names(b):
    b['level_0'] = b.apply(lambda x: '0_' + str(x['cluster_r0']), axis=1)
    for i in range(1, 11):
        b['level_'+str(i)] = b.apply(lambda x: cluster_name(x, i), axis=1)


def lookup_docs(doc_fname_series):
    return [os.path.basename(fn) for fn in doc_fname_series.tolist()]


def collect_nodes(b, levels):
    _seen = set([])
    for lvl in levels:
        # print lvl
        for node_name, group in b.groupby(lvl):
            # print '...'+node_name
            if node_name not in _seen:
                _seen.add(node_name)
                _doclist = lookup_docs(group['doc_id'])
                _doc_pivot = {'size': group.shape[0],
                              'id': node_name}
                NODE_DOC_MAP[node_name] = _doclist
                yield _doc_pivot


def reduce_key(k):
    level, path = k.split('_')
    parent_level = str(int(level) - 1)
    parent_path = '-'.join(path.split('-')[:-1])
    reduced = '_'.join([parent_level, parent_path])
    return reduced


def get_node_doclists(list_of_nodes):
    doc_lists = (NODE_DOC_MAP[n] for n in list_of_nodes)
    return list(doc_lists)


def combine_doclists(doc_lists):
    doc_ids = itertools.chain.from_iterable(itertools.izip_longest(*doc_lists))
    return [doc_id for doc_id in doc_ids if doc_id]


def add_level(lvl, parent_key, all_nodes):
    nodes = filter(lambda x: reduce_key(x['id']) == parent_key, all_nodes)
    next_lvl = lvl + 1
    for node in nodes:
        logger.info('beginning node: '+node['id'])
        node['children'] = add_level(next_lvl, node['id'], all_nodes)
        if len(node['children']) == 0:
            _doclists = get_node_doclists([node['id'], ])
        else:
            _doclists = get_node_doclists([c['id'] for c in node['children']])
        NODE_DOC_INDEX[node['id']] = combine_doclists(_doclists)
        logger.info('finding keywords for node: '+node['id'])
        node['keywords'] = get_node_keywords(_doclists)
        logger.info('finished node: '+node['id'])
    return nodes

def main():
    ids = ['doc_id', 'original_id']
    levels = ['level_'+str(i) for i in xrange(11)]
    rounds = ['cluster_r'+str(i) for i in xrange(11)]

    logger.info('reading cluster bookkeeping')
    bookie = pd.read_csv(open(os.path.join(settings.PERSIST_DIR,
                                           'cluster_bookeeping_kmeans.csv'),
                              'r'),
                         dtype={'doc_id':object})
    
    logger.info('making kanopy cluster table')
    add_level_names(bookie)

    logger.info('saving kanopy cluster table')
    bookie[ids + levels].to_csv(
        open(os.path.join(settings.PERSIST_DIR,
                          'kanopy_cluster_table.csv'), 'w'))
    # In[17]:

    logger.info('collecting nodes and writing to kmeans_clustered_docs')
    with open(os.path.join(settings.PERSIST_DIR,
                           'kmeans_clustered_docs.json'), 'w') as fout:
        all_nodes = [node for node in collect_nodes(bookie, levels)]
        json.dump(all_nodes, fout)
    
    # logger.info('collecting nodes from saved kmeans_clustered_docs')
    # with open(os.path.join(settings.PERSIST_DIR,
    #                        'kmeans_clustered_docs.json'), 'r') as fin:
    #     all_nodes = json.load(fin)

    logger.info('writing node names to kmeans_cluster_names')
    with open(os.path.join(settings.PERSIST_DIR,
                           'kmeans_cluster_names.json'), 'w') as fout:
        json.dump([node['id'] for node in all_nodes], fout)

    # logger.info('reading node names from kmeans_cluster_names')
    # with open(os.path.join(settings.PERSIST_DIR,
    #                        'kmeans_cluster_names.json'), 'r') as fin:
    #     cluster_names = json.load(fin)

    #root_nodes = ["0_0", "0_1", "0_2", "0_3"]
    root_nodes = ["0_0",
                  "1_1-1", "1_1-2", "1_1-3",
                  "2_1-0-0", "2_1-0-1", "2_1-0-2", "2_1-0-3"]

    tree = filter(lambda x: x['id'] in root_nodes, all_nodes)

    for root_node in tree:
        logger.info('beginning root: '+root_node['id'])
        root_node['children'] = add_level(1, root_node['id'], all_nodes)
        if len(root_node['children']) == 0:
            _doclists = get_node_doclists([root_node['id'], ])
        else:
            _doclists = get_node_doclists([c['id'] for c in root_node['children']])
        NODE_DOC_INDEX[root_node['id']] = combine_doclists(_doclists)
        logger.info('finding keywords for root: '+root_node['id'])
        root_node['keywords'] = get_node_keywords(_doclists)
        logger.info('finished root node: '+root_node['id'])

    logger.info('writing tree')
    json.dump(tree, open('cluster_viz/assets/tree.json', 'w'))

    logger.info('writing tree_data')
    json.dump(NODE_DOC_INDEX, open('cluster_viz/tree_data/MASTER.json', 'w'),
              indent=2)

if __name__ == "__main__":
    main()
