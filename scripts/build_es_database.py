import os
import json
import sys

from collections import defaultdict

from elasticsearch import Elasticsearch
from elasticsearch import helpers

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             os.path.pardir))

import settings

import logging
logging.basicConfig(filename='log/build_es_database.log',
                    format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)


logger = logging.getLogger('debug_log')

es = Elasticsearch(['localhost:9200', ])

mapping = json.load(open(os.path.join(settings.STATS_DIR,
                                      'es_mapping_part_two.json')))


tree_data = json.load(open(os.path.join(settings.PROJ_ROOT,
                                        'cluster_viz',
                                        'tree_data',
                                        'MASTER.json'), 'r'))

cluster_data = defaultdict(list)

for node_label, doc_ids in tree_data.iteritems():
    for doc_id in doc_ids:
        cluster_data[doc_id].append(node_label)

json.dump(cluster_data, open(os.path.join(settings.PROJ_ROOT,
                                          'cluster_viz',
                                          'tree_data',
                                          'MASTER_INVERSE.json'), 'w'))

del tree_data


def get_json_doc(doc_id):
    with open(os.path.join(settings.PROC_DIR,
                           '{}.json'.format(doc_id))) as fin:
        jd = json.load(fin)
    return jd


def build_es_action(doc_id, action_template):
    d = get_json_doc(doc_id)
    d['clusters'] = cluster_data.get(doc_id, [])
    source = action_template.copy()
    source['_id'] = doc_id
    source['_source'] = d
    return source


def create_index(index_name):
    es.indices.create(index=index_name,
                      body=mapping)


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
                                          doc_id, action_template)
                                          for doc_id in doc_ids))

    for success, source in bulk_insert:
        if not success:
            logger.warning("{d} not indexed\n{s}".format(
                d=source.get('_id', '???'), s=json.dumps(source, indent=2)))

if __name__ == "__main__":
    index_name, document_id_list = sys.argv[1:]
    if es.indices.exists(index_name):
        raise Exception("index already exists")
    create_index(index_name)
    main(index_name, document_id_list)
