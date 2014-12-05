import os
import json
import sys

from elasticsearch import Elasticsearch
from elasticsearch import helpers

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             os.path.pardir))

import settings

import logging
logging.basicConfig(filename='log/update_es_cluster_membership.log',
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


def build_es_action(doc_id, node_id, action_template):
    source = action_template.copy()
    source['_id'] = doc_id
    source['body']['params']['new_clusters'] = [node_id, ]
    return source


def main(index_name):
    action_template = {'_index': index_name,
                       '_op_type': 'update',
                       '_type': 'comment',
                       '_id': None,
                       'body': {
                           'script': 'cluster_add',
                           'params': {
                               'new_clusters': [],
                           }}}

    for node_id, doc_ids in tree_data.iteritems():
        logger.info('starting on node {}'.format(node_id))
        bulk_actions = (build_es_action(doc_id, node_id, action_template)
                        for doc_id in doc_ids)
        bulk_update = helpers.streaming_bulk(es, bulk_actions)

        for success, source in bulk_update:
            if not success:
                logger.warning("{d} not indexed\n{s}".format(
                    d=source['_id'], s=json.dumps(source, indent=2)))

        logger.info('...finished node {}'.format(node_id))


if __name__ == "__main__":
    index_name = sys.argv[1]
    if not es.indices.exists(index_name):
        raise Exception("no index by that name")
    main(index_name)
