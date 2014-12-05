import os
import json
import sys

#import pandas as pd
#import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch import helpers

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             os.path.pardir))

import settings

import logging
logging.basicConfig(filename='log/lsi_matrix.log',
                    format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)


logger = logging.getLogger('debug_log')

es = Elasticsearch(['localhost:9200', ])

tree_data = json.load(open(os.path.join(settings.PROJ_ROOT,
                                        'cluster_viz',
                                        'tree_data',
                                        'MASTER.json')))


def get_json_doc(doc_id):
    with open(os.path.join(settings.PROC_DIR,
                           '{}.json'.format(doc_id))) as fin:
        jd = json.load(fin)
    return jd


def build_es_action(doc_id, action_template):
    d = get_json_doc(doc_id)
    d['clusters'] = []
    source = action_template.copy()
    source['_id'] = doc_id
    source['_source'] = d
    return source


def main(index_name, document_id_list):
    action_template = {'_index': index_name,
                       '_type': 'comment',
                       '_id': None,
                       '_source': None}

    doc_ids = (line.strip() for line in
               open(os.path.join(settings.PERSIST_DIR,
                                 document_id_list)))

    bulk_insert = helpers.streaming_bulk(es,
                                         (build_es_action(
                                          doc_id,action_template) 
                                          for doc_id in doc_ids))

    for success, source in bulk_insert:
        if not success:
            logger.warning("{d} not indexed\n{s}".format(
                d=source['_id'], s=json.dumps(source, indent=2)))

if __name__ == "__main__":
    index_name, document_id_list = sys.argv[1:]
    if es.indices.exists(index_name):
        raise Exception("index already exists")
    main(index_name, document_id_list)
